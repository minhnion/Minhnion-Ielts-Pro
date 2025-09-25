import sys
import os
import json
import logging
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.question_type import QuestionType
from app.models.reading_passage import ReadingPassage
from app.models.practice_question import PracticeQuestion
from sqlalchemy.orm import Session

INPUT_DIR = Path("scripts/seed_data_cleaned")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def seed_data(db: Session):
    """
    Hàm chính để đọc các file JSON với cấu trúc mới (practice_sets) 
    và lưu dữ liệu vào cơ sở dữ liệu.
    """
    logging.info(f"Bắt đầu quét dữ liệu từ thư mục: {INPUT_DIR}")
    
    json_files = list(INPUT_DIR.glob("*.json"))
    if not json_files:
        logging.warning(f"Không tìm thấy file JSON nào trong {INPUT_DIR}. Dừng lại.")
        return

    logging.info(f"Tìm thấy {len(json_files)} file JSON để xử lý.")

    for json_file in json_files:
        logging.info(f"--- Đang xử lý file: {json_file.name} ---")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        try:
            # 1. XỬ LÝ QUESTION TYPE (CHUNG CHO CẢ FILE)
            qt_data = data['question_type']
            qt_slug = qt_data.get('slug') or qt_data['name'].lower().replace(' ', '-').replace('/', '-')
            
            question_type_obj = db.query(QuestionType).filter(QuestionType.slug == qt_slug).first()
            
            if not question_type_obj:
                logging.info(f"Tạo mới QuestionType: '{qt_data['name']}'")
                question_type_obj = QuestionType(
                    name=qt_data['name'],
                    slug=qt_slug,
                    description=qt_data.get('description', ''),
                    strategy=qt_data.get('strategy', '')
                )
                db.add(question_type_obj)
            else:
                logging.info(f"Sử dụng QuestionType đã tồn tại: '{qt_data['name']}'")
                # Cập nhật các trường nếu chúng đang trống
                if not question_type_obj.description and qt_data.get('description'):
                    question_type_obj.description = qt_data.get('description')
                if not question_type_obj.strategy and qt_data.get('strategy'):
                    question_type_obj.strategy = qt_data.get('strategy')

            if not data.get('practice_sets'):
                 logging.warning(f"File {json_file.name} không có 'practice_sets'. Bỏ qua.")
                 continue

            for practice_set in data['practice_sets']:
                # 2. XỬ LÝ READING PASSAGE (RIÊNG CHO TỪNG BỘ)
                passage_title = practice_set['passage_title']
                logging.info(f"Tạo ReadingPassage: '{passage_title}'")
                passage_obj = ReadingPassage(
                    title=passage_title,
                    content=practice_set['passage_content']
                )
                db.add(passage_obj)

                # 3. XỬ LÝ PRACTICE QUESTIONS (RIÊNG CHO TỪNG BỘ)
                questions_data = practice_set.get('questions', [])
                logging.info(f"Tạo {len(questions_data)} câu hỏi cho passage '{passage_title}'...")
                for q_data in questions_data:
                    # Logic xác định options: ưu tiên options trong câu hỏi, 
                    # nếu không có thì lấy options chung của practice_set
                    options_to_save = q_data.get('options') or practice_set.get('options') or {}
                    
                    new_question = PracticeQuestion(
                        question_text=q_data['question_text'],
                        correct_answer=q_data['correct_answer'],
                        explanation=q_data.get('explanation', ''),
                        options=options_to_save,
                        # Liên kết với passage và question type tương ứng
                        passage=passage_obj, 
                        question_type=question_type_obj
                    )
                    db.add(new_question)

            # 4. COMMIT GIAO DỊCH
            db.commit()
            logging.info(f"Lưu thành công dữ liệu từ file {json_file.name} vào DB.")

        except Exception as e:
            logging.error(f"LỖI khi xử lý file {json_file.name}: {e}. Đang rollback...")
            db.rollback()


if __name__ == "__main__":
    logging.info("--- BẮT ĐẦU SCRIPT SEED DATA (PHIÊN BẢN MỚI) ---")
    
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
        logging.info("--- KẾT THÚC SCRIPT SEED DATA ---")