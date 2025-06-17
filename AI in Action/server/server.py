import json
import os
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI
from google import genai
from google.genai.types import EmbedContentConfig
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from database.mongo import AtlasClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    app.state.atlas_client = AtlasClient(os.getenv("ATLAS_URI"), os.getenv("DB_NAME", "papers"))
    app.state.client = genai.Client(api_key=os.getenv("GOOGLE_CLOUD_APIKEY"))
    yield
    # Clean up the ML models and release the resources
    app.state.atlas_client.close()

class InputEmbedding(BaseModel):
    content: str

class InputSearch(BaseModel):
    search_text: str

class InputVectorSearch(BaseModel):
    embedding: List[float]

class InputVector(BaseModel):
    embedding: List[float]

class InputRelevance(BaseModel):
    query: str
    abstract: str

class ArxivPaper(BaseModel):
    id: str
    title: str
    authors: str
    abstract: str
    categories: str
    embedding: List[float]
    search_score: float

class BrainstormIdea(BaseModel):
    title: str
    text: str

class BrainstormModel(BaseModel):
    synthesis: str
    gaps: list[str]
    ideas: list[BrainstormIdea]

class BrainstormDocument(BaseModel):
    title: str
    abstract: str

class InputBrainstorm(BaseModel):
    docs: List[BrainstormDocument]

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/embedding")
def embedding(input_embedding: InputEmbedding):
    response = app.state.client.models.embed_content(
        model=os.getenv("EMBEDDING_GENAI_MODEL_ID", "models/text-embedding-004"),
        contents=input_embedding.content,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
        ),
    )
    return {
        "embedding": response.embeddings[0].values
    }

@app.post("/search")
def vectorSearch(input_search: InputSearch):
    response = app.state.client.models.embed_content(
        model=os.getenv("EMBEDDING_GENAI_MODEL_ID", "models/text-embedding-004"),
        contents=input_search.search_text,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
        ),
    )
    embedding_vector =  response.embeddings[0].values
    print(f"embedding_vector: {embedding_vector}")
    mongo_result = app.state.atlas_client.vector_search(
        os.getenv("COLLECTION_NAME"),
        "vector_index",
        "embedding",
        embedding_vector
    )
    print(f"mongo_result: {mongo_result}")
    return mongo_result

@app.post("/vectorSearch")
def vector_search(input_search: InputVectorSearch):
    mongo_result = app.state.atlas_client.vector_search(
        os.getenv("COLLECTION_NAME", "arxiv"),
        "vector_index",
        "embedding",
        input_search.embedding,
    )
    return mongo_result

@app.post("/relevance")
def relevance(input_relevance: InputRelevance):
    prompt = f"""Given this document query:
    {input_relevance.query}
    and this abstract paper:
    {input_relevance.abstract}
    Why does this paper is relevant? Give me a brief description of the relevance (one paragraph) and use plain text, not Markdown.
    """

    genai_resp = app.state.client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=[prompt],
    )
    return genai_resp.text

@app.post("/brainstorm")
def brainstorm(input_brainstorm: InputBrainstorm):
    prompts = ["""
        You are a research collaborator tasked with generating ideas for a new and innovative research paper. Given the following list of academic papers analyze the current state of the art and brainstorm potential directions for novel research. Your response must include:
        1. Brief synthesis of the main themes covered by the listed papers.
        2. Identification of gaps, limitations, or underexplored areas in the current literature.
        3. At least 5 concrete ideas for new research directions or paper topics that would be:
            - Innovative and non-trivial
            - Building upon or deviating meaningfully from the existing work
            - Clearly motivated by the limitations or trends found in the referenced papers
        """]

    for doc in input_brainstorm.docs:
        prompts.append(f"{doc.title}: {doc.abstract}")
    genai_resp = app.state.client.models.generate_content(
        model="gemini-2.5-flash-preview-05-20",
        contents=prompts,
        config={
            "response_mime_type": "application/json",
            "response_schema": BrainstormModel,
        },
    )
    print(json.loads(genai_resp.text))
    return json.loads(genai_resp.text)

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("API_HOST", "localhost"), port=int(os.getenv("API_PORT", "8000")))