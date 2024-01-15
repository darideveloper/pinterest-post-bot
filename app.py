import os
import random
from time import sleep
from flask import Flask, request, render_template
from dotenv import load_dotenv
from flask_cors import CORS
from pinterest_bot import PinterestBot
from threading import Thread
from logs import logger
from libs.price_checker import get_products_data

# Read settings
load_dotenv()
PORT = int(os.environ.get('PORT', 5001))
USE_IDS_FILE = os.environ.get('USE_IDS_FILE') == "True"

# Start flask
app = Flask(__name__)
CORS(app)

# Paths
current_folder = os.path.dirname(__file__)
imgs_folder = os.path.join(current_folder, "static", "imgs")
ids_file = os.path.join(current_folder, "ids.txt")

# Start pinterest bot
pinterest_bot = PinterestBot()


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
    thread_obj = Thread(target=pinterest_bot.posts, args=(data,))
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
    
    # Start app in background
    thread_obj = Thread(target=app.run, kwargs={"port": PORT})
    thread_obj.start()
        
    if USE_IDS_FILE:
        logger.info(">>> WORKING WITH IDS FILE")
        
        # Loop ids from csv file
        with open(ids_file, "r") as file:
            ids = file.readlines()
        
        for id in ids:
            
            id = int(id.strip())
            logger.info(f"\n> Posting id: {id}")
            
            # Get data from price checker api
            data = get_products_data(id)
            
            # Run bot
            pinterest_bot.posts(data)
        
    else:
        logger.info(">>> WORKING WITH BOOM BUTTON")
    
        # Show start message
        sleep(3)
        logger.info("**BOT READY TO CREATE POSTS**")