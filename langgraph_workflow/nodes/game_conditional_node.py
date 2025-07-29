import logging
from langgraph_workflow.models import WorkflowState
from langgraph_workflow.config import games_dict

logger = logging.getLogger(__name__)


def route_to_game(state: WorkflowState):
    """Route to the game based on the current game type.
    Task: Implement the logic to route to the appropriate game.
    """
    try:
        # Retrieve the current game type from the state
        current_game_type = state.get("current_game_type", "")

        # Validate if the current game type exists in games_dict
        if current_game_type not in games_dict:
            logger.warning(f"Invalid game type: {current_game_type}")
            # Return a default game or raise an error
            raise ValueError(f"Invalid game type: {current_game_type}")

        # Get the target node name
        next_node = games_dict[current_game_type]

        logger.info(f"Routing to game type: {current_game_type}")
        logger.info(f"Routing to node: {next_node}")

        # Return the appropriate game based on current_game_type
        return next_node

    except Exception as e:
        logger.error(f"Exception in route_to_game: {str(e)}")
        raise e
