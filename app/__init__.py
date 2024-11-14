import os
import time
import json
from flask import Flask
from flask_cors import CORS
import enum
from dotenv import load_dotenv
import logging
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, Literal
from chatbot.rag import create_faq_chroma_db

current_dir = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(current_dir, "../chroma/fina3001_faq_db")
upper_dir = os.path.join(current_dir, "..")

# Load environment variables from .env file
load_dotenv()

# App mode enum to handle different configurations
class AppMode(enum.Enum):
    PRODUCTION = "production"  # For production mode
    DEBUG = "debug"            # For development mode with reloading and debug info
    TEST = "test"              # For running tests

# Create the Flask application
def create_app(mode: AppMode = AppMode.PRODUCTION):
    # Initialize the Flask app
    app = Flask(__name__)
    
    # Enable Cross-Origin Resource Sharing (CORS)
    CORS(app)

    # Configure app mode
    if mode == AppMode.DEBUG:
        app.debug = True
    elif mode == AppMode.TEST:
        app.config['TESTING'] = True

    # Setup logging
    setup_logging()
    logger = logging.getLogger("flask-app")

    # Setup chroma db
    if os.getpid() == 2:
        setup_chroma_db()

    # Register your Blueprints here
    from .routes import bot_invoke
    app.register_blueprint(bot_invoke, url_prefix='/bot-invoke')

    # Basic route example
    @app.route('/')
    def index():
        return "Hi! The server is healthy."

    return app

# Setup logging function
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger("flask-app")
    
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log.setLevel(log_level)

    log.info("Logging is configured at the %s level.", log_level)

def setup_chroma_db():
    with open(os.path.join(upper_dir, "chatbot", "FAQ.json"), 'r', encoding='utf-8') as file:
        faq_data = json.load(file)
    create_faq_chroma_db(faq_data)