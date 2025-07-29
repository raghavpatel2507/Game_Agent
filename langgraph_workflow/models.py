from pydantic import BaseModel
from typing import TypedDict

class ChatRequest(BaseModel):
    user_input: str
    
# Define state schema
class WorkflowState(TypedDict):
    user_input: str =""
    game_data: dict
    chat_history: dict
    session_id: str = None
    session_file: str = None
    current_game_type: str = None
    answer: str
    game_status: str