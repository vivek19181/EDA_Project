def retrieve_documents(db,query,k=3):

    return db.similarity_search(query,k=k)