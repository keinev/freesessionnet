from flask import Flask, request, render_template
from elasticsearch import Elasticsearch

base_website = "https://sessionnet.dessau.de/bi/"

es = Elasticsearch(
    'https://localhost:9200',
    verify_certs=False,
    #ca_certs="./ca.crt",
    basic_auth=("elastic", "changeme")
)

app = Flask(__name__)

items = []

title = "free4Session"

@app.route("/")
def home():
    return render_template("index.html", items=items)

@app.route("/", methods =['POST'])
def get_search():
    items = []
    query = request.form.get('in_search')

    body = {
        "query": {
            "multi_match" : {
                "query":      query,
                "type":       "best_fields",
                "fields":     [ "*" ]
            }}}
    response = es.search(index="test_local", body=body)

    if response['hits']['total']['value'] >= 1:
        for hit in response['hits']['hits']:
            item = {}
            print(hit['_score'])
            print(base_website + hit['_source']['meeting']['link'])
            print(hit['_source']['meeting']['date'])

            item["date"] = hit['_source']['meeting']['date']
            item["accuracy"] = hit['_score']
            item["link"] = base_website + hit['_source']['meeting']['link']
            item["resp"] = hit['_source']['meeting']['responsible']
            try:
                item["desc"] = hit['_source']['main_files']['name']
            except TypeError:
                item["desc"] = "Error"
                

            items.append(item)
    else:
        item = {}
        item["date"] = "could not found " + query
        items.append(item)


    return render_template("index.html", items = items)


if __name__ == "__main__":
    app.run()