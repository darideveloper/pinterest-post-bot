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


def create_posts(post_data: list):
    """ Create each pinterest post

    Args:
        post_data (list): List of post dicts
    """
    
    for post in post_data:
        
        # Download product image
        post_image = post["image"]
        image_path = download_image(post_image)
        
        # 


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
    
    # Create post in background
    thread_obj = Thread(target=create_posts, args=(data,))
    thread_obj.start()
    
    return {
        "status": "success",
        "message": "post created",
        "data": data
    }


if __name__ == "__main__":
    app.run(port=PORT)