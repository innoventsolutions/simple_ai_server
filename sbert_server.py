import json
import os

import chromadb
from fastapi import FastAPI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

app = FastAPI()

# Adjust these values to control Chroma indexing
path = r"/path/to/data/documents"  # In .json format
packet_size = 1000
max_docs = 0
id_field = "sku"
text_field = "name_s"
# End of control values

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persistent_client = chromadb.PersistentClient()
collection = persistent_client.get_or_create_collection(
    name="sbert",
    metadata={"hnsw:space": "cosine"})
db = Chroma(
    client=persistent_client,
    collection_name="sbert",
    embedding_function=embeddings
)


@app.get("/load")
async def load():
    db.reset_collection()
    total_count = 0
    doc_list = []
    id_list = []
    for f_name in os.listdir(path):
        if f_name.endswith(".json"):
            print("Processing file: " + f_name)
            f = open(path + "/" + f_name)
            json_root = json.load(f)
            for i in json_root:
                doc_list.append(Document(
                    page_content=i[text_field],
                    metadata={"id": str(i[id_field])},
                    id=str(i[id_field])
                ))
                id_list.append(str(i[id_field]))
                total_count += 1
                if 0 < max_docs <= total_count:
                    break
                if len(doc_list) >= packet_size:
                    db.add_documents(documents=doc_list, ids=id_list)
                    doc_list.clear()
                    id_list.clear()
        if 0 < max_docs <= total_count:
            break
    if len(doc_list) > 0:
        db.add_documents(documents=doc_list, ids=id_list)
    return {
        "result": 'OK',
        "count": db._collection.count()
    }


@app.get("/query")
async def chroma_search(q: str, count: int):

    out = []
    results = db.similarity_search_with_relevance_scores(q, count)
    for res, score in results:
        out.append({
            "id": res.metadata['id'],
            "score": score
        })
    return out


@app.get("/doc")
async def chroma_get(doc_id: str):

    return db.get([doc_id])
