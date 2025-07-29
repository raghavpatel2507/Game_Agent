import logging
from langgraph_workflow.models import WorkflowState
from langgraph_workflow.prompt_templates.nodes_prompts import number_game_prompt
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
logger = logging.getLogger(__name__)



class NumberGameModel(BaseModel):
    ai: str = Field(description="question asked by AI to user")
    status: str = Field(description="game status, either 'inprogress' or 'done'")


# i change the logic i used the PydenticOutputParser
parser = PydanticOutputParser(pydantic_object=NumberGameModel)


chain = (
    number_game_prompt.partial(format_instructions=parser.get_format_instructions())
    | llm
    | parser
)


async def number_game_node(state: WorkflowState):
    """Number Game Node for guessing the number"""
    try:
        logger.info("\n################### NODE: number_game_node ###################")
        """
        # TODO: 
        
        - Make a LLM call with the number_game_prompt and NumberGameModel (or format_instructions)
        - Get the response from the LLM -> assign it to llm_response
        - Validate the LLM response structure  (if it's not a dict, convert it into dict)
        - Log the LLM response
        - Add the response to the state and return it
        
        Note: 
        - You can either use LangChain or OpenAI API to make the LLM call
        - Accordingly you can modify 'number_game_prompt' however you want (if you want)
        """
        # Extract data from state
        user_input = state.get("user_input", "")
        chat_history = state.get("chat_history", [])
        current_game_type = state.get("current_game_type", "")

        logger.debug(f"[STATE] user_input: {user_input}")
        logger.debug(f"[STATE] chat_history: {chat_history}")
        logger.debug(f"[STATE] current_game_type: {current_game_type}")

        # Run the chain
        result = await chain.ainvoke(
            {"user_input": user_input, "chat_history": chat_history}
        )

        ai_text = result.ai
        game_status = result.status

        logger.debug(f"LLM Result Parsed: ai={ai_text}, status={game_status}")

    except Exception as e:
        logger.error(f"Exception in number_game_node: {str(e)}")
        ai_text = "I'm ready to start the number guessing game! Think of a number between 1 and 50, and I'll try to guess it. Is your number higher than 25?"
        game_status = "inprogress"

    
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "ai", "content": ai_text})

    # Prepare updated state
    updated_state = state.copy()
    updated_state["answer"] = ai_text
    updated_state["game_status"] = game_status
    updated_state["chat_history"] = chat_history

    return updated_state
