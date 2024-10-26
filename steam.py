from getRAG import user_input
from getEmbedd import generateEmbedding
import streamlit as st
from PyPDF2 import PdfReader
import time
import asyncio
import shutil
import os

# To delete Faiss After done
def deleteFaiss():
    try:
        shutil.rmtree("faiss_index")
        print("Directory 'faiss' deleted successfully.")
    except FileNotFoundError:
        print("Directory 'faiss' not found.")


async def getRag(text):
    # summarizer = pipeline("summarization")
    # summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return await user_input(text, st.session_state.db_path)

async def createEmbedding(file_text):
    res = await generateEmbedding(file_text)
    if res is None:
        ValueError("Error in Creating Embedding")
    else:
        return res
    


# Below Frontend

# Initialize session state for API key and messages
# if 'file' not in st.session_state:
#     st.session_state.file = None
if 'situation' not in st.session_state:
    st.session_state.situation = ""
if 'file_text' not in st.session_state:
    st.session_state.file_text = ""
if 'db_path' not in st.session_state:
    st.session_state.db_path = ""
if 'Rag' not in st.session_state:
    st.session_state.Rag = []
# if 'new' not in st.session_state:
#     st.session_state.new = False
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Function to display chat interface
def chat_interface():

        # Display chat history
    for chat in st.session_state.Rag:
        if chat["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"**You:** {chat['content']}")
        else:
            with st.chat_message("assistant"):
                st.markdown(f"**Assistant:** {chat['content']}")

    # Accept user input
    prompt = st.chat_input("Say something")

    if prompt:

        # Add user message to chat history
        st.session_state.Rag.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(f"**You:** {prompt}")

        # Display loading message
        loading_message_placeholder = st.empty()
        loading_message_placeholder.markdown("**Loading...**")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = loop.run_until_complete(getRag(prompt))
            st.markdown(f"**Assistant:** {response}")

        # Clear loading message and display response
        loading_message_placeholder.empty()
        st.session_state.Rag.append({"role": "assistant", "content": response})

# Summarisation Page
def summarisation():
    st.title("Document Summarization")
    # st.write("Please wait, summarisation in progress...")

    # Lazy loading simulation
    if st.button("Summarize"):
        # Display loading message
        loading_message_placeholder = st.empty()
        loading_message_placeholder.markdown("**Sumarizing...**")

        # Display assistant response in chat message container
        # with st.chat_message("assistant"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(getRag("Summarize this Document"))
        # st.write("Summarisation complete!")
        st.text_area("Summary", response, height=700)
        # Clear loading message and display response
        loading_message_placeholder.empty()

        # st.write("### Summary :")
        

# Main application
st.set_page_config(page_title="QA RAG App", layout="wide")

# Sidebar for navigation
if  st.session_state.file_text:
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "Summarisation", "QA Chat"])

else:
    # st.session_state.new = False
    page = "Home"

if page == "Home":
    st.title("Welcome to ArGen")
    st.write("ArGen is an AI-driven solution designed to assist users with the following features:")
    st.write("""
        - **Doc. Summarisation:** Get concise summaries of long documents.
        - **RAG (Retrieval-Augmented Generation):** Perform question-answering on your uploaded document files.
    """)

        # File upload or text input (min 50 words)
    option = st.selectbox("Choose an input method:", ["Upload a PDF", "Enter text (at least 50 words)"])

    if option == "Upload a PDF":
        uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
    else:
        case_text = st.text_area("Enter at least 50 words of text here:")

    # Input to save API key
    # api_key_input = st.text_input("Enter Gemini API key:", type="password")

    if st.button("Save"):
        deleteFaiss()
        if option == "Upload a PDF":
            reader = PdfReader(uploaded_file)
            case_text = ""
            for page in reader.pages:
                case_text += page.extract_text()
            st.session_state.file_text = case_text
        st.session_state.page = "QA Chat"

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        st.session_state.db_path = loop.run_until_complete(createEmbedding(case_text))

        # os.environ["GOOGLE_API_KEY"]=api_key_input
        # st.session_state.new = True
        st.success("File saved! You can now access the chat pages from the sidebar.")
        st.rerun() # Rerun to update the page state

    if st.session_state.file_text:
        if st.button("Reset"):
            # st.session_state.file = None
            deleteFaiss()
            st.session_state.file_text = ""
            st.session_state.db_path = ""
            st.session_state.page = "Home"
            st.success("File Data reset! Please upload a new file on the Home page.")
            st.rerun()  # Rerun to update the page state

elif page == "Summarisation":
    summarisation()

elif page == "QA Chat":
    st.title("Document Chat")
    st.session_state.page = "Rag"
    # st.session_state.new = False
    chat_interface()


    
