from bs4 import BeautifulSoup
import requests
import re

cjahr = "2020"
cmonat = "1"
canz = "12" # months ahead - more is possible but ofc slower
time_pattern = r"\d{2}:\d{2}"

def get_list_with_meta():
    address = "https://sessionnet.dessau.de/bi/si0046.asp?__cjahr=" + cjahr + "&__canz=" + canz + "&__cmonat=" + cmonat
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
                                if ele not in down_elements:
                                    down_elements.append(ele.get('href'))
            if down_elements:
                full_list.append([event_date, other_meta, down_elements])
        return full_list


def main():
    print(get_list_with_meta())


if __name__ == "__main__":
    main()