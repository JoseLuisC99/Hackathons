from typing import Dict, Any, List
from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads
from pymongo.mongo_client import MongoClient
import ssl


class AtlasClient:
    def __init__(self, atlas_uri: str, dbname: str):
        self.mongodb_client = MongoClient(atlas_uri, ssl_cert_reqs=ssl.CERT_NONE)
        self.database = self.mongodb_client[dbname]

    def ping(self):
        self.mongodb_client.admin.command("ping")

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    def insert(self, collection_name: str, collection: Any) -> ObjectId:
        doc = self.database[collection_name].insert_one(collection)
        return doc.inserted_id

    def insert_many(self, collection_name: str, collections: List[Any]) -> List[ObjectId]:
        doc = self.database[collection_name].insert_many(collections)
        return doc.inserted_ids

    def find(self, collection_name: str, filter_dict: Dict[str, Any] | None = None, limit: int = 0):
        filter_dict = filter_dict or {}
        collection = self.database[collection_name]
        return list(collection.find(filter=filter_dict, limit=limit))

    def vector_search(self, collection_name: str, index_name: str, attr_name: str, embedding_vector: List[float], limit: int = 5):
        collection = self.database[collection_name]
        results = collection.aggregate([
            {
                '$vectorSearch': {
                    "index": index_name,
                    "path": attr_name,
                    "queryVector": embedding_vector,
                    "numCandidates": 50,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "title": 1,
                    "authors": 1,
                    "abstract": 1,
                    "categories": 1,
                    "embedding": 1,
                    "search_score": {"$meta": "vectorSearchScore"}
                }
            }
        ])
        return loads(dumps(results))

    def close(self):
        self.mongodb_client.close()