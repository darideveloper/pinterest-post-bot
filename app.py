import os
from time import sleep
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
from pinterest_bot import PinterestBot
from threading import Thread
from libs.images import download_image
from libs.chatgpt import get_tags_description
from logs import logger

# Read settings
load_dotenv()
PORT = int(os.environ.get('PORT', 5001))
WAIT_TIME_POST = int(os.environ.get('WAIT_TIME_POST', 10))

# Start flask
app = Flask(__name__)
CORS(app)


def create_posts(post_data: list):
    """ Create each pinterest post

    Args:
        post_data (list): List of post dicts
    """
    
    # Get 4 lower prices
    lower_prices = post_data[:4]
    price_1 = lower_prices[0]["price"]
    price_2 = lower_prices[1]["price"]
    price_3 = lower_prices[2]["price"]
    price_4 = lower_prices[3]["price"]
    
    # Start bot
    bot = PinterestBot(
        price_1,
        price_2,
        price_3,
        price_4,
    )
    
    for post in post_data:
        
        index = post_data.index(post) + 1
        max_post = len(post_data)
        logger.info(f"Posting {index} / {max_post}")
        
        tags, description = get_tags_description(
            post["keyword"],
            post["title"],
            post["price"],
            post["rate_num"],
            post["reviews"],
            post["store"],
            post["best_seller"],
            post["url"]
        )
        
        # Download product image
        post_image = post["image"]
        image_path = download_image(post_image)
        
        # Generate pin/post title
        keyword = post["keyword"]
        title = keyword.title()
        
        # previee page link
        link = post["url"].replace(
            "http://localhost:5000",
            "https://www.price-checker.us"
        )
        
        # board name
        board = title
        
        # create post
        bot.post(
            image_path,
            title,
            description,
            link,
            board,
            tags,
        )
        
        # Delete post image
        os.remove(image_path)
        
        # Wait before next post
        sleep(WAIT_TIME_POST)


def show_start_message():
    """ Show start message """
    
    sleep(5)
    logger.info("**BOT READY TO CREATE POSTS**")


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
    
    # Create thread for show start message
    thread_obj = Thread(target=show_start_message)
    thread_obj.start()
    
    app.run(port=PORT)