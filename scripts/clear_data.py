import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models.practice_question import PracticeQuestion
from app.models.reading_passage import ReadingPassage
from app.models.question_type import QuestionType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_all_data():
    db = SessionLocal()
    try:
        logging.info("Bắt đầu quá trình xóa dữ liệu...")
        
        num_questions = db.query(PracticeQuestion).delete()
        logging.info(f"Đã xóa {num_questions} bản ghi từ bảng practice_questions.")
        
        num_passages = db.query(ReadingPassage).delete()
        logging.info(f"Đã xóa {num_passages} bản ghi từ bảng reading_passages.")
        
        num_qtypes = db.query(QuestionType).delete()
        logging.info(f"Đã xóa {num_qtypes} bản ghi từ bảng question_types.")
        
        db.commit()
        logging.info("Xóa dữ liệu thành công!")
        
    except Exception as e:
        logging.error(f"Đã xảy ra lỗi: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_data()