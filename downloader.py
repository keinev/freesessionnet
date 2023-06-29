from sessionnet_scraper import SessionnetCrawler
from datetime import datetime, timedelta
import time


def get_all_files_and_meta(folder_path, targets_name, base_address, start_year):
    for year in range(start_year, int(datetime.today().strftime('%Y')) + 1):
        crawler = SessionnetCrawler(folder_path, targets_name, base_address, year, 1, 12)
        crawler.start_crawl()


def check_update_months(folder_path, targets_name, base_address, months_back):
    start_time = datetime.now()
    print(f'Started at {start_time.strftime("%H:%M:%S")}')
    start_date = datetime.now() - timedelta(days=30 * months_back)
    start_year = (int(start_date.strftime("%Y")))
    start_month = (int(start_date.strftime("%m")))
    crawler = SessionnetCrawler(folder_path, targets_name, base_address, start_year, start_month, months_back)
    crawler.start_crawl()
    print(f'it took {datetime.now() - start_time} to crawl {months_back} month')
    print(f'skipped: {crawler.skipped_total}, new: {crawler.new_total}')


def wait_until_next_execution(hour):
    current_time = datetime.now()
    next_execution_time = current_time.replace(hour=hour, minute=0, second=0)
    if current_time >= next_execution_time:
        next_execution_time += timedelta(days=1)
    wait_time = (next_execution_time - current_time).total_seconds()
    print("wait to Start:", wait_time)
    time.sleep(wait_time)


def main():
    folder_path = "RIS2_PDF/"
    targets_name = "Dessau"
    base_address = "https://sessionnet.dessau.de/bi/info.asp"
    look_back_in_month = 3
    scrape_hour = 4  # for 4AM

    while True:
        try:
            wait_until_next_execution(scrape_hour)
            check_update_months(folder_path, targets_name, base_address, look_back_in_month)
            print("Done. Going to sleep.")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
