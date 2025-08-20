import os

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:7b")

MAX_WORKERS = 3
AGENT_TIMEOUT = 120

MAX_FILE_SIZE = 1024 * 1024
ALLOWED_EXTENSIONS = {'.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.ts'}
MAX_FILES_PER_UPLOAD = 50

DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
