import os

from langchain_community.vectorstores import FAISS

VECTOR_PATH="vector_db"


def create_vector_store(documents,embeddings):

    db=FAISS.from_documents(documents,embeddings)

    db.save_local(VECTOR_PATH)

    return db


def load_vector_store(embeddings):

    if os.path.exists(VECTOR_PATH):

        return FAISS.load_local(
            VECTOR_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    return None