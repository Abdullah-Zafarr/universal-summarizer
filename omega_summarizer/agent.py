"""
agent.py — Groq-powered Agentic orchestration.
"""

import os
import json
from groq import Groq
from prompts import SYSTEM_PROMPT, TOOL_DEFINITIONS
from tools import execute_tool
from .utils import add_log

def run_agent(user_input: str, model: str):
    """
    Orchestrates the agentic flow:
    1. Sends user input to Groq with tool definitions.
    2. Groq decides which tool to call.
    3. Tool executes — the FULL result is stored for the user.
    4. A SHORT confirmation is sent back to Groq.
    5. Groq produces a brief final response (or we use the tool result directly).
    """
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key.startswith("your_"):
        return "❌ **GROQ_API_KEY** is not set. Please add it to your `.env` file."

    client = Groq(api_key=groq_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    add_log("agent", "Starting Groq orchestration…", "working")
    
    # Store the full tool result here — this is what the user sees
    last_tool_result = None
    max_iterations = 3  # Reduced — should only need 1-2 iterations

    for iteration in range(max_iterations):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                max_tokens=4096,
            )
        except Exception as e:
            error_msg = str(e)
            add_log("agent", f"Groq API error: {error_msg}", "error")
            # If Groq fails but we already got a good tool result, use that
            if last_tool_result and not last_tool_result.startswith("❌"):
                add_log("agent", "Using cached tool result ✓", "success")
                return last_tool_result
            return f"❌ Groq API call failed: {error_msg}"

        choice = response.choices[0]

        # ── If Groq wants to call a tool ──
        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}

                add_log(tool_name, f"Executing with args: {tool_args}", "working")

                # Execute the tool — this returns the FULL formatted summary
                tool_result = execute_tool(tool_name, tool_args)
                last_tool_result = tool_result  # Save the full result

                add_log(tool_name, "Completed ✓", "success")

                # Send only a SHORT confirmation back to Groq
                if tool_result.startswith("❌"):
                    truncated = tool_result[:500]
                else:
                    truncated = "[Tool completed successfully. The summary has been generated and will be displayed to the user. Just confirm completion in your response.]"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": truncated,
                })

        # ── If Groq returns a final response ──
        elif choice.finish_reason == "stop":
            add_log("agent", "Final response ready ✓", "success")
            # If we have a full tool result, prefer that over Groq's text
            if last_tool_result and not last_tool_result.startswith("❌"):
                return last_tool_result
            # Otherwise use Groq's response
            return choice.message.content or last_tool_result or "❌ No response generated."

        else:
            add_log("agent", f"Unexpected finish_reason: {choice.finish_reason}", "error")
            if last_tool_result and not last_tool_result.startswith("❌"):
                return last_tool_result
            return choice.message.content or "❌ Unexpected response from the orchestrator."

    # If we hit max iterations but have a good tool result, use it
    if last_tool_result and not last_tool_result.startswith("❌"):
        add_log("agent", "Returning cached tool result ✓", "success")
        return last_tool_result

    add_log("agent", "Max iterations reached", "error")
    return "❌ Agent loop hit the safety limit. Please try again."
