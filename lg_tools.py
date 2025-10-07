from typing import List, Dict
from langchain_core.tools import tool
from vector_db_ops import VectorChromaDB, GoogleEmbeddings
from prompt import (generate_ai_powered_recommendations_with_similarity_search,
                    hallucination_check_prompt,
                    generate_ai_powered_recommendations_with_web_search)
import logging
from logging_config import setup_logging
import json

setup_logging()
logger = logging.getLogger("tools")


@tool
def generate_query_embedding(user_query: str):
    """this method is used to generate embedding for user_query"""

    response = GoogleEmbeddings().generate_embedding(user_query)
    query_embedding = response.embeddings[0].values
    return query_embedding


@tool
def perform_similarity_search(dynamic_content: str):
    """this method is used to perform similarity search on the basis of provided user query embedding."""
    dynamic_content = json.loads(dynamic_content)
    query_embedding = dynamic_content.get("query_embedding")
    top_k = dynamic_content.get("top_search_results")
    vector_db = VectorChromaDB("pd_incidents")
    result = vector_db.get_records(query_embedding, top_k)
    # metadata_content = result.get('metadatas')
    # return metadata_content
    return result


@tool
def generate_vertexai_recommendation_with_similarity_search(dynamic_content: str):
    """this method is used to generate recommendation for provided user dict in json format"""
    dynamic_content = json.loads(dynamic_content)
    user_query = dynamic_content.get("user_query")
    similar_search_content = dynamic_content.get("similar_search_details")
    prompt = generate_ai_powered_recommendations_with_similarity_search(user_query, similar_search_content)
    response = GoogleEmbeddings().generate_response(prompt)
    ai_recommendation = response.text
    return ai_recommendation


@tool
def generate_vertexai_recommendation_with_web_search(dynamic_content: str):
    """this method is used to generate recommendation for provided user dict in json format"""
    dynamic_content = json.loads(dynamic_content)
    user_query = dynamic_content.get("user_query")
    prompt = generate_ai_powered_recommendations_with_web_search(user_query)
    response = GoogleEmbeddings().generate_response(prompt)
    ai_recommendation = response.text
    return ai_recommendation

@tool
def perform_hallucinations_check(processed_content: str):
    """
    this method is used to perform hallucination check for given content."""
    processed_content = json.loads(processed_content)
    user_query = processed_content.get("user_query")
    ai_recommendation = processed_content.get("ai_powered_recommendations")
    prompt = hallucination_check_prompt(user_query, ai_recommendation)
    response = GoogleEmbeddings().generate_response(prompt)
    hallucination_result = response.text
    if "True" in hallucination_result:
        hallucination_present = False
    elif "False" in hallucination_result:
        hallucination_present = True
    else:
        hallucination_present = True
    logger.info(f"Hallucination result: {hallucination_present} based upon response: {hallucination_result} .")
    return hallucination_present
