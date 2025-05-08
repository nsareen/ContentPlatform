"""
Script to start the backend server with proper environment variable loading
"""
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Verify OpenAI API key is loaded
api_key = os.environ.get("OPENAI_API_KEY")
if api_key:
    print(f"OpenAI API key loaded successfully: {api_key[:5]}...")
else:
    print("WARNING: OpenAI API key not found in environment variables")

# Start the server
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
