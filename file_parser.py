import os
import json
import glob

from dotenv import load_dotenv

from tika import parser
from elasticsearch import Elasticsearch

load_dotenv()


es = Elasticsearch(
    'https://localhost:9200',
    ca_certs="./ca.crt",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD'))
)


def read_json():

    for file in glob.glob(os.path.join(os.getenv('DATA_FOLDER'), '*_base.json')):
        # city = os.path.basename(file).split('_base.json')[0]
        # print(city)

        with open(file) as f:
            data = json.load(f)

        for session in data['sessions'].values():
            for main_file in session['main_files']:
                main_file['parsed_data'] = parser.from_file(os.path.join(os.getenv('DATA_FOLDER'), main_file['name']))

            for sub_session in session['sub_sessions']:
                for sub_file in sub_session['sub_files']:
                    sub_file['parsed_data'] = parser.from_file(os.path.join(os.getenv('DATA_FOLDER'), sub_file['name']))

            yield session


def save_json(data):
    resp = es.index(index=os.getenv('ELASTIC_INDEX'),  document=data)
    print(resp['result'])


if __name__ == '__main__':
    for data in read_json():
        save_json(data)

