import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# ۱. تنظیمات مسیر و پروکسی
FILE_PATH = "/Users/kiananasiri/Downloads/TorBot/collected_data_v10/page3.html"
OUTPUT_DIR = "html_dataset_100"
TARGET_COUNT = 100
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ۲. خواندن فایل و استخراج لینک‌ها
def get_urls_from_file(path):
    print(f"Reading links from: {path}")
    urls = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            # استخراج تمام متن‌هایی که با http شروع شده و شامل .onion هستند
            # (چون فایل شما لینک‌ها را به صورت متن ساده یا داخل تگ <a> دارد)
            all_text = soup.get_text(separator=' ')
            words = all_text.split()
            for word in words:
                if ".onion" in word and word.startswith("http"):
                    # تمیز کردن کاراکترهای اضافه مثل <br> یا فضای خالی
                    clean_url = word.strip().replace('<br>', '').replace(',', '')
                    if clean_url not in urls:
                        urls.append(clean_url)
    except Exception as e:
        print(f"Error reading file: {e}")
    return urls

# ۳. تابع دانلود تکی
def download_site(url, index):
    try:
        print(f"[{index}] Fetching: {url}")
        r = requests.get(url, proxies=proxies, timeout=25, verify=False)
        if r.status_code == 200 and len(r.text) > 100:
            filename = f"site_{index}.html"
            with open(os.path.join(OUTPUT_DIR, filename), "w", encoding='utf-8') as f:
                f.write(r.text)
            return True
    except:
        pass
    return False

# ۴. اجرای اصلی
if __name__ == "__main__":
    all_urls = get_urls_from_file(FILE_PATH)
    print(f"Found {len(all_urls)} onion links in your file.")
    
    # محدود کردن به لینک‌های موجود یا ۱۰۰ عدد
    urls_to_crawl = all_urls[:200] # ۲۰۰ تا برمی‌داریم که حتماً ۱۰۰ تا موفق داشته باشیم
    
    success_count = 0
    # استفاده از ThreadPool برای سرعت (۱۰ دانلود همزمان)
    print("Starting Multi-threaded download...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        # ارسال لینک‌ها به تردها
        results = list(executor.map(lambda p: download_site(p[1], p[0]), enumerate(urls_to_crawl)))
        success_count = sum(1 for x in results if x)

    print(f"\n--- DONE ---")
    print(f"Total links processed: {len(urls_to_crawl)}")
    print(f"Successfully saved: {success_count} files in '{OUTPUT_DIR}'")
