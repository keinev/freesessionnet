from fastapi import FastAPI
from elasticsearch import Elasticsearch
import os

from dotenv import load_dotenv

from fastapi.responses import HTMLResponse
import aiofiles


load_dotenv()

app = FastAPI()

es = Elasticsearch(
    'https://localhost:9200',
    ca_certs="./ca.crt",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD'))
)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    async with aiofiles.open('index.html', mode='r') as f:
        content = await f.read()
    return HTMLResponse(content=content)


@app.get("/search_all")
async def read_root(query: str):
    body = {
        "query": {
            "multi_match" : {
                "query":      query,
                "type":       "best_fields",
                "fields":     [ "*" ]
            }
        }
    }

    response = es.search(index=os.getenv('ELASTIC_INDEX'), body=body)
    return response
