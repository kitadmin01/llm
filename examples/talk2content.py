from langchain.document_loaders import BSHTMLLoader, PyPDFLoader, TextLoader, DirectoryLoader
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import numpy as np
from langchain.llms import OpenAI
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo

class DocumentProcessor:
    def __init__(self):
        load_dotenv()
        self.embedding = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0.1)

    def load_and_split_documents(self, url):
        # Load documents from URL
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # PDF Loader Example (Placeholder, not executable in this environment)
        # loader = PyPDFLoader("https://arxiv.org/pdf/2312.14804.pdf")
        # doc = loader.load()

        # Directory Loader Example (Placeholder, not executable in this environment)
        # text_loader_kwargs = {'autodetect_encoding': True}
        # loader = DirectoryLoader('../aikit/content', show_progress=True, loader_cls=TextLoader, loader_kwargs=text_loader_kwargs)
        # docs = loader.load()

        # Splitting documents example (Placeholder)
        # split_docs = ...

        # Placeholder for actual document loading and splitting
        split_docs = ["Your text here"]  # Example placeholder
        return split_docs

    def compute_embeddings(self, text1, text2):
        emb1 = self.embedding.embed_query(text1)
        emb2 = self.embedding.embed_query(text2)
        return np.dot(emb1, emb2)

    def initialize_vector_db(self, split_docs):
        persist_directory = 'vector_store'
        vectordb = Chroma.from_documents(documents=split_docs, embedding=self.embedding, persist_directory=persist_directory)
        return vectordb

    def retrieve_documents(self, vectordb, query):
        query_docs = vectordb.similarity_search(query, k=3)
        print("Documents retrieved by similarity search:", query_docs)
        
        query_docs_mmr = vectordb.max_marginal_relevance_search(query, k=3, fetch_k=30)
        print("Documents retrieved by MMR search:", query_docs_mmr)

        metadata_field_info = [AttributeInfo(name="source", description="Description of the source field", type="string")]
        document_content_description = "Description of document content"
        retriever = SelfQueryRetriever.from_llm(self.llm, vectordb, document_content_description, metadata_field_info, verbose=True)
        docs = retriever.get_relevant_documents(query, k=5)
        print("Documents retrieved using LLM-aided retrieval:", docs)

# Example usage
processor = DocumentProcessor()
split_docs = processor.load_and_split_documents("https://analytickit.com/product/")
distance = processor.compute_embeddings('The sun is shining brightly today.', 'Today, the sunshine is very bright.')
print(f'Distance between embeddings: {distance}')
vectordb = processor.initialize_vector_db(split_docs)
processor.retrieve_documents(vectordb, 'query text')
