from bs4 import BeautifulSoup
import requests
import re
import json
import os
from datetime import datetime
import hashlib

cjahr = "2020"
cmonat = "1"
# months ahead - more is possible but ofc slower
canz = "2"
time_pattern = r'\d{2}:\d{2}'
down_number_pattern = r'id=(\d+)'
meet_number_pattern = r'inr=(\d+)'
sub_doc_pattern = ""

down_base_addr = "https://sessionnet.dessau.de/bi/"
download_path = "RIS2_PDF/"

json_file = "#base.json"

all_known_numbers = []


# https://sessionnet.dessau.de/bi/si0046.asp?__cjahr=2020&__canz=2&__cmonat=1

def get_list_with_meta(start_year, month_ahead, c_month):
    address = f"https://sessionnet.dessau.de/bi/si0046.asp?__cjahr={start_year}&__canz={month_ahead}&__cmonat={c_month}"
    response = requests.get(address)

    if response.status_code == 200:
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        full_list = []
        last_event_date = ""

        table_body = soup.find('tbody')

        for table_record in table_body.find_all('tr'):
            down_elements = []
            event_date = ""
            other_meta = []

            for record_data in table_record.find_all('td'):
                class_attr = record_data.get('class', [])

                if 'sidat_tag' in class_attr:
                    if record_data.a is not None:
                        event_date = record_data.a.span.next_sibling
                        last_event_date = event_date
                    else:
                        event_date = last_event_date

                if 'silink' in class_attr:
                    if record_data.a is not None:
                        other_meta.append(record_data.a.text)
                        link_to_follow = record_data.a['href']

                        for list_element in record_data.find_all('li'):
                            other_meta.append(list_element.text)

                if 'sidocs' in class_attr:
                    if record_data.a is not None:
                        for element in record_data.find_all('a'):
                            href = element.get('href')
                            if href and href not in down_elements:
                                down_elements.append(href)

            if down_elements:
                full_list.append([event_date, other_meta, down_elements, link_to_follow])

        return full_list


def build_json(list_with_meta):
    meeting_id = extract_meeting_id(list_with_meta[3])
    if not meeting_id:
        return None

    json_data = initialize_json_data(meeting_id, list_with_meta)
    update_json_with_persons(json_data, meeting_id, list_with_meta[3])
    update_json_with_meta(json_data, meeting_id, list_with_meta[3])
    update_json_with_sub_docs(json_data, meeting_id, list_with_meta[3])

    json_output = json.dumps(json_data, indent=4)
    print(json_output)
    # write_json(json_output)


def extract_meeting_id(link):
    meeting_id = re.search(meet_number_pattern, link)
    if meeting_id:
        return meeting_id.group(1)
    return None


def initialize_json_data(meeting_id, list_with_meta):
    files_in_data = build_files_in_data(list_with_meta)
    json_data = {
        meeting_id: {
            "meeting": {
                "link": list_with_meta[3],
                "date": list_with_meta[0],
                "name": "placeholder",
                "responsible": list_with_meta[1][0],
                "start_time": list_with_meta[1][1][:5],
                "end_time": list_with_meta[1][1][-9:-4],
                "location": list_with_meta[1][2]
            },
            "persons": [],
            "main_files": files_in_data,
            "sub_files": []
        }
    }
    return json_data


def build_files_in_data(list_with_meta):
    files_in_data = []
    crawl_date = str(datetime.now())
    for down_file in list_with_meta[2]:
        file_info = build_file_info(down_file, list_with_meta, crawl_date)
        files_in_data.append(file_info)
    return files_in_data


def build_file_info(down_file, list_with_meta, crawl_date):
    file_info = {}
    match_id = re.search(down_number_pattern, down_file)
    if match_id:
        file_info["id"] = match_id.group(1)
    file_info.update({
        "link": list_with_meta[3],
        "crawltime": str(crawl_date),
        "name": "placeholder",
        "hash": "placeholder",
        "doc_type": "main",
        "version": "1"
    })
    return file_info


def update_json_with_persons(json_data, meeting_id, link):
    for person in get_person_data(link):
        new_person = {
            "name": person[0],
            "partie": person[1],
            "type": person[2]
        }
        json_data[meeting_id]["persons"].append(new_person)


def update_json_with_meta(json_data, meeting_id, link):
    new_meta = get_update_meta(link)
    if len(new_meta) != 0:
        json_data[meeting_id]["meeting"]["name"] = new_meta[0]


