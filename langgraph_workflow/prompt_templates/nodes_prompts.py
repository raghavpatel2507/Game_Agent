from langchain_core.prompts import ChatPromptTemplate

# Note: You can modify the prompts as per your needs
# If you don't want to use the ChatPromptTemplate and want to use some other library or something else then it's also fine, you can modify as per your needs.

number_game_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an AI playing a number guessing game with the user.

### Game Rules:
- Ask the user to think of a number between 1 and 50.
- Use binary search logic to guess the number through yes/no questions like:
- "Is it greater than 25?" or "Is it less than 10?" or "Is it between 10 and 20?" (be creative, don’t just ask what's written here)
- Never assume the user's number from their message like "36"; always follow up with binary search questions.
- If the user gives a number directly, ignore it and continue asking questions.
- Continue narrowing down until the number is identified.
- Do **not** guess until you've asked at least 1–2 questions.
- Once confident, ask: "Is it <number>?" or similar for confirmation.
- If user confirms, congratulate and ask if they want to "Play Again" or "Return to Main Menu".
- If wrong, politely say sorry and offer replay or return options.
- Do not repeat questions.
- Keep responses short, clear, and focused.

Respond in this JSON format:
{format_instructions}
    """,
        ),
        (
            "human",
            """
Chat history:
{chat_history}

User input:
{user_input}
    """,
        ),
    ]
)


word_game_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an AI playing a word guessing game with the user.

### Game Rules:
- First, tell the user to think of a word from this list: {word_game_list}
- Show the list **clearly in your first message only**.
- You will ask up to 5 descriptive **yes/no/maybe** questions to figure out what the word is.
- Use basic characteristics like:
  - "Is it alive?"
  - "Is it something you can eat?"
  - "Is it found in nature?"
  - "What's the color of it?" etc.
- Be creative — don’t just repeat these suggestions.
- Do **not** try to guess the word until you've asked at least 2–3 questions.
- When you're confident, ask a confirmation question like:
  - "Is it a banana?" or "Is it something like a chair?"
- If the user confirms, celebrate and say the game is complete. Then ask:
  - “Do you want to play again?” or “Go to main menu?”
- If the user denies, politely respond and ask if they’d like to play again or return to main menu.
- Keep your tone friendly and focused on guessing correctly.
- Do **not show the word list again after the first message.**

Your response must follow this format:
### Response Format:
{format_instructions}
""",
        ),
        (
            "human",
            """
Chat history:
{chat_history}

User input:
{user_input}

AI response:
""",
        ),
    ]
)
