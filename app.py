import os
from time import sleep
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
from pinterest_bot import PinterestBot
from threading import Thread
from tools import download_image

# Read settings
load_dotenv()
PORT = int(os.environ.get('PORT', 5001))
WAIT_TIME_POST = int(os.environ.get('WAIT_TIME_POST', 10))

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
        
        # Generate pin/post title
        keyword = post["keyword"]
        title = f"Price Comparison {keyword}!"
        
        # Generate pin description TODO: generate with ai
        description = post["title"]
        
        # previee page link
        link = post["url"].replace(
            "http://localhost:5000",
            "https://www.price-checker.us"
        )
        
        # board name
        board = title
        
        # tags list TODO: generate with ai
        tags = ["iphone", "Smartphone"]
        
        # create post
        bot.post(
            image_path,
            title,
            description,
            link,
            board,
            tags
        )
        
        # Delete post image
        os.remove(image_path)
        
        # Wait before next post
        sleep(WAIT_TIME_POST)


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