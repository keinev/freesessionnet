from bs4 import BeautifulSoup
import requests
import re
import json
import os
from datetime import datetime

cjahr = "2020"
cmonat = "1"
# months ahead - more is possible but ofc slower
canz = "12"
time_pattern = r"\d{2}:\d{2}"
down_number_pattern = r'id=(\d+)'

json_filename = "base.json"
down_base_addr = "https://sessionnet.dessau.de/bi/"
download_path = "RIS2_PDF/"

all_known_numbers = []


def get_list_with_meta(start_year, month_ahead, c_month):
    address = "https://sessionnet.dessau.de/bi/si0046.asp?__cjahr=" + start_year + "&__canz=" + month_ahead + "&__cmonat=" + c_month
    response = requests.get(address)
    if response.status_code == 200:
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        full_list = []

        last_event_date = ""
        for table_record in soup.find_all('tr'):
            if table_record.find('th') is not None:  # ignore table head
                continue
            down_elements = []
            event_date = ""
            other_meta = []
            for record_data in table_record.find_all('td'):
                class_attr = record_data.get('class')
                if class_attr is not None:
                    if 'sidat_tag' in class_attr:
                        if record_data.a is not None:
                            event_date = record_data.a.span.next_sibling
                            last_event_date = event_date
                        else:
                            event_date = last_event_date
                    if 'silink' in class_attr:
                        if record_data.a is not None:
                            other_meta.append(record_data.a.text)
                            for list_elements in record_data.find_all('li'):
                                if re.search(time_pattern, list_elements.text):
                                    other_meta.append(list_elements.text[:5])
                                else:
                                    other_meta.append(list_elements.text)
                    if 'sidocs' in class_attr:
                        if record_data.a is not None:
                            a_ele = record_data.find_all('a')
                            for ele in a_ele:
                                if ele.get('href') not in down_elements:
                                    down_elements.append(ele.get('href'))
            if down_elements:
                if check_list_pattern([event_date, other_meta, down_elements]):
                    full_list.append([event_date, other_meta, down_elements])
        return full_list


def download_file(file_part, file_number, version):
    # download file and save in pattern filenumber_version-fullfilename
    full_address = down_base_addr + file_part
    response = requests.get(full_address)
    if response.status_code == 200:
        filename = response.headers.get('content-disposition')
        filename = str(file_number) + "_" + version + "-" + filename[filename.find('"') + 1:-1]
        open(download_path + filename, 'wb').write(response.content)
        return True
    return False


def check_list_pattern(list_entry):
    if len(list_entry) != 3:
        return False
    elif re.search(time_pattern, list_entry[0]):
        return False
    elif len(list_entry[1]) != 3:
        return False
    elif list_entry[2] == None:
        return False
    else:
        return True


def get_known_numbers():
    try:
        lst_folder_items = os.listdir(download_path)
        if len(lst_folder_items) != 0:
            for list_item in lst_folder_items:
                if list_item[-5:] != ".json":
                    all_known_numbers.append(list_item[:list_item.find("-")])
        return True
    except FileNotFoundError:
        print("Directory not found. Check Directory in download_path =")
        return False


def generate_json(list_to_json):
    files_in_data = []
    crawl_date = str(datetime.now())

    if list_to_json[2]:
        for down_file in list_to_json[2]:
            file_info = {}
            match_id = re.search(down_number_pattern, down_file)
            if match_id:
                file_info["id"] = match_id.group(1)
            file_info["link"] = down_file
            file_info["name"] = "placeholder"
            files_in_data.append(file_info)

    json_data = {
        "crawltime": crawl_date,
        "meeting": {
            "date": list_to_json[0],
            "responsible": list_to_json[1][0],
            "time": list_to_json[1][1],
            "location": list_to_json[1][2]
        },
        "files": files_in_data
    }
    json_output = json.dumps(json_data, indent=4)
    return json_output


def main():
    json_exist = False
    files_exist = False
    # IDEA
    # check if files in dir (but ignore base.json)
    if len(os.listdir(download_path)) != 0:

    # - if not start crawl since 2006
    # - if yes check last know date and crawl from last known date - 1 month
    # check if base.json exists
    # - check if number of files (-1) eq. number of files in json
    # -- if not iterate over all files and write missing to json

    # QUESTIONS
    # if we collect all docs by bruteforce (old method) do we get docs not listed?


    # OLD
    #if get_known_numbers():
    #    down_meta = get_list_with_meta(cjahr, canz, cmonat)
    #    for item in down_meta:
    #        for down_file in item[2]:
    #            only_number = re.search(down_number_pattern, down_file)
    #            only_number = only_number.group(1)
    #            if only_number in all_known_numbers:
    #                print("known:", only_number)


if __name__ == "__main__":
    main()
