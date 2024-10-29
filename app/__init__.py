import os
import time
from flask import Flask
from flask_cors import CORS
import enum
from dotenv import load_dotenv
import logging
from langchain.pydantic_v1 import BaseModel, Field
from typing import Optional, Literal
from chatbot.rag import load_faq_json_from_chroma_path, create_faq_chroma_db

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
    faq_data = load_faq_json_from_chroma_path()
    if faq_data:
        create_faq_chroma_db(faq_data)
    else:
        logger.info("Fail to load and create chroma db.")

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