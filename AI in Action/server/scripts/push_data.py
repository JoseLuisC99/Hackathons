import os
import pandas as pd
from google import genai
from google.genai.types import EmbedContentConfig
from dotenv import load_dotenv
from pymongo.errors import OperationFailure
from database.mongo import AtlasClient


load_dotenv()


if __name__ == "__main__":
    atlas_client = AtlasClient(os.getenv("ATLAS_URI"), os.getenv("DB_NAME", "papers"))
    atlas_client.ping()

    client = genai.Client(api_key=os.getenv("GOOGLE_CLOUD_APIKEY"))

    for chunk in pd.read_json("../data/arxiv-metadata.json", lines=True, chunksize=100):
        df = chunk[["id", "title", "authors", "abstract", "categories"]].copy()
        print(df["categories"].head())

        response = client.models.embed_content(
            model=os.getenv("GOOGLE_GENAI_MODEL_ID", "models/text-embedding-004"),
            contents=(df["title"] + "\n" + df["abstract"]).to_list(),
            config=EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
            ),
        )
        df["embedding"] = list(map(lambda x: x.values, response.embeddings))
        try:
            atlas_client.insert_many(os.getenv("COLLECTION_NAME", "arxiv"), df.to_dict("records"))
        except OperationFailure as e:
            print(f"Error while loading data: {e}")
            break