import re
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.schema import AgentAction, AgentFinish
from typing import Union

class RobustReActParser(ReActSingleInputOutputParser):
    """
    Custom parser that fixes common small LLM formatting mistakes.
    Handles cases like:
    - Action: SearchData(query="...") 
    - Action: SearchData - "query"
    - Missing Action Input line
    """

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        # If Final Answer exists → return it
        if "Final Answer:" in text:
            answer = text.split("Final Answer:")[-1].strip()
            return AgentFinish({"output": answer}, text)

        # Fix common mistake: Action: ToolName(query="...")
        # Extract tool name and input from function-call style
        func_pattern = r'Action:\s*(\w+)\s*\(.*?["\'](.+?)["\'].*?\)'
        func_match = re.search(func_pattern, text)
        if func_match:
            tool_name = func_match.group(1)
            tool_input = func_match.group(2)
            return AgentAction(tool_name, tool_input, text)

        # Fix: Action and Action Input on same line
        same_line = r'Action:\s*(\w+)\s*[-:]\s*["\']?(.+?)["\']?\s*$'
        same_match = re.search(same_line, text, re.MULTILINE)
        if same_match:
            tool_name = same_match.group(1)
            tool_input = same_match.group(2)
            return AgentAction(tool_name, tool_input, text)

        # Try standard parsing
        try:
            return super().parse(text)
        except Exception:
            # Last resort: extract any tool name + use full question as input
            tool_match = re.search(r'Action:\s*(\w+)', text)
            if tool_match:
                tool_name = tool_match.group(1)
                # Extract Action Input if exists
                input_match = re.search(r'Action Input:\s*(.+)', text)
                tool_input = input_match.group(1).strip() if input_match else "search data"
                return AgentAction(tool_name, tool_input, text)

            # Absolute last resort → Final Answer with error
            return AgentFinish(
                {"output": "I couldn't process this query properly."},
                text
            )