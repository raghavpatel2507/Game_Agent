import logging
from fastapi import APIRouter, Depends
from utils import (
    create_response,
    initialize_session,
    update_state_result,
    process_user_input_update_session_data,
)
import os
from langgraph_workflow.models import ChatRequest
from langgraph_workflow.workflow import LanggraphAgents
import uuid

# Create a directory to store session files
SESSION_DIR = "sessions_data"
os.makedirs(SESSION_DIR, exist_ok=True)

router = APIRouter(prefix="/agent", tags=["agent"])

lang_agent = LanggraphAgents()
logger = logging.getLogger(__name__)

session_id = str(uuid.uuid4())


@router.post("/game")
async def chat(request: ChatRequest, graph=Depends(lang_agent.build_workflow)):
    try:
        logger.info("========= Inside Game API =========")

        global session_id
        logger.debug(f"Request Session ID: '{session_id}'")
        session_file = os.path.join(SESSION_DIR, f"{session_id}.json")

        # Initialize session file and game state
        initialize_session(session_id, session_file)

        # Update session file with user input and read game state
        data = process_user_input_update_session_data(session_file, request)

        if request.user_input == "result":
            return create_response(
                message="Results fetched successfully",
                status_code=200,
                success=True,
                data=data,
            )

        ############### Start the workflow ###############

        # Initialize state with required data for LangGraph
        intial_state = {
            "session_id": session_id,
            "session_file": session_file,
            "user_input": request.user_input,
            "game_data": {},  # Will be populated by nodes
            "chat_history": [],  # Will be populated by nodes
            "current_game_type": "",  # Will be populated by nodes
            "answer": "",
            "game_status": "",
        }

        # Run the LangGraph agent
        result_state = await graph.ainvoke(intial_state)

        # Update state with results
        update_state_result(result_state)

        # TODO:Add appropriate response to data_res dict from result_state
        data_res = {
            "answer": result_state.get("answer", ""),
            "game_status": result_state.get("game_status", ""),
            "current_game_type": result_state.get("current_game_type", ""),
            "session_id": result_state.get("session_id", ""),
        }

        logger.debug(f"Answer for the user query: '{result_state.get('answer')}'")

        return create_response(
            message="Answer retrieved successfully",
            status_code=200,
            success=True,
            data=data_res,
        )

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return create_response(
            message="Something went wrong while retrieving the answer",
            status_code=500,
            success=False,
            data={},
        )
