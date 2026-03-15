from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Optional, List
import requests as req
from agent.llm_factory import get_llm

class DirectOllama(LLM):
    model: str = "phi3:mini"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.0
    num_predict: int = 150
    num_ctx: int = 512

    @property
    def _llm_type(self) -> str:
        return "direct_ollama"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            response = req.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.num_predict,
                        "num_ctx": self.num_ctx,
                        "stop": stop or []
                    }
                },
                timeout=60
            )
            result = response.json().get("response", "")
            print(f"✅ LLM responded: {len(result)} chars")
            return result
        except Exception as e:
            print(f"❌ LLM error: {e}")
            return f"LLM error: {str(e)}"

def get_llm(streaming: bool = False) -> DirectOllama:
    print("✅ Using DirectOllama")
    return DirectOllama()