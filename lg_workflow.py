import logging
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Optional, Any, List
from dotenv import load_dotenv
from logging_config import setup_logging
from lg_tools import (generate_query_embedding,
                      perform_similarity_search,
                      generate_vertexai_recommendation_with_similarity_search,
                      perform_hallucinations_check,
                      generate_vertexai_recommendation_with_web_search)
import json
import os

load_dotenv()
setup_logging()
logger = logging.getLogger("langgraph_workflow")


class AgentState(TypedDict):
    user_query: str
    query_embedding: Optional[Any]
    similar_identified_incident_details: Optional[Any]
    ai_powered_recommendations_with_similarity_search: str
    ai_powered_recommendations_with_web_search: str
    hallucination_existence: bool
    conversation_history: Optional[Any]
    log_agents_entries: Optional[List]
    human_review_msg: Optional[Any]
    hallucination_check_counter: int
    terminate_process_due_to_no_ai_suggestion: str
    top_search_results: int


def user_query_embed_generator_agent(state: AgentState):
    """Generate the user query vector embeddings"""
    try:
        logger.info(f"{user_query_embed_generator_agent.__name__} started")
        user_query = state.get("user_query", None)
        log_agents_entries = state.get("log_agents_entries", None)
        if not log_agents_entries:
            log_agents_entries = []
        if not user_query:
            err_msg = "User query didn't found."
            logger.exception(err_msg, exc_info=True)
            raise Exception(err_msg)
        query_embedding = generate_query_embedding.invoke(user_query)
        log_agents_entries.append(f"Agent:{user_query_embed_generator_agent.__name__} generated query vector embedding")
        logger.info(f"{user_query_embed_generator_agent.__name__} completed.")
        return {"query_embedding": query_embedding,
                "log_agents_entries": log_agents_entries}
    except Exception as e:
        logger.exception(f"Error in {user_query_embed_generator_agent.__name__}. Exception: {e}", exc_info=True)
        raise Exception()


def similarity_search_executor_agent(state: AgentState):
    """Execute and fetch similarity search from vector DB."""
    try:
        logger.info(f"{similarity_search_executor_agent.__name__} started")
        log_agents_entries = state.get("log_agents_entries", None)
        query_embedding = state.get("query_embedding", None)
        top_search_results = state.get("top_search_results")
        hallucination_check_counter = state.get("hallucination_check_counter")
        if not query_embedding:
            err_msg = "Query Embedding not found."
            logger.exception(err_msg, exc_info=True)
            raise Exception(err_msg)
        if not top_search_results:
            top_search_results = 3
        if hallucination_check_counter:
            top_search_results += hallucination_check_counter
            logger.info(f"IMPORTANT: top search results modified: {top_search_results}")
        logger.info(f"Similarity search top search results counter: {top_search_results}")
        dynamic_content = json.dumps({"query_embedding": query_embedding,
                                      "top_search_results": top_search_results})
        similarity_search_content = perform_similarity_search.invoke(dynamic_content)
        log_agents_entries.append(f"Agent:{similarity_search_executor_agent.__name__} generated "
                                  
                                  f"similarity search content")
        logger.info(f"{similarity_search_executor_agent.__name__} completed.")
        return {"similar_identified_incident_details": similarity_search_content,
                "log_agents_entries": log_agents_entries}

    except Exception as e:
        logger.exception(f"Error in {user_query_embed_generator_agent.__name__}. Exception: {e}", exc_info=True)
        raise Exception()


