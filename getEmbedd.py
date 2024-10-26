from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
import tempfile
# import google.generativeai as genai
import streamlit as st
import re
from dotenv import load_dotenv
import os

load_dotenv()
# def load_pdf(file_path):
#     """
#     Reads the text content from a PDF file and returns it as a single string.

#     Parameters:
#     - file_path (str): The file path to the PDF file.

#     Returns:
#     - str: The concatenated text content of all pages in the PDF.

#     Raises:
#     - FileNotFoundError: If the specified file_path does not exist.
#     - PyPDF2.utils.PdfReadError: If the PDF file is encrypted or malformed.

#     Example:
#     >>> pdf_text = load_pdf("example.pdf")
#     >>> print(pdf_text)
#     "This is the text content extracted from the PDF file."
#     """
#     # Logic to read pdf
#     reader = PdfReader(file_path)

#     # Loop over each page and store it in a variable
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text()

#     return text


def split_text(text: str):
    """
    Splits a text string into a list of non-empty substrings based on the specified pattern.
    The "\n \n" pattern will split the document para by para
    Parameters:
    - text (str): The input text to be split.

    Returns:
    - List[str]: A list containing non-empty substrings obtained by splitting the input text.

    """
    split_text = re.split('\n \n', text)
    return [i for i in split_text if i != ""]

async def get_vector_store(text_chunks):
    # Create embeddings using a Google Generative AI model
    # api_key = os.getenv("GOOGLE_API_KEY")
    api_key = st.secrets["gemini_key"]
    os.getenv("GOOGLE_API_KEY") = api_key
    print(api_key)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=api_key)

    # Create a vector store using FAISS from the provided text chunks and embeddings
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)

    # Save the vector store locally with the name "faiss_index"
    # vector_store.save_local("faiss_index")
    tempdir = tempfile.mkdtemp()
    vector_store_path = os.path.join(tempdir, "faiss")
    vector_store.save_local(vector_store_path)

    return vector_store_path



# text = load_pdf(file_path="/content/The Complete Book of Ayurvedic Home Remedies.pdf")

async def generateEmbedding(file_text):
    text = file_text
    print("vector Embediing 1")
    text_chunks = split_text(text)
    print("vector Embediing 2")
    location = await get_vector_store(text_chunks)
    print("vector Embediing 3")
    return location
