import os
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
COLLECTION_NAME = "pdf_documents"