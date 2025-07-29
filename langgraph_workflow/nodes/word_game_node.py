import logging
from langgraph_workflow.models import WorkflowState
from langgraph_workflow.config import word_game_list
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from langgraph_workflow.prompt_templates.nodes_prompts import word_game_prompt
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger(__name__)

# Load API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# Define the expected structure of the LLM response
class WordGameModel(BaseModel):
    ai: str = Field(description="Question asked by AI to user or final response")
    status: str = Field(description="Game status, either 'inprogress' or 'done'")

# Game word list
word_game_list = ["apple", "chair", "elephant", "guitar", "rocket", "pencil", "pizza", "tiger"]

# Create parser and prompt
parser = PydanticOutputParser(pydantic_object=WordGameModel)



# Create the chain
chain = word_game_prompt.partial(
    format_instructions=parser.get_format_instructions(),
    word_game_list=", ".join(word_game_list)
) | llm | parser

# Async word game node
async def word_game_node(state: WorkflowState) -> WorkflowState:
    try:
        logger.info("################### NODE: word_game_node ###################")

        user_input = state.get("user_input", "")
        chat_history = state.get("chat_history", [])

        logger.debug(f"User input: {user_input}")
        logger.debug(f"Chat history: {chat_history}")

        result = await chain.ainvoke({
            "user_input": user_input,
            "chat_history": chat_history
        })

        ai_text = result.ai
        game_status = result.status

        logger.debug(f"Parsed Result: ai='{ai_text}', status='{game_status}'")

    except Exception as e:
        logger.error(f"Error in word_game_node: {e}")
        ai_text = f"Welcome to the word guessing game! I have a list of words: {', '.join(word_game_list)}. Pick one word and I’ll try to guess it with yes/no questions. Are you ready?"
        game_status = "inprogress"

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "ai", "content": ai_text})

    updated_state = state.copy()
    updated_state["answer"] = ai_text
    updated_state["game_status"] = game_status
    updated_state["chat_history"] = chat_history

    return updated_state
