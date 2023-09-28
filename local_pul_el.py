import os
import json
import glob
import requests
import hashlib

from tika import parser
from elasticsearch import Elasticsearch

data_folder = "./RIS2_PDF"

es = Elasticsearch(
    'https://192.168.178.63:9200',
    verify_certs=False,
    basic_auth=("elastic", "changeme")
    )


def read_json():
    for file in glob.glob(os.path.join(data_folder, '*_base.json')):
        with open(file) as f:
            data = json.load(f)

        for session in data['sessions'].values():
            for main_file in session['main_files']:
                try:
                    main_file['parsed_data'] = parser.from_file(os.path.join(data_folder, main_file['name']))
                except requests.exceptions.ReadTimeout:
                    print(f"Timeout when processing {main_file}. Skipping...")
                    continue

            for sub_session in session['sub_sessions']:
                for sub_file in sub_session['sub_files']:
                    try:
                        sub_file['parsed_data'] = parser.from_file(os.path.join(data_folder, sub_file['name']))
                    except requests.exceptions.ReadTimeout:
                        print(f"Timeout when processing {sub_file}. Skipping...")
                        continue
            yield session

def compute_hash(file_content):
    return hashlib.md5(file_content.encode()).hexdigest()


def save_json(data):
    doc_id = data['main_files'][0]['parsed_data']['content']
    if not doc_id:
        print(f'error with {data}')
        return
        #doc_id = data['sub_sessions'][0]['sub_files'][0]['parsed_data']['content']
    
    doc_id = compute_hash(doc_id)

    resp = es.index(index="sessionnet_dessau",  document=data, id = doc_id)
    #print(resp['result'])


if __name__ == '__main__':
    i = 0
    for data in read_json():
        print(i)
        i += 1
        save_json(data)
