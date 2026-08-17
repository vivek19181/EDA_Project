import os

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_llm():

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )


def ask_ai(question, docs):
    if not docs:
        return "No relevant information found."

    context = "\n\n".join(doc.page_content for doc in docs)

    return f"""### Answer

Based on your uploaded dataset, I found these relevant details:

{context[:1200]}

(This answer is generated from retrieved dataset content without an online LLM.)
"""