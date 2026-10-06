from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
import json

from tool_registry import TOOLS

from db import (
    create_conversation,
    save_message,
    get_messages,
    get_all_memories,
    save_memory
)


# =========================================
# FASTAPI APP
# =========================================

app = FastAPI(
    title="AI Agent",
    description="AI Agent built from scratch",
    version="1.0"
)


# =========================================
# REQUEST MODEL
# =========================================

class ChatRequest(BaseModel):

    conversation_id: int
    message: str


# =========================================
# SERVE FRONTEND
# =========================================

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


@app.get("/")
def home():

    return FileResponse(
        "frontend/index.html"
    )


# =========================================
# TOOL DESCRIPTIONS
# =========================================

def get_tool_descriptions():

    descriptions = ""

    for name, tool in TOOLS.items():

        descriptions += f"""
Tool: {name}
Description: {tool["description"]}
Arguments: {tool["arguments"]}
"""

    return descriptions


# =========================================
# EXECUTE TOOL
# =========================================

def execute_tool(tool_name, arguments):

    if tool_name not in TOOLS:

        return "Tool not found"

    return TOOLS[tool_name]["function"](
        **arguments
    )


# =========================================
# PARSE LLM RESPONSE
# =========================================

def parse_llm_response(response):

    response = response.strip()

    if response.startswith("```json"):

        response = response[7:]

    if response.startswith("```"):

        response = response[3:]

    if response.endswith("```"):

        response = response[:-3]

    try:

        return json.loads(
            response.strip()
        )

    except json.JSONDecodeError:

        return None


# =========================================
# ASK QWEN
# =========================================

def ask_llm(prompt):

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={
            "model": "qwen3:4b",
            "prompt": prompt,
            "stream": False
        }

    )

    return response.json()["response"]


# =========================================
# CREATE CONVERSATION
# =========================================

@app.post("/conversations")
def create_new_conversation():

    conversation_id = create_conversation(
        "AI Agent Conversation"
    )

    return {
        "conversation_id": conversation_id
    }


# =========================================
# GET CONVERSATION
# =========================================

@app.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int
):

    messages = get_messages(
        conversation_id
    )

    return {

        "conversation_id":
            conversation_id,

        "messages": [

            {
                "role": role,
                "content": content
            }

            for role, content in messages

        ]

    }


# =========================================
# GET MEMORIES
# =========================================

@app.get("/memories")
def get_memories():

    memories = get_all_memories()

    return {

        "memories": [

            {
                "key": key,
                "value": value
            }

            for key, value in memories

        ]

    }


# =========================================
# CHAT
# =========================================

@app.post("/chat")
def chat(request: ChatRequest):

    conversation_id = (
        request.conversation_id
    )

    user_input = request.message


    # -------------------------------------
    # Load conversation
    # -------------------------------------

    previous_messages = get_messages(
        conversation_id
    )

    history = []

    for role, content in previous_messages:

        history.append(
            f"{role}: {content}"
        )


    # -------------------------------------
    # Load long-term memory
    # -------------------------------------

    memories = get_all_memories()

    if memories:

        memory_text = "\n".join(

            f"- {key}: {value}"

            for key, value in memories

        )

    else:

        memory_text = (
            "No long-term memories."
        )


    # -------------------------------------
    # Save user message
    # -------------------------------------

    save_message(
        conversation_id,
        "user",
        user_input
    )

    history.append(
        f"user: {user_input}"
    )


    # -------------------------------------
    # Create prompt
    # -------------------------------------

    prompt = f"""
You are an AI agent.

Available tools:

{get_tool_descriptions()}

Long-term memory:

{memory_text}

Conversation history:

{history}

User request:

{user_input}

Only return valid JSON.

If a tool is required:

{{
    "tool": "tool_name",
    "arguments": {{}},
    "memory": null
}}

If you can answer:

{{
    "tool": "none",
    "answer": "final answer",
    "memory": null
}}

If the user gives an important permanent
personal fact, save it:

{{
    "tool": "none",
    "answer": "final answer",
    "memory": {{
        "key": "memory_key",
        "value": "memory_value"
    }}
}}
"""


    # =====================================
    # AGENT LOOP
    # =====================================

    while True:

        response = ask_llm(prompt)

        data = parse_llm_response(
            response
        )


        if data is None:

            return {
                "error":
                    "Invalid response from LLM"
            }


        # ---------------------------------
        # Save memory
        # ---------------------------------

        memory = data.get(
            "memory"
        )

        if isinstance(memory, dict):

            key = memory.get("key")
            value = memory.get("value")

            if key and value:

                save_memory(
                    key,
                    value
                )


        # ---------------------------------
        # Final answer
        # ---------------------------------

        if data.get("tool") == "none":

            answer = data.get(
                "answer",
                "Done."
            )

            save_message(
                conversation_id,
                "assistant",
                answer
            )

            return {

                "conversation_id":
                    conversation_id,

                "answer":
                    answer

            }


        # ---------------------------------
        # Execute tool
        # ---------------------------------

        tool_name = data.get(
            "tool"
        )

        arguments = data.get(
            "arguments",
            {}
        )

        result = execute_tool(
            tool_name,
            arguments
        )


        # ---------------------------------
        # Save tool result
        # ---------------------------------

        save_message(

            conversation_id,

            "tool",

            f"{tool_name}: {result}"

        )


        history.append(

            f"Tool {tool_name} result: "
            f"{result}"

        )


        # ---------------------------------
        # Next prompt
        # ---------------------------------

        prompt = f"""
You are an AI agent.

Available tools:

{get_tool_descriptions()}

Long-term memory:

{memory_text}

Original user request:

{user_input}

Conversation history:

{history}

Tool result:

{result}

Decide what to do next.

Return ONLY valid JSON.

If another tool is required:

{{
    "tool": "tool_name",
    "arguments": {{}},
    "memory": null
}}

If finished:

{{
    "tool": "none",
    "answer": "final answer",
    "memory": null
}}
"""