def llm_generated_recommendation_with_similar_search_agent(state: AgentState):
    try:
        logger.info(f"{llm_generated_recommendation_with_similar_search_agent.__name__} started")
        user_query = state.get("user_query", None)
        log_agents_entries = state.get("log_agents_entries", None)
        similar_search_details = state.get("similar_identified_incident_details")

        if not similar_search_details:
            err_msg = "Similar search content not found."
            logger.exception(err_msg, exc_info=True)
            raise Exception(err_msg)
        similar_search_details = json.dumps(similar_search_details)
        dynamic_content = {"user_query": user_query,
                           "similar_search_details": similar_search_details}
        dynamic_content = json.dumps(dynamic_content)
        ai_powered_recommendations = generate_vertexai_recommendation_with_similarity_search.invoke(dynamic_content)
        log_agents_entries.append(f"Agent:{llm_generated_recommendation_with_similar_search_agent.__name__} generated "
                                  f"ai powered recommendation.")
        logger.info(f"{llm_generated_recommendation_with_similar_search_agent.__name__} completed.")
        return {"ai_powered_recommendations_with_similarity_search": ai_powered_recommendations,
        # return {"ai_powered_recommendations_with_similarity_search": "Change the machine configuration from 2vcpu to 4vcpu",
                "log_agents_entries": log_agents_entries}
    except Exception as e:
        logger.exception(f"Error in {llm_generated_recommendation_with_similar_search_agent.__name__}. Exception: {e}",
                         exc_info=True)
        raise Exception()


def llm_generated_recommendation_with_web_search_agent(state: AgentState):
    try:
        logger.info(f"{llm_generated_recommendation_with_web_search_agent.__name__} started")
        user_query = state.get("user_query", None)
        log_agents_entries = state.get("log_agents_entries", None)
        dynamic_content = {"user_query": user_query}
        dynamic_content = json.dumps(dynamic_content)
        ai_powered_recommendations = generate_vertexai_recommendation_with_web_search.invoke(dynamic_content)
        log_agents_entries.append(f"Agent:{llm_generated_recommendation_with_web_search_agent.__name__} generated "
                                  f"ai powered web search recommendation.")
        logger.info(f"{llm_generated_recommendation_with_web_search_agent.__name__} completed.")
        return {"ai_powered_recommendations_with_web_search": ai_powered_recommendations,
                "log_agents_entries": log_agents_entries}
    except Exception as e:
        logger.exception(f"Error in {llm_generated_recommendation_with_web_search_agent.__name__}. Exception: {e}",
                         exc_info=True)
        raise Exception()


def verifying_hallucination_checker_agent(state: AgentState):
    try:
        logger.info(f"{verifying_hallucination_checker_agent.__name__} started")
        log_agents_entries = state.get("log_agents_entries")
        hallucination_check_counter = state.get("hallucination_check_counter", 0)
        user_query = state.get("user_query")
        logger.info(f"Hallucination check counter: {hallucination_check_counter}")

        if hallucination_check_counter in (0,1):
            ai_powered_recommendations = state.get("ai_powered_recommendations_with_similarity_search")
        elif hallucination_check_counter == 2:
            ai_powered_recommendations = state.get("ai_powered_recommendations_with_web_search")
        else:
            ai_powered_recommendations = None

        if not ai_powered_recommendations:
            err_msg = "ai powered recommendations(similarity search or web_search) content not found."
            logger.exception(err_msg, exc_info=True)
            raise Exception(err_msg)

        dynamic_content = {"user_query": user_query,
                           "ai_powered_recommendations"
                           "": ai_powered_recommendations,
                           "hallucination_check_counter": hallucination_check_counter}

        dynamic_content = json.dumps(dynamic_content)

        hallucination_existence = perform_hallucinations_check.invoke(dynamic_content)
        log_agents_entries.append(f"Agent:{verifying_hallucination_checker_agent.__name__} generated "
                                  f"provided hallucination checks.")
        logger.info(f"{verifying_hallucination_checker_agent.__name__} completed.")
        hallucination_check_counter += 1
        return {"hallucination_existence": hallucination_existence,
                "log_agents_entries": log_agents_entries,
                "hallucination_check_counter": hallucination_check_counter}

    except Exception as e:
        logger.exception(f"Error in {verifying_hallucination_checker_agent.__name__}. Exception: {e}", exc_info=True)
        raise Exception()


