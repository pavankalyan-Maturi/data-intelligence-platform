import os

def get_llm(streaming: bool = False):
    """
    Returns appropriate LLM based on environment:
    - Production (GROQ_API_KEY set): Groq cloud LLM
    - Development (no key): Local Ollama
    """
    groq_api_key = os.getenv("GROQ_API_KEY")

    if groq_api_key:
        return _get_groq_llm(groq_api_key)
    else:
        return _get_ollama_llm()


def _get_groq_llm(api_key: str):
    """Groq LLM — fast, free, production ready"""
    try:
        from langchain_groq import ChatGroq
        from langchain.schema.output_parser import StrOutputParser
        print("✅ Using Groq LLM (production)")

        llm = ChatGroq(
            groq_api_key=api_key,
            model_name="llama3-8b-8192",
            temperature=0.0,
            max_tokens=300,
        )
        return llm
    except ImportError as e:
        print(f"⚠️ Groq not available: {e}, falling back to Ollama")
        return _get_ollama_llm()


def _get_ollama_llm():
    """DirectOllama — for local development"""
    from langchain.llms.base import LLM
    from typing import Optional, List
    import requests as req

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
                        },
                        "stop": ["##", "Your task:", "Question:", "\n\n\n"]
                    },
                    timeout=60
                )
                result = response.json().get("response", "").strip()
                if "\n\n" in result:
                    result = result.split("\n\n")[0].strip()
                print(f"✅ Ollama responded: {len(result)} chars")
                return result
            except Exception as e:
                print(f"❌ Ollama error: {e}")
                return f"Error: {str(e)}"

    print("✅ Using DirectOllama (local development)")
    return DirectOllama()