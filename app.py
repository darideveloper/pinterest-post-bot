import os
import random
from time import sleep
from flask import Flask, request, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from pinterest_bot import PinterestBot
from threading import Thread
from libs.images import download_image
from libs.chatgpt import get_tags_description
from logs import logger
from libs.images import delete_temp_images

# Read settings
load_dotenv()
PORT = int(os.environ.get('PORT', 5001))
WAIT_TIME_POST = int(os.environ.get('WAIT_TIME_POST', 10))
USE_REFERRAL_LINK = os.environ.get('USE_REFERRAL_LINK') == "True"

# Start flask
app = Flask(__name__)
CORS(app)

# Paths
current_folder = os.path.dirname(__file__)
imgs_folder = os.path.join(current_folder, "static", "imgs")


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
    
    post_ordinals = {
        2: "2nd",
        3: "3rd",
        21: "21st",
        22: "22nd",
        23: "23rd",
        31: "31st",
        32: "32nd",
        33: "33rd",
    }
    
    for post in post_data:
        
        # Get post prefix
        post_id = post_data.index(post) + 1
        if post_id == 1:
            prefix = "Cheaper"
        elif post_id in post_ordinals.keys():
            prefix = post_ordinals[post_id]
        else:
            prefix = str(post_id) + "th"
        
        # Get post data
        index = post_data.index(post) + 1
        max_post = len(post_data)
        logger.info(f"Posting {index} / {max_post}")
        keyword = post["keyword"]
        
        description = get_tags_description(
            keyword,
            post["title"],
            post["price"],
            post["rate_num"],
            post["reviews"],
            post["store"],
            post["best_seller"],
            post["url"],
        )
        
        # Download product image
        post_image = post["image"]
        image_path = download_image(post_image, keyword)
        
        # Generate pin/post title
        keyword = post["keyword"].upper()
        
        # previee page link
        link_price_checker = post["url"].replace(
            "http://localhost:5000",
            "https://www.price-checker.us"
        ).replace(
            "http://127.0.0.1:5000",
            "https://www.price-checker.us"
        )
        
        link_price_checker += f"?product={post['title']}"
        link_store = post["link"]
        
        # create post
        bot.post(
            image=image_path,
            title=keyword,
            description=description,
            link=link_store if USE_REFERRAL_LINK else link_price_checker,
            board=keyword,
            price=post["price"],
            prefix=prefix
        )
        
        # Wait before next post
        sleep(WAIT_TIME_POST)
        
        # Delete all images in temp folder
        delete_temp_images()
                

def show_start_message():
    """ Show start message """
    
    sleep(3)
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


@app.get("/ad-1")
def ad_1():
    
    # Get random bg image
    imgs_folder_ad = os.path.join(imgs_folder, "ad-1")
    images = os.listdir(imgs_folder_ad)
    bg_image = random.choice(images)
    
    # Remove folder before "static" in image path
    bg_image_path = f"/imgs/ad-1/{bg_image}"
    
    # Get GET params
    product_name = request.args.get("product-name")
    product_image = request.args.get("product-image")
    product_price = request.args.get("product-price")
    product_price_prefix = request.args.get("product-price-prefix")
    product_price_2 = request.args.get("product-price-2")
    product_price_3 = request.args.get("product-price-3")
    product_price_4 = request.args.get("product-price-4")
    
    # Retun html template
    return render_template(
        "ad-1.html",
        bg_image=bg_image_path,
        ad_num=1,
        product_name=product_name,
        product_image=product_image,
        product_price=product_price,
        product_price_prefix=product_price_prefix,
        product_price_2=product_price_2,
        product_price_3=product_price_3,
        product_price_4=product_price_4,
    )


if __name__ == "__main__":
    
    # Create thread for show start message
    thread_obj = Thread(target=show_start_message)
    thread_obj.start()
    
    app.run(port=PORT, debug=True)