def update_to_user_with_llm_recommendation_agent(state: AgentState):
    try:
        logger.info(f"{update_to_user_with_llm_recommendation_agent.__name__} started")
        log_agents_entries = state.get("log_agents_entries", None)
        hallucination_check_counter = state.get("hallucination_check_counter")
        conversation_history = state.get("conversation_history")
        ai_powered_recommendations = None
        if hallucination_check_counter in (1,2):
            logger.info(f"Hallucination counter check:1 means providing response with similarity search")
            ai_powered_recommendations = state.get("ai_powered_recommendations_with_similarity_search")
        elif hallucination_check_counter == 2:
            logger.info(f"Hallucination counter check:2 means providing response with web search")
            ai_powered_recommendations = state.get("ai_powered_recommendations_with_web_search")

        human_review_msg = {"AI_generated_recommendation": ai_powered_recommendations}
        log_agents_entries.append(f"Agent:{update_to_user_with_llm_recommendation_agent.__name__} generated "
                                  f"ai powered recommendation.")
        conversation_history.append(f"agent recommendation: {ai_powered_recommendations}")
        logger.info(f"{update_to_user_with_llm_recommendation_agent.__name__} completed.")
        return {"human_review_msg": human_review_msg,
                "log_agents_entries": log_agents_entries,
                "conversation_history": conversation_history}

    except Exception as e:
        logger.exception(f"Error in {update_to_user_with_llm_recommendation_agent.__name__}. Exception: {e}",
                         exc_info=True)
        raise Exception()


def terminate_process_with_no_ai_suggestion(state: AgentState):
    try:
        logger.info(f"{terminate_process_with_no_ai_suggestion.__name__} started")
        log_agents_entries = state.get("log_agents_entries", None)
        conversation_history = state.get("conversation_history")
        log_agents_entries.append(f"Agent:{terminate_process_with_no_ai_suggestion.__name__} generated "
                                  f"ai powered recommendation.")
        terminate_process_due_to_no_ai_suggestion = "There is no AI powered suggestion due to lack of " \
                                                    "clarity of log details or limited searched_result. " \
                                                    "Please rephrase the log alert and try again."
        conversation_history.append(f"agent message: {terminate_process_due_to_no_ai_suggestion}")
        logger.info(f"{terminate_process_with_no_ai_suggestion.__name__} completed.")
        return {"log_agents_entries": log_agents_entries,
                "conversation_history": conversation_history,
                "terminate_process_due_to_no_ai_suggestion": terminate_process_due_to_no_ai_suggestion}

    except Exception as e:
        logger.exception(f"Error in {terminate_process_with_no_ai_suggestion.__name__}. Exception: {e}",
                         exc_info=True)
        raise Exception()


def generate_iac_code(state: AgentState):
    try:
        logger.info(f"{generate_iac_code.__name__} started")
        log_agents_entries = state.get("log_agents_entries", None)
    except Exception as e:
        logger.exception(f"Error in {generate_iac_code.__name__}. Exception: {e}", exc_info=True)
        raise Exception()


def get_github_repo_details(state: AgentState):
    try:
        logger.info(f"{get_github_repo_details.__name__} started")
        log_agents_entries = state.get("log_agents_entries", None)
    except Exception as e:
        logger.exception(f"Error in {get_github_repo_details.__name__}. Exception: {e}", exc_info=True)
        raise Exception()

#
# def generate_github_pr(state: AgentState):
#     try:
#         logger.info(f"{generate_github_pr.__name__} started")
#         log_agents_entries = state.get("log_agents_entries", None)
#     except Exception as e:
#         logger.exception(f"Error in {generate_github_pr.__name__}. Exception: {e}", exc_info=True)
#         raise Exception()

