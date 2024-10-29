from quart import Blueprint, request, jsonify
import json
import time
import os
import asyncio
import logging
from chatbot.bot import invoke_bot

# Retrieve the logger that was created in the __init__.py
logger = logging.getLogger("flask-app")

# Create a Blueprint for the chatbot invoking routes
bot_invoke = Blueprint('bot-invoke', __name__)

@bot_invoke.route('/invoke', methods=['POST'])
def invoke():
    try:
        # Extract user query from the request body
        data = request.get_json()
        user_query = data.get('query')  # Expecting a 'query' field in the JSON body
        
        if not user_query:
            raise ValueError("The 'query' field is required.")
        
        # Call the invoke_bot method with the user query
        bot_message = invoke_bot(user_query=user_query)
        
        # Return the bot message as a JSON response
        return jsonify({"message": bot_message}), 200
    
    except Exception as e:
        logger.error(f"Error in invoke_bot: {str(e)}")  # Log error from invoke_bot
        return jsonify({"error": str(e)}), 400  # Return the error message as JSON with a 400 status code

