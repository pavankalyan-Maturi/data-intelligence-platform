from langchain.agents import create_react_agent
from langchain.agents.agent import AgentExecutor
from langchain.prompts import PromptTemplate
from agent.llm_factory import get_llm
from agent.tools import tools
from agent.parser import RobustReActParser
from mlops.tracking import log_query_run
import time

REACT_PROMPT = PromptTemplate.from_template("""Answer the question using tools. Follow this EXACT format:

Thought: [your reasoning]
Action: SearchData
Action Input: [search query]
Observation: [tool result will appear here]
Thought: [reasoning about result]
Final Answer: [your final answer]

STRICT RULES:
- Action must be on its OWN line
- Action Input must be on the NEXT line after Action
- Never write Action: SearchData(query="...") — that is WRONG
- Always write Action and Action Input as separate lines

CORRECT EXAMPLE:
Thought: I need to search for attrition data
Action: SearchData
Action Input: employees with attrition yes
Observation: Found 5 employees...
Thought: I have the answer
Final Answer: There are 5 employees with attrition Yes

Tools available:
{tools}
Tool names: {tool_names}

Question: {input}
{agent_scratchpad}""")


def run_agent(question: str) -> dict:
    start_time = time.time()    # 🆕 start timer
    llm = get_llm()

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=REACT_PROMPT,
        output_parser=RobustReActParser()
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=3,
        max_execution_time=120,
        handle_parsing_errors=True,
    )

    try:
        result = agent_executor.invoke({"input": question})
        output = result.get("output", "")

        failed_phrases = ["agent stopped", "iteration limit", "couldn't process"]
        if any(p in output.lower() for p in failed_phrases) or not output.strip():
            return _rag_fallback(question, start_time)

        latency = time.time() - start_time  # 🆕

        # 🆕 Log successful agent run
        log_query_run(
            question=question,
            answer=output,
            mode="agent",
            latency_seconds=latency,
            use_agent=True,
            status="success"
        )

        return {
            "question": question,
            "answer": output,
            "latency_seconds": round(latency, 3),
            "status": "success (agent)"
        }

    except Exception as e:
        print(f"Agent error: {e}")
        return _rag_fallback(question, start_time)


def _rag_fallback(question: str, start_time: float) -> dict:
    print("⚠️ Agent failed → falling back to RAG")
    from agent.rag import rag_query

    # track=False because we'll log it here with agent context
    result = rag_query(question, track=False)
    latency = time.time() - start_time  # 🆕 total time including agent attempt

    # 🆕 Log fallback run with agent context
    log_query_run(
        question=question,
        answer=result["answer"],
        mode="RAG fallback",
        latency_seconds=latency,
        context_rows=result.get("sources_found", 0),
        avg_similarity=result.get("avg_similarity", 0.0),
        use_agent=True,
        status="success"
    )

    return {
        "question": question,
        "answer": result["answer"],
        "latency_seconds": round(latency, 3),
        "status": "success (RAG fallback)"
    }