import os

import requests
from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    _IMPORT_ERROR = None
except ImportError as exc:
    ChatGoogleGenerativeAI = None
    _IMPORT_ERROR = exc


def get_llm():
    """Return a configured ChatGoogleGenerativeAI instance, or None if it
    can't be created (missing package or missing/empty API key)."""
    if ChatGoogleGenerativeAI is None:
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        return None

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key
    )


def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def ask_ai(question, docs, dataset_summary=None):
    if not docs:
        return "No relevant information found."

    context = "\n\n".join(doc.page_content for doc in docs)

    summary_context = ""
    if dataset_summary:
        summary_context = f"""
Authoritative dataset summary:
- Rows: {dataset_summary['rows']}
- Columns: {dataset_summary['columns']}
- Missing values: {dataset_summary['missing']}
- Duplicate rows: {dataset_summary['duplicates']}
Use these exact values for summary questions. Do not estimate them from the sample context.
"""

    prompt = f"""Answer the user's question using only the dataset information below.
If the context does not contain enough information, say so clearly.

User question:
{question}

Dataset context:
{context}
{summary_context}
"""

    api_key = os.getenv("GEMINI_API_KEY")
    if ChatGoogleGenerativeAI is not None and api_key and api_key.strip():
        try:
            response = get_llm().invoke(prompt)
            content = response.content
            if isinstance(content, list):
                content = "\n".join(
                    block.get("text", str(block)) if isinstance(block, dict) else str(block)
                    for block in content
                )
            return content
        except Exception:
            pass

    try:
        return ask_ollama(prompt)
    except requests.RequestException as exc:
        return f"""### ⚠️ AI request failed

Neither Gemini nor the local Ollama model could answer: **{exc}**

Retrieved dataset context:

{context[:1200]}
"""