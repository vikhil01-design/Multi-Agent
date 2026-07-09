import logging
import time
import os
from fastapi import FastAPI, Query
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from graph import build_graph
from guardrails import guardrail_check
import asyncio
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("agent.log")],
)

logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/research")
async def research(query: str = Query(..., description="Research query")):
    """
    Accepts query as a request parameter.
    Example:
    POST /research?query=Research Tesla revenue
    """
    start_time = time.time()
    logger.info(f"MAIN: Received research request: {query[:100]}...")

    if not query.strip():
        logger.warning("MAIN: Empty query received")
        return {"status": "error", "message": "Query cannot be empty"}

    guardrail_result = guardrail_check(query)
    if not guardrail_result.get("allowed", True):
        logger.warning(
            f"MAIN: Guardrail blocked request: {guardrail_result.get('reason')}"
        )
        return {
            "status": "blocked",
            "message": guardrail_result.get("reason"),
            "guardrail": guardrail_result,
        }

    state = {
        "user_prompt": [HumanMessage(content=query)],
        "crew_response": [],
        "critic_decision": "",
        "retries": 0,
    }

    # Calculate timeout: account for LLM retries (4 attempts * 60s) + backoff delays (5+10+15s)
    # + web searches + processing. Use 5 minutes (300s) to be safe.
    # This ensures retries don't cause premature timeouts
    timeout_seconds = 300  # 5 minutes - accounts for retries and slow operations

    graph = build_graph()

    logger.info("MAIN: Starting graph execution...")
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(
                graph.invoke,
                state,
                {"recursion_limit": 30},
            ),
            timeout=timeout_seconds,
        )
        elapsed_time = time.time() - start_time
        logger.info(
            f"MAIN: Graph execution completed successfully in {elapsed_time:.2f} seconds"
        )
        logger.info(
            f"MAIN: Final state - task_complete: {result.get('task_complete')}, steps: {len(result.get('execution_results', []))}"
        )
    except asyncio.TimeoutError:
        elapsed_time = time.time() - start_time
        logger.error(
            f"MAIN: Request timed out after {elapsed_time:.2f} seconds (limit: {timeout_seconds}s)"
        )
        logger.error(
            "MAIN: Note: Graph execution may continue in background. Check agent.log for final results."
        )
        return {
            "status": "timeout",
            "message": f"Request exceeded {timeout_seconds}s timeout ({elapsed_time:.2f}s elapsed). LLM retries or web searches may be slow. Check agent.log for details - execution may complete after timeout.",
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            f"MAIN: Error during execution after {elapsed_time:.2f} seconds: {str(e)}",
            exc_info=True,
        )
        return {"status": "error", "message": f"Error during execution: {str(e)}"}

    user_prompt_value = result.get("user_prompt", [])
    if isinstance(user_prompt_value, list) and user_prompt_value:
        first_message = user_prompt_value[0]
        if hasattr(first_message, "content"):
            user_query_text = first_message.content
        elif isinstance(first_message, dict):
            user_query_text = first_message.get("content", "")
        else:
            user_query_text = str(first_message)
    else:
        user_query_text = str(user_prompt_value)

    return {
        "status": "success",
        "UserQuery": user_query_text,
        "CrewResponse": result.get("crew_response", ""),
        "CriticDecision": result.get("critic_decision", ""),
        "Retries": result.get("retries", 0),
        "HumanHandoff": result.get("humanHandOff", False),
        "HumanHandoffRef": result.get("humanHandOffRef", ""),
        "Guardrail": guardrail_result,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


# def main():
#     investment_state = {
#         "user_prompt": "Evaluate investment opportunities in renewable energy stocks.",
#     }

#     crew_output = investment_crew_node(investment_state)
#     print("Crew execution result:")
#     print(crew_output)
#     print("STATE===>", investment_state)


# if __name__ == "__main__":
#     main()
