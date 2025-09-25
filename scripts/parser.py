import os
import json
import logging
import re
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

INPUT_DIR = Path("scripts/seed_data")
OUTPUT_DIR = Path("scripts/seed_data_cleaned") 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY không được tìm thấy. Hãy chắc chắn bạn đã đặt nó trong file .env")

genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel('gemini-1.5-flash-latest')



def get_master_prompt(html_content: str) -> str:
    """
    Tạo ra prompt hoàn chỉnh để gửi đến LLM.
    PHIÊN BẢN "BULLETPROOF": Cực kỳ rõ ràng về logic trích xuất OPTIONS.
    """
    return f"""
You are a world-class data extraction AI for an IELTS learning application. Your single task is to meticulously analyze the provided HTML and convert it into a single, valid JSON object with no extra text or explanations.

The JSON object MUST strictly follow this exact structure. Pay close attention to the nesting:
{{
    "question_type": {{
        "name": "The full name of the question type",
        "description": "The introductory paragraph(s) describing the question type.",
        "strategy": "The HTML content of the tips and strategies."
    }},
    "recommended_links": [
        {{ "text": "The anchor text of a recommended link", "url": "The href value" }}
    ],
    "practice_sets": [
        {{
            "passage_title": "The title of this specific reading passage.",
            "passage_content": "The HTML content of this specific reading passage.",
            "options": {{
                // SHARED OPTIONS FOR THIS SET go here.
                // Applies to types like: Matching Headings, Categorisation, Summary Completion.
                // e.g., {{ "I": "Heading I", "II": "Heading II" }}.
                // If no shared options, leave as an empty object: {{}}.
            }},
            "questions": [
                {{
                    "question_text": "The full HTML text of the question.",
                    "correct_answer": "The correct answer for this question.",
                    "explanation": "The detailed explanation for this answer. If none, return an empty string.",
                    "options": {{
                        // INDIVIDUAL OPTIONS FOR THIS QUESTION go here.
                        // Applies to types like: Multiple Choice.
                        // e.g., {{ "A": "Option A for Q1", "B": "Option B for Q1" }}.
                        // If no individual options, leave as an empty object: {{}}.
                    }}
                }}
            ]
        }}
    ]
}}

--- OPTIONS EXTRACTION LOGIC (VERY IMPORTANT) ---
For each `practice_set` you identify, you MUST follow this logic to extract the options correctly:
1.  **SHARED OPTIONS**: Look for a list of options (often in a `<ul>` or `<blockquote>`) that appears *before* the numbered questions (e.g., before `Questions 1-5`). These are shared options.
    -   If you find them, extract them into the main `options` object for that `practice_set`.
    -   This applies to question types like 'Matching Headings', 'Categorisation', and 'Summary Completion'.
2.  **INDIVIDUAL OPTIONS**: Look for a list of options that appears *inside* or *immediately after* the text of a specific question (e.g., after "1. Where is rice grown?"). These are individual options.
    -   If you find them, extract them into the `options` object *inside that specific question*.
    -   This primarily applies to the 'Multiple Choice' question type.
3.  **NEVER LEAVE `options` OUT**: If a practice set or a question has no options to extract, you MUST still include the `options` key with an empty object as its value: `{{}}`.

--- SPECIAL INSTRUCTIONS FOR "SUMMARY COMPLETION" ---
If the question type is "Summary Completion":
1.  The `question_text` is the entire summary paragraph.
2.  Create a SEPARATE question object in the `questions` array FOR EACH BLANK.
3.  The `question_text` will be THE SAME for each of these objects.
4.  The `correct_answer` will be the answer for that specific blank.
5.  The shared `options` object at the `practice_set` level should contain the list of words to choose from.

--- FINAL RULES ---
- Your entire response MUST be ONLY the JSON object. No markdown, no explanations.
- CRITICAL: Identify every independent practice set in the HTML and create a separate object for it in the `practice_sets` array.
- CRITICAL: Extract recommended links from the "RECOMMENDED FOR YOU" section.
- If a section is not present (e.g., no strategy), return an empty string "" or an empty array [] accordingly.

Here is the HTML content to analyze:
---
{html_content}
---
"""

def create_output_directory():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.info(f"Thư mục đầu ra '{OUTPUT_DIR}' đã sẵn sàng.")

def clean_llm_response(response_text: str) -> str:
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        return match.group(0)
    return response_text 

def parse_html_file_with_llm(filepath: Path):
    logging.info(f"Đang xử lý file: {filepath.name}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        prompt = get_master_prompt(html_content)

        logging.info(f"Gửi yêu cầu đến Gemini cho file {filepath.name}...")
        response = MODEL.generate_content(prompt)
        
        cleaned_json_str = clean_llm_response(response.text)
        
        json_data = json.loads(cleaned_json_str)

        output_filename = filepath.stem + ".json"
        output_filepath = OUTPUT_DIR / output_filename
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        
        logging.info(f"Lưu thành công dữ liệu đã trích xuất vào: {output_filepath}")

    except json.JSONDecodeError:
        logging.error(f"LỖI: Gemini đã trả về một chuỗi JSON không hợp lệ cho file {filepath.name}.")
        with open(OUTPUT_DIR / (filepath.stem + "_error.txt"), 'w', encoding='utf-8') as f:
            f.write(response.text)
    except Exception as e:
        logging.error(f"Đã xảy ra lỗi không xác định khi xử lý file {filepath.name}: {e}")


def main():
    create_output_directory()
    logging.info("--- BẮT ĐẦU QUÁ TRÌNH PARSE BẰNG LLM ---")

    if not INPUT_DIR.exists():
        logging.error(f"Thư mục đầu vào '{INPUT_DIR}' không tồn tại.")
        return

    for html_file in INPUT_DIR.glob("*.html"):
        parse_html_file_with_llm(html_file)

    logging.info("--- HOÀN THÀNH QUÁ TRÌNH PARSE BẰNG LLM ---")


if __name__ == "__main__":
    main()