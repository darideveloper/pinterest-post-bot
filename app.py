import os
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
from pinterest_bot import PinterestBot
from threading import Thread
from tools import download_image

# Read settings
load_dotenv()
PORT = int(os.environ.get('PORT', 5001))

# Start flask
app = Flask(__name__)
CORS(app)

# Start bot
bot = PinterestBot()


@app.get("/")
def index():
    return {
        "status": "success",
        "message": "service running",
        "data": []
    }
    
    
@app.post("/")
def create_pinterest_post():
    
    # Get json post data
    data = request.json
    
    return {
        "status": "success",
        "message": "post created",
        "data": data
    }


if __name__ == "__main__":
    app.run(port=PORT)