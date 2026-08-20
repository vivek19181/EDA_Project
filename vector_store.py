import os

import streamlit as st
from langchain_community.vectorstores import FAISS

VECTOR_PATH="vector_db"


@st.cache_resource(show_spinner="Preparing dataset search...")
def build_vector_store(csv_text):
    from chunking import dataframe_to_documents
    from embeddings import get_embedding_model

    documents = dataframe_to_documents(csv_text)
    return create_vector_store(documents, get_embedding_model())


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