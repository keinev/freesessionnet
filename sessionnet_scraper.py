from bs4 import BeautifulSoup
import requests
import re
import json
import os
from datetime import datetime


class Sessionnet_Crawler:
    time_pattern = r'\d{2}:\d{2}'
    down_number_pattern = r'id=(\d+)'
    meet_number_pattern = r'inr=(\d+)'
    date_pattern = r'^(\d{2})\.(\d{2})\.(\d{4})$'

    def __init__(self, file_path, city_name, base_address, start_year, start_month, month_ahead, skip_known):
        self.file_path = file_path
        self.city_name = city_name
        self.base_address = base_address.replace("info.asp", "")
        self.start_year = start_year
        self.start_month = start_month
        self.month_ahead = month_ahead
        self.skip_known = skip_known

        self.json_file = f"#{self.city_name.lower()}_base.json"
        self.path_to_file = self.file_path + self.json_file

        self.check_init()

    def check_init(self):
        init_constuct = {"sessions": {}}
        if not os.path.isfile(self.path_to_file):
            init_data = json.dumps(init_constuct)
            with open(self.path_to_file, 'w') as file_writer:
                file_writer.write(init_data)

    def start_crawl(self):
        existing_data = []
        if self.skip_known:
            with open(self.path_to_file, "r") as file:
                existing_data = json.load(file)

        for year in range(self.start_year, int(datetime.today().strftime('%Y')) + 1):
            first_data = self.get_list_with_meta(year, self.month_ahead, self.start_month)
            for line in first_data:
                if self.skip_known:
                    if line[3].replace("si0057.asp?__ksinr=", "") not in existing_data["sessions"]:
                        self.write_json_file(self.build_json(line))
                    else:
                        print(f'skipped {line[0]}')
                else:
                    self.write_json_file(self.build_json(line))

    def build_json(self, list_with_meta):
        meeting_id = re.search(self.meet_number_pattern, list_with_meta[3]).group(1)

        json_data = self.initialize_json_data(meeting_id, list_with_meta)
        self.update_json_with_persons(json_data, meeting_id, list_with_meta[3])

        html_meta_subd = self.get_html_for_meta_and_subdocs(list_with_meta[3])

        self.update_json_with_meta(json_data, meeting_id, html_meta_subd)
        self.update_json_with_sub_docs(json_data, meeting_id, html_meta_subd)

        return json_data

    def initialize_json_data(self, meeting_id, list_with_meta):
        files_in_data = self.build_files_in_data(list_with_meta)
        if len(list_with_meta[1]) == 3:
            got_loc = list_with_meta[1][2]
        else:
            print(f'location error with {list_with_meta[1]}')
            got_loc = ""

        try:
            got_start_time = list_with_meta[1][1][:5]
        except Exception as e:
            got_start_time = ""
        try:
            got_end_time = list_with_meta[1][1][-9:-4]
        except Exception as e:
            got_end_time = ""

        json_data = {
            meeting_id: {
                "meeting": {
                    "link": list_with_meta[3],
                    "date": list_with_meta[0],
                    "name": "",
                    "responsible": list_with_meta[1][0],
                    "start_time": got_start_time,
                    "end_time": got_end_time,
                    "location": got_loc,
                    "last_crawl": str(datetime.now())
                },
                "persons": [],
                "main_files": files_in_data,
                "sub_sessions": []
            }
        }
        return json_data

    def build_files_in_data(self, list_with_meta):
        files_in_data = []
        for down_file in list_with_meta[2]:
            file_info = self.build_file_info(down_file)
            files_in_data.append(file_info)
        return files_in_data

    def build_file_info(self, down_file):
        file_info = {}
        match_id = re.search(self.down_number_pattern, down_file)
        if match_id:
            file_info["id"] = match_id.group(1)
        file_info.update({
            "link": down_file,
            "downloadtime": "",
            "name": "",
            "hash": "",
            "doc_type": "main",
            "version": ""
        })
        return file_info

    def update_json_with_persons(self, json_data, meeting_id, link):
        for person in self.get_person_data(link):
            if len(person) >= 3:
                new_person = {
                    "name": person[0],
                    "partie": person[1],
                    "type": person[2],
                }
                if len(person) > 3:
                    if len(person[3:]) > 0:
                        new_person["bycatch"] = person[3:]
                json_data[meeting_id]["persons"].append(new_person)
            else:
                print(f'error with {person}')

    def get_person_data(self, session_link):
        all_member_data = []
        new_addr = self.base_address + session_link.replace("si0057", "to0045")
        response = requests.get(new_addr)

        if response.status_code == 200:
            html_text = response.text
            soup = BeautifulSoup(html_text, 'html.parser')
            table_body = soup.find('tbody')
            if table_body is not None:
                table_rows = table_body.find_all('tr')
                for row in table_rows:
                    if 'smcrowh' not in row.get('class', []):
                        member_data = [data_part.text.strip() for data_part in row.find_all('td')]
                        all_member_data.append(member_data)
        else:
            print(f'response {response.status_code}')
        return all_member_data

    def get_html_for_meta_and_subdocs(self, link):
        html_text = ""

        new_addr = self.base_address + link
        print(new_addr)
        response = requests.get(new_addr)

        if response.status_code == 200:
            html_text = response.text
        return html_text

    def write_json_file(self, session_to_write):
        with open(self.path_to_file, "r") as file:
            existing_data = json.load(file)

        existing_data["sessions"].update(session_to_write)

        with open(self.path_to_file, "w") as file:
            json.dump(existing_data, file, indent=4)

    def get_list_with_meta(self, start_year, month_ahead, c_month):
        address = f"{self.base_address}si0046.asp?__cjahr={start_year}&__canz={month_ahead}&__cmonat={c_month}"
        response = requests.get(address)
        print(address)

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
                link_to_follow = ""

                for record_data in table_record.find_all('td'):
                    class_attr = record_data.get('class', [])

                    if 'sidat_tag' in class_attr:
                        if record_data.a is not None:
                            date_match = re.match(self.date_pattern, str(record_data.a.span.next_sibling))
                            if date_match:
                                event_date = record_data.a.span.next_sibling
                                last_event_date = event_date
                            else:
                                event_date = last_event_date
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

    def update_json_with_meta(self, json_data, meeting_id, html_text):
        new_meta_data = []

        soup = BeautifulSoup(html_text, 'html.parser')
        new_meta_data = soup.find("div", {"class": "siname"}).string

        if len(new_meta_data) != 0:
            json_data[meeting_id]["meeting"]["name"] = new_meta_data

    def update_json_with_sub_docs(self, json_data, meeting_id, html_text):
        sub_docs_with_meta = []

        soup = BeautifulSoup(html_text, 'html.parser')
        table_body = soup.find('tbody')
        if table_body is not None:
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
                    sub_docs_links = list(
                        set([a_tag['href'] for a_tag in sub_docs.find_all('a', attrs={'href': True})]))

                    sub_doc_meta_name_element = sub_doc_meta.find('div',
                                                                  attrs={'class': 'smc-card-header-title-simple'})

                    if sub_doc_meta_name_element is not None:
                        sub_doc_meta_name = sub_doc_meta_name_element.text.strip()

                    sub_doc_decision_element = sub_doc_meta.find('p',
                                                                 attrs={'class': 'smc_field_smcdv0_box2_beschluss'})

                    if sub_doc_decision_element is not None:
                        sub_doc_decision = sub_doc_decision_element.text.replace("Beschluss: ", "")

                    sub_doc_decision_votes_element = sub_doc_meta.find('p',
                                                                       attrs={
                                                                           'class': 'smc_field_smcdv0_box2_abstimmung'})

                    if sub_doc_decision_votes_element is not None:
                        sub_doc_decision_votes = sub_doc_decision_votes_element.text.replace("Abstimmung: ", "")

                    sub_docs_with_meta.append(
                        [sub_doc_label, sub_doc_meta_name, sub_doc_decision, sub_doc_decision_votes, sub_docs_links])

        if len(sub_docs_with_meta) != 0:
            for each_sub in sub_docs_with_meta:
                sub_item = self.build_sub_item(each_sub)
                json_data[meeting_id]["sub_sessions"].append(sub_item)

    def build_sub_item(self, each_sub):
        all_votes = self.build_all_votes(each_sub[3])
        subfiles_with_meta = self.build_sub_file_meta(each_sub[4])

        sub_item = {
            "id": each_sub[0],
            "desc": each_sub[1],
            "voted_status": each_sub[2],
            "votes": all_votes,
            "requester": each_sub[0].split('/')[-1],
            "sub_files": subfiles_with_meta
        }
        return sub_item

    def build_sub_file_meta(self, all_subfiles):
        subfiles_with_meta = []

        for sub_file in all_subfiles:
            match_id = re.search(self.down_number_pattern, sub_file)
            if match_id:
                sub_id = match_id.group(1)
            else:
                sub_id = ""
            subfile_meta = {
                "id": sub_id,
                "link": sub_file,
                "downloadtime": "",
                "name": "",
                "hash": "",
                "doc_type": "sub",
                "version": ""
            }
            subfiles_with_meta.append(subfile_meta)
        return subfiles_with_meta

    def build_all_votes(self, vote_string):
        all_votes = {}
        if len(vote_string) != 0:
            all_votes["yes"] = re.search(r'Ja:\s(\d+)', vote_string).group(1)
            all_votes["no"] = re.search(r'Nein:\s(\d+)', vote_string).group(1)
            all_votes["nonvote"] = re.search(r'Enthaltungen:\s(\d+)', vote_string).group(1)
        return all_votes


crawler = Sessionnet_Crawler("RIS2_PDF/", "Dessau", "https://sessionnet.dessau.de/bi/info.asp", 2022, 1, 12, False)
crawler.start_crawl()
