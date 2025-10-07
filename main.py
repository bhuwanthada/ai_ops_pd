from fastapi import FastAPI, HTTPException, Query, Request
from typing import List, Dict, Any
import os
from logging_config import setup_logging
import logging
from lg_workflow import compile_graph
from pydantic import BaseModel
from typing import Literal

setup_logging()
logger = logging.getLogger("api")


# --- FastAPI App Definition ---
app = FastAPI(
    title="Google Embeddings Generation and Chroma Db retrieval",
    version="1.0.0"
)

graph_app = None
graph_memory = None


class UserRequest(BaseModel):
    log_id: str
    query: str


class UserReviewLogRequest(BaseModel):
    log_id: str
    user_comment_on_solution: str




@app.on_event("startup")
async def startup_event():
    global graph_app, graph_memory
    graph_memory, graph_app = compile_graph()
    if (not graph_memory) or (not graph_app):
        logger.info("Graph not compiled.")
    else:
        logger.info("Graph compiled and ready to use.")


@app.post("/generate-ai-recommendation")
async def generate_agentic_result(user_request: UserRequest, request: Request):
    """
    Accepts a query string, generates its embedding using Google Vertex AI,
    and searches the Chroma DB for the most similar documents.
    """
    query = user_request.query
    log_id = user_request.log_id

    try:
        global graph_memory, graph_app
        if not query:
            err_msg = "Please provide log alert details."
            logger.exception(err_msg, exc_info=True)
            raise HTTPException(detail=err_msg, status_code=400)
        if not graph_app:
            raise AttributeError()
        config = {"configurable": {"thread_id": log_id}}
        stored_state = graph_memory.get(config)
        message_history = []
        if stored_state and "channel_values" in stored_state:
            print(f"Resuming for log alert case: {log_id}")
            channel_values = stored_state["channel_values"]
            message_history = channel_values["conversation_history"]
            logger.info(f"Important: Same log id : {log_id} identified again.")
        message_history.append(f"user logged alert: {query}")
        initial_state = {
            "user_query": query,
            "conversation_history": message_history
        }
        logger.info(f"Invoking the graph to generate ai based assessment.")
        result = graph_app.invoke(initial_state, config=config)
        logger.info(f"Result from fresh claim execution: {result}")
        if result.get("hallucination_existence"):
            return result.get("terminate_process_due_to_no_ai_suggestion")
        else:
            return result.get("ai_powered_recommendations_with_similarity_search")
    except AttributeError:
        err_msg = "Graph not initialized. Please again."
        logger.exception(err_msg,exc_info=True)
        HTTPException(status_code=500, detail=err_msg)
    except HTTPException as he:
        err_msg = "Something went wrong. Error while processing request."
        logger.exception(f"{err_msg} Exception: {he}", exc_info=True)
        HTTPException(status_code=500, detail=err_msg)
    except Exception as e:
        err_msg = f"An unexpected error occurred during search."
        logger.exception(f"{err_msg} Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=err_msg)


@app.post("/process-human-feedback")
async def process_human_feedback(update_log:UserReviewLogRequest, request: Request):
    try:
        global graph_memory, graph_app
        log_id = update_log.log_id
        human_review_feedback = update_log.human_review_feedback
        if not graph_app:
            raise AttributeError()
        if not human_review_feedback:
            raise HTTPException(detail="Please provide feedback on ai generated solution", status_code=400)
        config = {"configurable": {"thread_id": log_id}}
        stored_state = graph_memory.get(config)
        message_history = []
        if stored_state and "channel_values" in stored_state:
            print(f"Resuming for log alert case: {log_id}")
            channel_values = stored_state["channel_values"]
            message_history = channel_values["conversation_history"]
        new_conversation_msg = f"User updates on ai-assessed solution as: {human_review_feedback}"
        message_history.append(new_conversation_msg)
        update_state = {
            "conversation_history": message_history,
            "human_review_msg": human_review_feedback
        }
        graph_app.update_state(config, update_state)
        result = graph_app.invoke(None, config=config)
        logger.info(f"Result for existing log alert with memory-saver: {result}")
        return result
    except AttributeError:
        err_msg = "Graph not initialized. Please again."
        logger.exception(err_msg, exc_info=True)
        HTTPException(status_code=500, detail=err_msg)
    except HTTPException as he:
        err_msg = "Something went wrong. Error while processing request."
        logger.exception(f"{err_msg} Exception: {he}", exc_info=True)
        HTTPException(status_code=500, detail=err_msg)
    except Exception as e:
        err_msg = f"An unexpected error occurred during search."
        logger.exception(f"{err_msg} Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=err_msg)