import logging
from langgraph_workflow.models import WorkflowState
from utils import load_session, load_required_game_data
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()
import os
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama3-70b-8192",api_key=GROQ_API_KEY)

logger = logging.getLogger(__name__)

async def game_selector_node(state: WorkflowState):
    """ Select the game type based on user input. """
    try:
        logger.info("\n################### NODE: game_selector_node ###################")
        
        # Get session info from state with proper error handling
        session_id = state.get('session_id')
        session_file = state.get('session_file')
        
        if not session_id or not session_file:
            raise ValueError("Missing session_id or session_file in state")
            
        # Load session data
        game_data = load_session(session_id=session_id, session_file=session_file)
        
        if not game_data:
            raise ValueError(f"Failed to load session data for session_id: {session_id}")
        
        # Get current game type
        current_game_type = game_data.get("current_game_type", "")
        if not current_game_type:
            raise ValueError("No current_game_type found in session data")
        
        logger.info(f"Selected game type: {current_game_type}")
        
        # Load chat history with error handling
        try:
            chat_history = load_required_game_data(game_data)
            if chat_history is None:
                chat_history = []
        except Exception as e:
            logger.warning(f"Could not load chat history, using empty: {e}")
            chat_history = []
        
        logger.debug(f"Chat history loaded: {len(chat_history) if chat_history else 0} entries")
        
        # Return updated state
        return {
            'current_game_type': current_game_type,
            'chat_history': chat_history,
            'game_data': game_data
        }
        
    except Exception as e:
        logger.error(f"Exception in game_selector_node: {str(e)}")
        raise e