def update_json_with_sub_docs(json_data, meeting_id, link):
    sub_docs_wth_meta = get_sub_docs(link)
    if len(sub_docs_wth_meta) != 0:
        for each_sub in sub_docs_wth_meta:
            sub_item = build_sub_item(each_sub)
            json_data[meeting_id]["sub_files"].append(sub_item)


def build_sub_item(each_sub):
    all_votes = build_all_votes(each_sub[3])
    sub_item = {
        "id": each_sub[0],
        "desc": each_sub[1],
        "voted_status": each_sub[2],
        "votes": all_votes,
        "requester": each_sub[0].split('/')[-1],
        "files": each_sub[4]
    }
    return sub_item


def build_all_votes(vote_string):
    all_votes = {}
    if len(vote_string) != 0:
        all_votes["yes"] = re.search(r'Ja:\s(\d+)', vote_string).group(1)
        all_votes["no"] = re.search(r'Nein:\s(\d+)', vote_string).group(1)
        all_votes["nonvote"] = re.search(r'Enthaltungen:\s(\d+)', vote_string).group(1)
    return all_votes


def get_person_data(session_link):
    all_member_data = []
    new_addr = down_base_addr + session_link.replace("si0057", "to0045")
    response = requests.get(new_addr)

    if response.status_code == 200:
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        table_body = soup.find('tbody')
        table_rows = table_body.find_all('tr')

        for row in table_rows:
            if 'smcrowh' not in row.get('class', []):
                member_data = [data_part.text.strip() for data_part in row.find_all('td')]
                all_member_data.append(member_data)

    return all_member_data


def get_update_meta(session_link):
    new_meta_data = []
    response = requests.get(down_base_addr + session_link)

    if response.status_code == 200:
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        new_meta_data.append(soup.find("div", {"class": "siname"}).string)

    return new_meta_data


def get_sub_docs(session_link):
    sub_docs_with_meta = []

    new_addr = down_base_addr + session_link
    response = requests.get(new_addr)

    if response.status_code == 200:
        html_text = response.text
        soup = BeautifulSoup(html_text, 'html.parser')
        table_body = soup.find('tbody')

        for table_record in table_body.find_all('tr'):
            toxx_in_record = table_record.find('td', attrs={'class': 'toxx'})
            trenn_in_record = table_record.find('td', attrs={'class': 'totrenn'})

            if not toxx_in_record and not trenn_in_record:
                sub_doc_label = ""
                sub_doc_meta_name = ""
                sub_docs_links = []
                sub_doc_decision = ""
                sub_doc_decision_votes = ""

                sub_doc_meta = table_record.find('td', attrs={'class': 'tobetr'})
                sub_doc_label_element = table_record.find('td', attrs={'class': 'tovo'})

                if sub_doc_label_element is not None:
                    sub_doc_label = sub_doc_label_element.text.strip()

                sub_docs = table_record.find('td', attrs={'class': 'sidocs'})
                sub_docs_links = list(set([a_tag['href'] for a_tag in sub_docs.find_all('a', attrs={'href': True})]))

                sub_doc_meta_name_element = sub_doc_meta.find('div', attrs={'class': 'smc-card-header-title-simple'})

                if sub_doc_meta_name_element is not None:
                    sub_doc_meta_name = sub_doc_meta_name_element.text.strip()

                sub_doc_decision_element = sub_doc_meta.find('p', attrs={'class': 'smc_field_smcdv0_box2_beschluss'})

                if sub_doc_decision_element is not None:
                    sub_doc_decision = sub_doc_decision_element.text.replace("Beschluss: ", "")

                sub_doc_decision_votes_element = sub_doc_meta.find('p',
                                                                   attrs={'class': 'smc_field_smcdv0_box2_abstimmung'})

                if sub_doc_decision_votes_element is not None:
                    sub_doc_decision_votes = sub_doc_decision_votes_element.text.replace("Abstimmung: ", "")

                sub_docs_with_meta.append(
                    [sub_doc_label, sub_doc_meta_name, sub_doc_decision, sub_doc_decision_votes, sub_docs_links])

    return sub_docs_with_meta


def get_doc_hash(content):
    md5_hash = hashlib.md5(content).hexdigest()
    return md5_hash


def main():
    first_data = get_list_with_meta(cjahr, canz, cmonat)
    for line in first_data:
        build_json(line)


if __name__ == "__main__":
    main()