def validate_hallucination(state: AgentState) -> str:
    logger.info(f"Checking Hallucination for given alert with similarity_search_recommendation powered recommendation")
    if state.get("hallucination_existence") and state.get("hallucination_check_counter") <= 1:
        logger.info(f"Hallucination detected. Need to increase similarity search TOP_K result.")
        return similarity_search_executor_agent.__name__
    elif state.get("hallucination_existence") and state.get("hallucination_check_counter") <= 2:
        logger.info(f"Hallucination detected. Need to regenerate the response from web search.")
        return llm_generated_recommendation_with_web_search_agent.__name__
    elif state.get("hallucination_existence") and state.get("hallucination_check_counter") <= 3:
        logger.info(f"Hallucination present even after similarity search and with web search. "
                    f"Hence returning no response.")
        return terminate_process_with_no_ai_suggestion.__name__
    else:
        return update_to_user_with_llm_recommendation_agent.__name__


def compile_graph():
    logger.info(f"start: {compile_graph.__name__}")
    memory_saver = MemorySaver()
    workflow = StateGraph(AgentState)
    workflow.add_node(user_query_embed_generator_agent.__name__,
                      user_query_embed_generator_agent)
    workflow.add_node(similarity_search_executor_agent.__name__,
                      similarity_search_executor_agent)
    workflow.add_node(llm_generated_recommendation_with_similar_search_agent.__name__,
                      llm_generated_recommendation_with_similar_search_agent)
    workflow.add_node(verifying_hallucination_checker_agent.__name__,
                      verifying_hallucination_checker_agent)
    workflow.add_node(update_to_user_with_llm_recommendation_agent.__name__,
                      update_to_user_with_llm_recommendation_agent)
    workflow.add_node(terminate_process_with_no_ai_suggestion.__name__,
                      terminate_process_with_no_ai_suggestion)
    workflow.add_node(llm_generated_recommendation_with_web_search_agent.__name__,
                      llm_generated_recommendation_with_web_search_agent)
    workflow.add_edge(START, user_query_embed_generator_agent.__name__)
    workflow.add_edge(user_query_embed_generator_agent.__name__,
                      similarity_search_executor_agent.__name__)
    workflow.add_edge(similarity_search_executor_agent.__name__,
                      llm_generated_recommendation_with_similar_search_agent.__name__)
    workflow.add_edge(llm_generated_recommendation_with_similar_search_agent.__name__,
                      verifying_hallucination_checker_agent.__name__)
    workflow.add_edge(llm_generated_recommendation_with_web_search_agent.__name__,
                      verifying_hallucination_checker_agent.__name__)
    workflow.add_conditional_edges(verifying_hallucination_checker_agent.__name__,
                                   validate_hallucination,
                                   {llm_generated_recommendation_with_web_search_agent.__name__:
                                    llm_generated_recommendation_with_web_search_agent.__name__,
                                    update_to_user_with_llm_recommendation_agent.__name__:
                                        update_to_user_with_llm_recommendation_agent.__name__,
                                    terminate_process_with_no_ai_suggestion.__name__:
                                        terminate_process_with_no_ai_suggestion.__name__,
                                    similarity_search_executor_agent.__name__:
                                        similarity_search_executor_agent.__name__})
    workflow.add_edge(update_to_user_with_llm_recommendation_agent.__name__, END)
    workflow.add_edge(terminate_process_with_no_ai_suggestion.__name__, END)
    logger.info(f"end: {compile_graph.__name__}")
    graph_builder = workflow.compile(checkpointer=memory_saver,
                                     interrupt_after=[update_to_user_with_llm_recommendation_agent.__name__])
    logger.info(f"end: {compile_graph.__name__}")
    png_data = graph_builder.get_graph().draw_mermaid_png()
    file_path = os.path.join(os.getcwd(), "workflow.png")
    with open(file_path, "wb") as f:
        f.write(png_data)
    logger.info(f"filed saved at: {file_path}")
    return memory_saver, graph_builder
