# Paper Pal AI
_Your AI-Powered Research Partner for Deeper Insights transforms the way you engage with academic literature, moving 
beyond traditional search to provide a truly intelligent and interactive research experience._

## Server script
First, create a virtual environment to run the scripts:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To run the server script, first you need to load the database from kaggle. The dataset used in this project is arXiv 
Dataset (you can download a snapshot it [here](https://www.kaggle.com/datasets/Cornell-University/arxiv)). To load the 
dataset in MongoDB Atlas run the script `push_data.py`, this will load the required fields with a vector embedding 
extracted from GenAI service.
```bash
python ./scripts/push_data.py
```

Once the dataset loaded on MongoDB Atlas, execute the `server.py` script to run the server.
```bash
python server.py
```

### Required environment variables
Set the next variables in your environment:

| Environment variable     | Use                                                                                 |
|--------------------------|-------------------------------------------------------------------------------------|
| GOOGLE_CLOUD_PROJECT     | GCP project name                                                                    |
| GOOGLE_CLOUD_LOCATION    | GCP geographical location (make sure it supports GenAI service)                     |
| GOOGLE_CLOUD_APIKEY      | GCP API key                                                                         |
| EMBEDDING_GENAI_MODEL_ID | GenAI model used to create the embeddings (Defaults to `models/text-embedding-004`) |
| ATLAS_URI                | MongoDB Atlas URL connection                                                        |
| DB_NAME                  | Name of the database (Defaults to `papers`)                                         |
| COLLECTION_NAME          | Collection's name (Defaults to `arxiv`)                                             |
| API_HOST                 | Deploy host (Defauls to `localhost`)                                                |
| API_PORT                 | Deploy port (Defaults to `8000`)                                                    |