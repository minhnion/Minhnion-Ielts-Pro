import os
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CẤU HÌNH ---
BASE_DIR = os.path.dirname(__file__)
INPUT_DIR = os.path.join(BASE_DIR, 'seed_data')
OUTPUT_DIR = os.path.join(BASE_DIR, 'seed_data_cleaned')

def create_output_directory():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def clean_text(text):
    if not text: return ""
    return ' '.join(text.split()).strip()

def generate_slug(name):
    slug_base = name.replace("Ielts Reading", "").strip()
    return "ielts-reading-" + slug_base.lower().replace(' ', '-')

def find_question_anchors(tag):
    return tag.name in ['p', 'h4'] and re.search(r'Questions?[\s\d\-–]+', tag.get_text(), re.IGNORECASE)

def parse_html_file(filepath):
    logging.info(f"--- Bắt đầu phân tích file: {filepath.name} ---")
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    main_content = soup.find('div', class_='entry-content')
    if not main_content:
        logging.error(f"Không tìm thấy 'div.entry-content' trong file {filepath.name}. Bỏ qua.")
        return None

    question_type_name = "Ielts Reading " + ' '.join(word.capitalize() for word in filepath.stem.replace('ielts-', '').replace('reading-', '').replace('-', ' ').split())
    question_type_slug = generate_slug(question_type_name)

    question_anchors = main_content.find_all(find_question_anchors)
    logging.info(f"Tìm thấy {len(question_anchors)} khối câu hỏi dựa trên các 'mỏ neo'.")

    all_practice_questions = []

    for i, anchor in enumerate(question_anchors):
        logging.info(f"  -> Đang xử lý khối câu hỏi #{i+1} bắt đầu từ: '{clean_text(anchor.get_text())}'")
        
        passage_parts = []
        for sibling in anchor.find_previous_siblings():
            if (sibling in question_anchors) or (sibling.name in ['h2', 'h4'] and "Practice" in sibling.get_text()):
                break
            if sibling.find('strong') and len(sibling.find('strong').get_text()) > 15:
                passage_parts.append(clean_text(sibling.get_text()))
                break
            if sibling.name == 'p':
                passage_parts.append(clean_text(sibling.get_text()))
        passage_parts.reverse()
        passage = "\n".join(passage_parts).strip()
        if not passage:
            logging.warning(f"     Không tìm thấy passage cho khối #{i+1}. Bỏ qua.")
            continue
        logging.info(f"     Đã trích xuất passage ({len(passage)} ký tự).")

        questions_raw = []
        current_question = None
        current_element = anchor.find_next_sibling()
        
        while current_element and not (current_element.name == 'span' and 'collapseomatic' in current_element.get('class', [])):
            text = clean_text(current_element.get_text())
            # Xử lý thẻ <p> chứa câu hỏi
            if current_element.name == 'p' and re.match(r'^\d+\.?', text):
                if current_question: questions_raw.append(current_question)
                current_question = {"question_text": text, "options": []}
            # === SỬA LỖI 1: Xử lý <ol> và <ul> chứa câu hỏi ===
            elif current_element.name in ['ol', 'ul']:
                 for li in current_element.find_all('li', recursive=False):
                    li_text = clean_text(li.get_text())
                    if current_question: questions_raw.append(current_question) # Lưu câu hỏi trước đó
                    current_question = {"question_text": li_text, "options": []}
            elif current_question:
                options = [clean_text(opt) for opt in current_element.stripped_strings if opt.strip()]
                if options: current_question["options"].extend(options)
            current_element = current_element.find_next_sibling()
        if current_question: questions_raw.append(current_question)
        logging.info(f"     Tìm thấy {len(questions_raw)} câu hỏi thô.")

        answer_span = current_element
        if answer_span and answer_span.get('id'):
            span_id = answer_span.get('id')
            target_div_id = f"target-{span_id}"
            answer_container = soup.find('div', id=target_div_id)
            if answer_container:
                # === SỬA LỖI 2: Tìm danh sách bên trong div đáp án ===
                answer_list = answer_container.find(['ol', 'ul'])
                if answer_list:
                    answer_items = answer_list.find_all('li', recursive=False)
                    logging.info(f"     Tìm thấy khối đáp án và có {len(answer_items)} mục đáp án.")
                    for j, item in enumerate(answer_items):
                        if j < len(questions_raw):
                            correct_answer_text = item.find(string=True, recursive=False)
                            correct_answer = clean_text(correct_answer_text) if correct_answer_text else ""
                            full_question_text = questions_raw[j]['question_text'] + "\n" + "\n".join(questions_raw[j]['options'])
                            explanation_node = item.find(['ul', 'ol'])
                            explanation = clean_text(explanation_node.get_text()) if explanation_node else ' '.join(item.get_text(separator=' ', strip=True).split()[len(correct_answer.split()):])
                            all_practice_questions.append({
                                "passage": passage, "question_text": full_question_text,
                                "correct_answer": correct_answer, "explanation": explanation if explanation else None
                            })
                else: logging.warning("     Không tìm thấy thẻ <ol> hoặc <ul> bên trong div đáp án.")
            else: logging.warning(f"     Tìm thấy span nhưng không thấy div đáp án với id: {target_div_id}")
        elif questions_raw: logging.warning("     Không tìm thấy span 'collapseomatic' của đáp án.")

    final_data = {
        "name": question_type_name, "slug": question_type_slug,
        "description": "Extracted from ieltsliz.com", "strategy": "Extracted from ieltsliz.com",
        "practice_questions": all_practice_questions
    }
    return final_data

def main():
    create_output_directory()
    input_path = Path(INPUT_DIR)
    if not input_path.exists():
        logging.error(f"Thư mục đầu vào '{INPUT_DIR}' không tồn tại.")
        return

    logging.info("--- BẮT ĐẦU QUÁ TRÌNH PHÂN TÍCH TỔNG THỂ ---")
    for html_file in input_path.glob("*.html"):
        parsed_data = parse_html_file(html_file)
        if parsed_data and parsed_data['practice_questions']:
            # Bỏ qua các bài tập từ vựng không cần thiết
            real_questions = [q for q in parsed_data['practice_questions'] if 'vocabulary' not in q['question_text'].lower()]
            if real_questions:
                parsed_data['practice_questions'] = real_questions
                output_filename = html_file.stem + ".json"
                output_filepath = Path(OUTPUT_DIR) / output_filename
                with open(output_filepath, 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=4)
                logging.info(f"Lưu thành công {len(real_questions)} câu hỏi từ '{html_file.name}' vào '{output_filepath.name}'")
            else:
                logging.warning(f"Không có câu hỏi thực hành nào (sau khi lọc) được lưu từ file: {html_file.name}")
        else:
            logging.warning(f"Không có câu hỏi thực hành nào được lưu từ file: {html_file.name}")
    logging.info("--- HOÀN THÀNH QUÁ TRÌNH PHÂN TÍCH TỔNG THỂ ---")

if __name__ == "__main__":
    main()