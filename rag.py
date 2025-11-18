import streamlit as st
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.prompts import PromptTemplate

# --- 1. CONFIGURATION AND INITIALIZATION ---

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Please create a .env file and set the key.")
    st.stop()

# Qdrant Configuration
COLLECTION_NAME = "employee_documents"
QDRANT_URL = "http://localhost:6333"  # Ensure your Qdrant server is running

# Initialize clients
try:
    QDRANT_STORAGE_PATH = "qdrant_storage_local"
    qdrant_client = QdrantClient(path=QDRANT_STORAGE_PATH)
    # Check if collection exists
    collections = qdrant_client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        # If not, create it
        # We need the dimension of the embedding model (Gemini-based embeddings are typically 768)
        # Note: LangChain's GoogleGenerativeAIEmbeddings might default to a different dimension.
        # For simplicity and robust embedding, we'll initialize the model to check dimensions
        # but for a stable demo, we'll use a common dimension (768 for text-embedding-004)
        # Replace '768' with the actual dimension if you use a specific model.
        EMBEDDING_DIMENSION = 768

        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIMENSION, distance=Distance.COSINE),
        )
        st.success(f"Created Qdrant collection: {COLLECTION_NAME}")

    # Initialize Gemini and Embeddings
    llm = GoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", api_key=GEMINI_API_KEY)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", api_key=GEMINI_API_KEY)

    # Initialize LangChain Qdrant Vector Store
    vectorstore = Qdrant(
        client=qdrant_client,
        collection_name=COLLECTION_NAME,
        embeddings=embeddings,
    )

except Exception as e:
    st.error(f"Error initializing Qdrant or Gemini: {e}")
    st.stop()


# --- 2. DATA PROCESSING FUNCTIONS ---

def get_document_loader(file_path):
    """Selects the correct LangChain DocumentLoader based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyPDFLoader(file_path)
    elif ext == ".txt":
        return TextLoader(file_path)
    elif ext in [".doc", ".docx"]:
        return UnstructuredWordDocumentLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def process_and_store_file(uploaded_file, employee_id):
    """
    Handles file upload, parsing, chunking, and storing in Qdrant.
    """
    try:
        # Save uploaded file temporarily
        temp_dir = "temp_files"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load document
        loader = get_document_loader(file_path)
        docs = loader.load()

        # Chunk document
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)

        # Add metadata (employee_id) to each chunk
        for chunk in chunks:
            chunk.metadata["employee_id"] = employee_id

        # Store in Qdrant
        vectorstore.add_documents(chunks)

        # Clean up temporary file
        os.remove(file_path)

        return len(chunks)

    except Exception as e:
        st.error(f"Error processing file for Employee ID {employee_id}: {e}")
        return 0


# --- 3. GUARDRAILS AND RAG CHAIN SETUP ---

def create_qa_chain():
    """
    Creates the RetrievalQA chain with a custom prompt for guardrails and masking.
    """
    # 1. Guardrail for irrelevant questions / out of context
    # 2. Guardrail for masking (Aadhaar/PAN) data 
    # (Note: This is a PROMPT-LEVEL guardrail and is not a 100% security solution. 
    # For robust security, you'd need a separate PII detection/masking layer before embedding.)

    template = """
    You are an AI assistant for a human resources department. Your task is to answer questions about employee documents based *only* on the provided context.

    CONTEXT:
    {context}

    QUESTION: {question}

    YOUR RULES:
    1. **Strict Context:** Answer the question ONLY if the required information is present in the CONTEXT.
    2. **Out of Scope:** If the question is *not* directly related to the provided employee document context, or if the answer is not in the context, respond with: "I can only answer questions related to the employee's uploaded documents (e.g., resume, contract details, work history). This question is outside my scope."
    3. **PII Masking:** **NEVER** disclose sensitive personally identifiable information (PII) like Aadhaar numbers, PAN numbers, or full home addresses. If the question asks for this information, respond with: "I cannot disclose sensitive PII like Aadhaar or PAN numbers for security and privacy reasons."
    4. **Answer Format:** Keep your answers concise and professional.

    ASSISTANT RESPONSE:
    """

    QA_PROMPT = PromptTemplate(
        template=template, input_variables=["context", "question"]
    )

    # Create the RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": QA_PROMPT},
        return_source_documents=False  # Set to True for debugging
    )

    return qa_chain


qa_chain = create_qa_chain()

# --- 4. STREAMLIT UI ---

st.set_page_config(page_title="Employee RAG Chatbot", layout="wide")
st.title("👨‍💼 Employee Document RAG Chatbot (Gemini + Qdrant)")
st.caption("Upload employee files and query specific employee data using Gemini LLM.")

# Sidebar for Upload and Indexing
with st.sidebar:
    st.header("1. Upload & Index Documents")

    employee_id_input = st.text_input("Enter Employee ID (e.g., E101)", key="employee_id_input")

    uploaded_files = st.file_uploader(
        "Upload Employee Files (txt, pdf, docx)",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True
    )

    if st.button("Index Files"):
        if not employee_id_input:
            st.warning("Please enter an **Employee ID**.")
        elif not uploaded_files:
            st.warning("Please upload at least one file.")
        else:
            total_chunks = 0
            with st.spinner(f"Indexing files for Employee {employee_id_input}..."):
                for uploaded_file in uploaded_files:
                    chunks = process_and_store_file(uploaded_file, employee_id_input)
                    total_chunks += chunks
            st.success(
                f"Successfully indexed **{len(uploaded_files)}** files into **{total_chunks}** chunks for Employee ID **{employee_id_input}**.")

st.header("2. Ask a Question")


# Get existing employee IDs for querying
# This is a mock function; a real implementation would query Qdrant metadata for distinct IDs
def get_available_employee_ids():
    # In a real app, you'd use a Qdrant 'scroll' query to get unique metadata values.
    # For this demo, we'll just check if any data exists.
    try:
        count = qdrant_client.count(collection_name=COLLECTION_NAME, exact=True).count
        return ["E101", "E102", "E999"] if count > 0 else []  # Use known IDs for demo
    except:
        return []


available_ids = get_available_employee_ids()

if not available_ids:
    st.info("Please index some documents first to enable querying.")
    st.stop()

# Employee ID selection for query (metadata filtering)
selected_employee_id = st.selectbox(
    "Select Employee ID to Query",
    options=["All Employees"] + available_ids,
    index=0
)

user_query = st.text_area("Your Question:")

if st.button("Get Answer"):
    if not user_query:
        st.warning("Please enter a question.")
    else:
        # --- Metadata Filter (Qdrant specific filtering) ---
        qdrant_filter = None
        if selected_employee_id != "All Employees":
            qdrant_filter = {
                "must": [{
                    "key": "employee_id",
                    "match": {"value": selected_employee_id}
                }]
            }

        # Configure the retriever with the Qdrant filter
        # Note: LangChain's Qdrant implementation accepts 'search_kwargs' for filtering.
        qa_chain.retriever.search_kwargs = {"filter": qdrant_filter}

        with st.spinner(f"Searching documents for Employee {selected_employee_id}..."):
            # Run the RAG chain
            try:
                response = qa_chain.invoke({"query": user_query})
                st.subheader("🤖 AI Response")
                st.write(response["result"])
            except Exception as e:
                st.error(f"An error occurred during query: {e}")

# Footer for running the app
st.markdown("---")
st.markdown("Run this application using: `streamlit run app.py`")