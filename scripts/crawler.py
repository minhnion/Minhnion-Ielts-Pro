import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
from pathlib import Path

# Cấu hình logging để theo dõi tiến trình
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Danh sách các URL cần crawl
URLS_TO_CRAWL = [
    "https://ieltsliz.com/ielts-reading-multiple-choice/",
    "https://ieltsliz.com/ielts-reading-matching-headings/",
    "https://ieltsliz.com/ielts-yes-no-not-given-practice/",
    "https://ieltsliz.com/sentence-completion-questions-in-ielts-reading/",
    "https://ieltsliz.com/matching-paragraph-information-ielts-reading/",
    "https://ieltsliz.com/categorisation-practice-for-ielts-reading/",
    "https://ieltsliz.com/choosing-a-title-ielts-reading/",
    "https://ieltsliz.com/ielts-short-answer-questions-reading-practice/",
    "https://ieltsliz.com/food-ielts-summary-reading-practice/",
    "https://ieltsliz.com/matching-sentence-endings-ielts-reading-practice/",
]

OUTPUT_DIR = "scripts/seed_data"

# Giả lập header của một trình duyệt thông thường để tránh bị chặn
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
# -----------------

def create_output_directory():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    logging.info(f"Thư mục '{OUTPUT_DIR}' đã sẵn sàng.")

def get_clean_filename_from_url(url):
    path = urlparse(url).path
    filename = path.strip('/').split('/')[-1]
    return f"{filename}.html" if filename else "index.html"

def fetch_and_save_content(url):
    try:
        filename = get_clean_filename_from_url(url)
        filepath = Path(OUTPUT_DIR) / filename

        if filepath.exists():
            logging.info(f"Bỏ qua (đã tồn tại): {filename}")
            return

        logging.info(f"Đang xử lý URL: {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # thẻ <div class="entry-content"> chứa nội dung chính
        main_content = soup.find('div', class_='entry-content')

        if main_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Sử dụng prettify() để mã HTML dễ đọc hơn
                f.write(main_content.prettify())
            logging.info(f"Lưu thành công nội dung vào file: {filepath}")
        else:
            logging.warning(f"Không tìm thấy 'div.entry-content' tại URL: {url}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Lỗi khi yêu cầu URL {url}: {e}")
    except Exception as e:
        logging.error(f"Đã xảy ra lỗi không xác định với URL {url}: {e}")

def main():
    create_output_directory()
    logging.info("--- BẮT ĐẦU QUÁ TRÌNH CRAWL ---")
    
    for url in URLS_TO_CRAWL:
        fetch_and_save_content(url)
        
    logging.info("--- HOÀN THÀNH QUÁ TRÌNH CRAWL ---")

if __name__ == "__main__":
    main()