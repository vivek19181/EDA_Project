import streamlit as st

from langchain_text_splitters import RecursiveCharacterTextSplitter


@st.cache_data
def dataframe_to_documents(csv_text):

    splitter=RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    return splitter.create_documents([csv_text])