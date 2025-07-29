from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.config import settings
import os
import json
import logging

logger = logging.getLogger(__name__)


# General JSON response to return in API response
def create_response(message: str, status_code: int, success: bool = False, **kwargs):
    """General JSON response"""

    return JSONResponse(
        status_code=status_code,
        content={"success": success, "message": message, **jsonable_encoder(kwargs)},
    )



def initialize_session(session_id, session_file, game_type=""):
    if not os.path.exists(session_file):
        game_data = {
            "session_id": session_id,
            "current_game_type": game_type,
            "game_status": "",
            "word_game_cnt": 0,
            "number_game_cnt": 0,
            "word_game": {},
            "number_game": {},
        }
        with open(session_file, "w") as f:
            json.dump(game_data, f, indent=4)
        print(f"✅ New session created: {session_file}")
    else:
        print(f"📂 Session already exists: {session_file}")


# Update session based on user_input
def update_game_type_and_count(game_data, user_input):
    if user_input in ["word_game", "number_game"]:
        game_data["current_game_type"] = user_input
        game_data["game_status"] = "inprogress"
        print(f"🎮 Game type set to: {user_input}")
    return game_data



def load_session(session_id, session_file, game_type=None):
    """Load session data, create if doesn't exist"""
    try:
        if not os.path.exists(session_file):
            logger.warning(f"Session file not found, creating: {session_file}")
            initialize_session(session_id, session_file, game_type or "")
        
        with open(session_file, "r") as f:
            game_data = json.load(f)
        
        logger.info(f"Successfully loaded session: {session_id}")
        return game_data
        
    except Exception as e:
        logger.error(f"Error loading session {session_id}: {e}")
        
        return {
            "session_id": session_id,
            "current_game_type": game_type or "",
            "game_status": "",
            "word_game_cnt": 0,
            "number_game_cnt": 0,
            "word_game": {},
            "number_game": {}
        }


def load_required_game_data(game_data):
    """Load game history data with proper error handling"""
    try:
        if not game_data:
            return []
            
        current_game = game_data.get("current_game_type")
        if not current_game:
            logger.warning("No current_game_type found")
            return []
            
        current_game_cnt_key = current_game + "_cnt"
        current_count = game_data.get(current_game_cnt_key, 0)
        
        
        game_key = f"game{current_count}"
        
        
        if current_game not in game_data:
            logger.warning(f"Game type {current_game} not found in data")
            return []
            
        
        history = game_data[current_game].get(game_key, [])
        
        return history if isinstance(history, list) else []
        
    except Exception as e:
        logger.error(f"Error in load_required_game_data: {e}")
        return []


def update_state_result(result_state):
    try:
        session_file = result_state.get("session_file")
        with open(session_file, "r") as f:
            game_data = json.load(f)

        current_type = game_data.get("current_game_type")
        current_status = result_state.get("game_status", "")
        user_input = result_state.get("user_input")
        ai_answer = result_state.get("answer")

        game_data["game_status"] = current_status
        counter = game_data.get(f"{current_type}_cnt", 0)
        game_key = f"game{counter}"

        
        if game_key not in game_data[current_type]:
            game_data[current_type][game_key] = []

        game_rounds = game_data[current_type][game_key]

        
        if game_rounds and game_rounds[-1].get("user") == "":
            game_rounds[-1]["user"] = user_input

           
            if current_status != "done" and ai_answer:
                game_rounds.append({"ai": ai_answer, "user": ""})

        else:
            
            if user_input and ai_answer:
                game_rounds.append({"user": user_input, "ai": ai_answer})
                if current_status != "done":
                    game_rounds.append({"ai": ai_answer, "user": ""})

        
        game_data[current_type][game_key] = game_rounds

    
        if current_status == "done":
            game_data[f"{current_type}_cnt"] += 1
            game_data["game_status"] = ""

        with open(session_file, "w") as f:
            json.dump(game_data, f, indent=4)

        print(f"✅ Game state updated: {game_key} | Status: {current_status}")
        print("---\n")

    except Exception as e:
        print("➡ error in update_state_result:", e)
        raise e


def process_user_input_update_session_data(session_file, request):
    with open(session_file, "r") as f:
        game_data = json.load(f)

    user_input = request.user_input.lower().strip()
    print("➡ user_input:===>", user_input)

    if user_input in ["word_game", "number_game"]:
        game_data = update_game_type_and_count(game_data, user_input)

        # Create new game entry if not already exists
        game_type = user_input
        counter = game_data.get(f"{game_type}_cnt", 0)
        game_key = f"game{counter}"

        if game_key not in game_data[game_type]:
            game_data[game_type][game_key] = []

    elif user_input == "result":
        msg = f"You have played {game_data.get('word_game_cnt', 0)} word games and {game_data.get('number_game_cnt', 0)} number games."
        print("➡ msg:", msg)
        return msg

    else:
        current_type = game_data.get("current_game_type")
        if not current_type:
            return {
                "error": "No game type selected yet. Start with 'word_game' or 'number_game'."
            }

        counter = game_data.get(f"{current_type}_cnt")
        game_key = f"game{counter}"

        if game_key not in game_data[current_type]:
            return {"error": f"Current game entry '{game_key}' not found."}

    with open(session_file, "w") as f:
        json.dump(game_data, f, indent=4)
