# scripts/seed.py
import sys
import os
import json
from typing import List, Dict, Any

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models import question_type as qt_model
from sqlalchemy.orm import Session

# --- CONFIGURATION ---
INPUT_DIR = os.path.join(os.path.dirname(__file__), 'seed_data_cleaned')

def seed_all_data():
    """
    Reads all cleaned JSON files and seeds the entire database in the correct order.
    """
    db = SessionLocal()

    try:
        # --- Step 1: Check if database is already seeded ---
        if db.query(qt_model.QuestionType).count() > 0:
            print("Database already contains data. To re-seed, please run 'alembic downgrade base' and 'alembic upgrade head' first.")
            return

        # --- Step 2: Find all cleaned JSON files ---
        files_to_process = [f for f in os.listdir(INPUT_DIR) if f.endswith('_cleaned.json')]
        if not files_to_process:
            print(f"No cleaned JSON files found in {INPUT_DIR}. Did you run the parser?")
            return
            
        print(f"Found {len(files_to_process)} cleaned files. Starting the seeding process...")

        all_lessons_data = []
        for filename in files_to_process:
            filepath = os.path.join(INPUT_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                all_lessons_data.append(json.load(f))

        # --- Step 3: Seed all QuestionType objects first ---
        print("--> Seeding Question Types...")
        question_type_objects = []
        for lesson_data in all_lessons_data:
            qt_obj = qt_model.QuestionType(
                name=lesson_data['name'],
                slug=lesson_data['slug'],
                description=lesson_data['description'],
                strategy=lesson_data['strategy']
            )
            question_type_objects.append(qt_obj)
        
        db.add_all(question_type_objects)
        db.commit() # Commit to generate IDs
        print(f"    Successfully seeded {len(question_type_objects)} QuestionType records.")

        # --- Step 4: Seed all PracticeQuestion objects and link them ---
        print("--> Seeding Practice Questions...")
        practice_question_objects = []
        for lesson_data in all_lessons_data:
            if not lesson_data['practice_questions']:
                continue

            # We need to fetch the parent QuestionType we just created to get its ID
            parent_qt = db.query(qt_model.QuestionType).filter_by(slug=lesson_data['slug']).first()
            if not parent_qt:
                print(f"    Warning: Could not find parent QuestionType for slug '{lesson_data['slug']}'. Skipping its practice questions.")
                continue

            for pq_data in lesson_data['practice_questions']:
                # Convert options dict to JSON string if it's a dict
                options_json = json.dumps(pq_data.get('options')) if isinstance(pq_data.get('options'), dict) else None
                
                pq_obj = qt_model.PracticeQuestion(
                    passage=pq_data['passage'],
                    question_text=pq_data['question_text'],
                    correct_answer=pq_data['correct_answer'],
                    explanation=pq_data['explanation'],
                    # options=options_json, # Uncomment this if you add an 'options' column of type JSON to your PracticeQuestion model
                    question_type_id=parent_qt.id # This creates the link!
                )
                practice_question_objects.append(pq_obj)
        
        if practice_question_objects:
            db.add_all(practice_question_objects)
            db.commit()
            print(f"    Successfully seeded {len(practice_question_objects)} PracticeQuestion records.")
        else:
            print("    No practice questions found to seed.")
            
        print("\nSeeding process completed successfully!")

    except Exception as e:
        print(f"\nAn error occurred during seeding: {e}")
        db.rollback() # Rollback any changes if an error occurs
    finally:
        db.close()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("=== Running Comprehensive Database Seeder ===")
    seed_all_data()
    print("==========================================")