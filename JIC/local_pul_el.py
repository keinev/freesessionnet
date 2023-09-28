import os
import json
import glob

from tika import parser
from elasticsearch import Elasticsearch

data_folder = "./RIS2_PDF"

es = Elasticsearch(
    'https://localhost:9200',
    verify_certs=False,
    #ca_certs="ca.crt",
    basic_auth=("elastic", "changeme")
)


def read_json():
    for file in glob.glob(os.path.join(data_folder, '*_base.json')):
        # city = os.path.basename(file).split('_base.json')[0]
        # print(city)
        with open(file) as f:
            data = json.load(f)

        for session in data['sessions'].values():
            for main_file in session['main_files']:
                main_file['parsed_data'] = parser.from_file(os.path.join(data_folder, main_file['name']))

            for sub_session in session['sub_sessions']:
                for sub_file in sub_session['sub_files']:
                    sub_file['parsed_data'] = parser.from_file(os.path.join(data_folder, sub_file['name']))

            yield session


def save_json(data):
    resp = es.index(index="test_local",  document=data)
    #print(resp['result'])


if __name__ == '__main__':
    i = 0
    for data in read_json():
        print(i)
        i += 1
        save_json(data)

