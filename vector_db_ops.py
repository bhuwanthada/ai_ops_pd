import chromadb
import uuid
from google import genai
from google.genai.types import EmbedContentConfig
import pandas as pd
from dotenv import load_dotenv
import os
import logging
from logging_config import setup_logging

load_dotenv()
setup_logging()

logger = logging.getLogger("vector_db_ops")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")


class GoogleEmbeddings:
    def __init__(self):
        try:
            self.gcp_client = genai.Client(vertexai=GOOGLE_GENAI_USE_VERTEXAI,
                                           project=GOOGLE_CLOUD_PROJECT,
                                           location=GOOGLE_CLOUD_LOCATION)
            logger.info("Google embedding client initiated.")
        except Exception as e:
            logger.exception(f"Exception while initializing genai client. Exception: {e}",
                             exc_info=True)
            raise Exception()

    def generate_embedding(self, doc):
        try:
            response = self.gcp_client.models.embed_content(
                model="gemini-embedding-001",
                contents=[
                    doc
                ],
                config=EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=3072
                ),
            )
            logger.debug(f"Embedding successfully created for content: {doc}.")
            return response
        except Exception as e:
            logger.exception(f"Exception while genai embedding generating embedding for "
                             f"content: {doc}. Exception: {e}",
                             exc_info=True)
            raise Exception()

    def generate_response(self, prompt):
        try:
            response = self.gcp_client.models.generate_content(model="gemini-2.5-pro", contents=[prompt])
            return response
        except Exception as e:
            logger.exception(f"Exception while genai generating recommendation. Exception: {e}",
                             exc_info=True)
            raise Exception()


class VectorChromaDB:
    def __init__(self, collection_name):
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path="gen_db")

            self.collection = self.client.get_or_create_collection(
                name=collection_name)
            logger.info(f"Chroma DB client initiated for db: {collection_name}")
        except Exception as e:
            logger.exception(f"Exception while initializing chroma db client. Exception: {e}",
                             exc_info=True)
            raise Exception()

    def create_embeddings(self, doc, metadata):
        """Creates embeddings for the text chunks and stores them in ChromaDB."""
        try:
            # Generate IDs for the chunks
            doc_id = str(uuid.uuid4())

            # Generate embeddings
            response = GoogleEmbeddings().generate_embedding(doc)

            embeddings = response.embeddings[0].values

            # Add chunks to ChromaDB
            self.collection.add(documents=doc, ids=doc_id, embeddings=embeddings, metadatas=metadata)
            logger.info(f"Vector db operation completed for content: {doc}.")
        except Exception as e:
            logger.exception(f"Exception in vector db embedding creation and storing"
                             f"for content: {doc}. Exception: {e}",
                             exc_info=True)
            raise Exception()

    def get_records(self, user_query, top_k):
        try:
            result = self.collection.query(query_embeddings=user_query, n_results=top_k,
                                           include=["metadatas", "documents", "distances"])
            logger.info(f"Similarity search result completed.")
            return result
        except Exception as e:
            logger.exception(f"Exception in similarity search for user_query: {user_query}. Exception: {e}",
                             exc_info=True)
            raise Exception()


def generate_and_store_embedding():
    df_whole = pd.read_csv("sqlserver_incidents.csv")
    # df_whole = pd.read_csv("sqlserver_incidents_latest.csv")
    df = df_whole
    vector_db = VectorChromaDB("pd_incidents")
    counter = 0
    for cols in df.itertuples():
        vector_db.create_embeddings(doc=cols.summary, metadata={"data": cols.log_entries,
                                                                "description": cols.description,
                                                                "summary": cols.summary})
        logger.info(f"Processing completed for row: {counter}")
        counter+=1
# generate_and_store_embedding()


def generate_query_embedding(user_query:str):
    """this method is used to generate embedding for user_query"""
    vector_db = VectorChromaDB("pd_incidents")
    response = GoogleEmbeddings().generate_embedding(user_query)
    qry_embeddings = response.embeddings[0].values
    result = vector_db.get_records(qry_embeddings,top_k=3)
    return result
# testing the solution:
def get_result():
    vector_db = VectorChromaDB("pd_incidents")
    user_query = "SQL server memory pressure observed"
    response = GoogleEmbeddings().generate_embedding(user_query)
    qry_embeddings = response.embeddings[0].values
    result = vector_db.get_records(qry_embeddings,top_k=3)
    return result

# resp = get_result()
# print(resp['metadatas'])
