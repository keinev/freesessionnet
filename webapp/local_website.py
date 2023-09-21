from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import re
import os

load_dotenv()

base_website = "https://sessionnet.dessau.de/bi/"

es = Elasticsearch(
    'https://es01:9200',
    ca_certs="/usr/share/elasticsearch/config/certs/ca/ca.crt",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD'))
)

app = Flask(__name__)

items = []
count_found = ""
title = "free4Session"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/", methods =['POST'])
def get_search():
    items = []
    count_found = ""
    query = request.form.get('in_search')


    if re.match(r'^[\w\s]+$', query):
        body = {
            "query": {
                "multi_match" : {
                    "query":      query,
                    "type":       "best_fields",
                    "fields":     [ "*" ]
                }},
                "highlight": {
                    "fields": {
                        "main_files.parsed_data.content": {},
                        "sub_sessions.sub_files.parsed_data.content": {}
                }}}
        try:
            response = es.search(index="sessionnet_dessau", body=body)
            if response['hits']['total']['value'] >= 1:
                count_found = str(response['hits']['total']['value']) + " Ergebnisse in " + str(response['took']) + " ms"
                for hit in response['hits']['hits']:
                    item = {}
                    item["date"] = hit['_source']['meeting']['date']
                    item["accuracy"] = hit['_score']
                    item["link"] = base_website + hit['_source']['meeting']['link']
                    item["resp"] = hit['_source']['meeting']['responsible']
                    preview = hit['highlight']
                    n_content = ""
                    try:
                        for content in preview["sub_sessions.sub_files.parsed_data.content"]:
                            n_content += str(content) + " ... "
                    except:
                        for content in preview["main_files.parsed_data.content"]:
                            n_content += str(content) + " ... "
                    n_content = n_content.replace("\n", "")
                    n_content = n_content.replace("-", "")
                    n_content = n_content.replace("<em", ">")
                    n_content = n_content.replace("/em>", "<")
                    item["desc"] = n_content
                    items.append(item)

            else:
                item = {}
                item["date"] = "could not found " + query
                items.append(item)

        except:
            item = {}
            item["date"] = "could not reach Elastic"
            items.append(item)
        
    else:
        item = {}
        item["date"] = "querry must meet pattern a-zA-Z0-9_ "
        items.append(item)

    return render_template("index.html", items = items, count_found=count_found)


if __name__ == "__main__":
    app.run()