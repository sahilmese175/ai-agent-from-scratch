import requests
import json

from tool_registry import TOOLS


# -----------------------------------------
# Get descriptions of all available tools
# -----------------------------------------
def get_tool_descriptions():

    descriptions = ""

    for name, tool in TOOLS.items():

        descriptions += f"""
Tool: {name}
Description: {tool["description"]}
Arguments: {tool["arguments"]}
"""

    return descriptions


# -----------------------------------------
# Execute a tool
# -----------------------------------------
def execute_tool(tool_name, arguments):

    if tool_name not in TOOLS:
        return "Tool not found"

    tool = TOOLS[tool_name]

    function = tool["function"]

    result = function(**arguments)

    return result


# -----------------------------------------
# Parse LLM response
# -----------------------------------------
def parse_llm_response(response):

    response = response.strip()

    # Remove ```json
    if response.startswith("```json"):
        response = response[7:]

    # Remove ```
    if response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        return None


# -----------------------------------------
# Send prompt to local Qwen
# -----------------------------------------
def ask_llm(prompt):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "qwen3:4b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)

    return response.json()["response"]


# -----------------------------------------
# Get user input
# -----------------------------------------
user_input = input("You: ")


# -----------------------------------------
# Get tool descriptions
# -----------------------------------------
tool_descriptions = get_tool_descriptions()


# -----------------------------------------
# Short-term memory
# -----------------------------------------
history = []

history.append(
    f"User: {user_input}"
)


# -----------------------------------------
# Initial prompt
# -----------------------------------------
prompt = f"""
You are an AI agent.

You have access to these tools:

{tool_descriptions}

Your job is to solve the user's request.

You may use one or more tools.

If you need a tool, return ONLY valid JSON:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "value"
    }}
}}

If you have enough information to answer the user, return ONLY valid JSON:

{{
    "tool": "none",
    "answer": "your final answer"
}}

Conversation history:

{history}
"""


# =========================================
# AGENT LOOP
# =========================================

while True:

    # -------------------------------------
    # Ask LLM
    # -------------------------------------
    response = ask_llm(prompt)

    print("\nLLM response:")
    print(response)


    # -------------------------------------
    # Save LLM response to memory
    # -------------------------------------
    history.append(
        f"Agent: {response}"
    )


    # -------------------------------------
    # Convert JSON to Python
    # -------------------------------------
    data = parse_llm_response(response)

    if data is None:

        print("\nInvalid JSON returned by LLM.")
        print("Agent stopped safely.")

        break


    # -------------------------------------
    # Get tool name
    # -------------------------------------
    tool_name = data.get("tool")


    # -------------------------------------
    # Agent finished
    # -------------------------------------
    if tool_name == "none":

        final_answer = data.get(
            "answer",
            "Done."
        )

        print("\nFinal answer:")
        print(final_answer)

        break


    # -------------------------------------
    # Check whether tool exists
    # -------------------------------------
    if tool_name not in TOOLS:

        print("\nUnknown tool:", tool_name)

        break


    # -------------------------------------
    # Get tool arguments
    # -------------------------------------
    arguments = data.get(
        "arguments",
        {}
    )


    # -------------------------------------
    # Execute tool
    # -------------------------------------
    result = execute_tool(
        tool_name,
        arguments
    )


    print("\nTool result:")
    print(result)


    # -------------------------------------
    # Save tool result to memory
    # -------------------------------------
    history.append(
        f"Tool {tool_name} result: {result}"
    )


    # -------------------------------------
    # Create next prompt
    # -------------------------------------
    prompt = f"""
You are an AI agent.

You have access to these tools:

{tool_descriptions}

Original user request:

{user_input}

Conversation history:

{history}

Decide what to do next.

If you need another tool, return ONLY valid JSON:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "value"
    }}
}}

If you have enough information to answer the user, return ONLY valid JSON:

{{
    "tool": "none",
    "answer": "your final answer"
}}
"""