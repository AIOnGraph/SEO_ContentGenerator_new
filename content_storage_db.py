from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from pinecone import Pinecone as pp
from langchain_community.vectorstores.pinecone import Pinecone
import streamlit as st





def text_splitter_and_store_in_db(data_to_store):
    # my_bar.progress(45, text="processing data ..")
    for content_topic, dict_content_details in data_to_store.items():
        content_text=dict_content_details["content_text"]
        print(content_text)
        # loader = Docx2txtLoader("example_data/fake.docx")
        text_splitter = CharacterTextSplitter(separator="\n\n\n\n",chunk_size=1000, chunk_overlap=0)
        document = text_splitter.create_documents(texts=[content_text], metadatas=[{"content_topic":content_topic,"content_type":dict_content_details["content_type"],"content_language":dict_content_details["language"],"focus_market":dict_content_details["focus_market"]}])
        print(document)
        content_docs = text_splitter.split_documents(document)
        print(content_docs)
        response = store_data_in_pinecone(content_docs)
        return response


def store_data_in_pinecone(document):
    # my_bar.progress(70, text="Uploading data ..")
    index_name = 'generated-content-storage'
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    pp(api_key=st.secrets["PINECONE_API_KEY"])
    Pinecone.from_documents(document, embeddings, index_name=index_name)
    print("Successfully Uploaded")
    # my_bar.progress(100, text="Successfully Uploaded ")
    return "Successfully Uploaded"


def search_similar():
    index_name = 'generated-content-storage'
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    docsearch = Pinecone.from_existing_index(index_name, embeddings)
    query = "https://www.ongraph.com/market-research-software-tools-for-survey-creation/"
    docs = docsearch.similarity_search(query, k=1)
    print(docs[0].page_content)


def process_to_store_data(content_topic,content_text,content_type,language,focus_market):
    data_to_store={content_topic:{"content_text":content_text,"content_type":content_type,"language":language,"focus_market":focus_market}}
    response = text_splitter_and_store_in_db(data_to_store)
    return response
    


def get_content_from_database(content_topic):
    try:
        query = content_topic
        index_name = 'generated-content-storage'
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        docsearch = Pinecone.from_existing_index(index_name, embeddings)
        docs = docsearch.similarity_search(query, k=1)
        if docs[0].metadata["content_topic"] == query:
            print(docs[0].metadata)
            print(docs[0].page_content)
            print("gettiing from database")
            return docs[0].page_content
        else:
            st.session_state.spinner_status = "Sorry not find anything in Database .. wait "
            return None
        
    except Exception as e:
        return None
        

