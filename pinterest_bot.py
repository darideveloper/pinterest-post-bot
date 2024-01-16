import os
from time import sleep
from logs import logger
from datetime import datetime
from dotenv import load_dotenv
from scraping.web_scraping import WebScraping
from libs.canva import Canva, imgs_folder
from libs.images import crop_image
from libs.ad_generator import AdGenerator
from selenium.webdriver.common.keys import Keys
from libs.images import download_image
from libs.chatgpt import get_description
from libs.images import delete_temp_images

load_dotenv()
CHROME_FOLDER = os.getenv("CHROME_FOLDER")
WAIT_TIME = os.getenv("WAIT_TIME")
HEADLESS = os.getenv("HEADLESS") == "True"
AD_ID = int(os.getenv("AD_ID"))
USE_REFERRAL_LINK = os.environ.get('USE_REFERRAL_LINK') == "True"
WAIT_TIME_POST = int(os.environ.get('WAIT_TIME_POST', 10))
DEBUG = os.environ.get('DEBUG') == "True"


class PinterestBot(WebScraping):

    def __init__(self):
        """ Initialize bot
        """
        
        self.pages = {
            "home": "https://www.pinterest.com/",
            "post": "https://www.pinterest.com/pin-creation-tool/"
        }

        # Instance parent class
        super().__init__(
            headless=HEADLESS,
            chrome_folder=CHROME_FOLDER,
            start_killing=True,
            download_folder=imgs_folder
        )
        
        # Connect to canva
        self.canva = Canva(self)
        
        # Connect to ad generator
        self.ad_generator = AdGenerator(self)
        
        # Save lower prices
        self.price_1 = 0
        self.price_2 = 0
        self.price_3 = 0
        self.price_4 = 0

    def __login__(self):
        """ Open browser go to pinterest and validate session """

        selectors = {
            "login_btn": '.red.SignupButton.active, button[tabindex="0"]'
        }

        self.set_page(self.pages["home"])
        self.refresh_selenium()
        login_text = self.get_text(selectors["login_btn"])
        if str(login_text).lower().strip() == "log in":
            logger.error("ERROR: You should login manually to pinterest")
            quit()

    def __select_create_board__(self, board: str):
        """ Select a board or create a new board for the post

        Args:
            board (str): Name of board
        """

        selectors = {
            "display_btn": '[data-test-id="board-dropdown-select-button"]',
            "search_bar": '#pickerSearchField',
            "result": '[data-test-id="boardWithoutSection"] [role="button"]',
            "new_board_btn": '[aria-label="Popover"] [role="button"]',
            "crate_board_btn": '[aria-label="Board form"] button',
        }
        
        # Add current date to board
        today = datetime.now().strftime("%Y-%m-%d")
        board += f" {today}"

        # Show board options
        self.click(selectors["display_btn"])
        self.refresh_selenium(time_units=2)

        # Query board name
        self.send_data(selectors["search_bar"], board)

        # Select first result (if exists)
        result = self.get_elems(selectors["result"])
        if result:
            self.click_js(selectors["result"])
        else:
            # Create new board
            self.click_js(selectors["new_board_btn"])
            self.refresh_selenium()
            self.click_js(selectors["crate_board_btn"])
            self.refresh_selenium()

    def __select_tags__(self, tags: list):
        """ Select each tag in the list

        Args:
            tags (list): List of tags
        """

        selectors = {
            "input": '#storyboard-selector-interest-tags',
            "result": '[aria-label="Popover"] [role="button"]'
        }

        for tag in tags:
            
            # Delete olf characters
            for _ in range(10):
                self.send_data(selectors["input"], Keys.BACKSPACE)
                sleep(0.1)
            
            # send only first 7 chars
            tag_small = tag[:7]
            for char in tag_small:
                self.send_data(selectors["input"], char)
                sleep(0.1)
            self.refresh_selenium(2)
            
            # Select first tag
            try:
                self.click_js(selectors["result"])
            except Exception:
                logger.error(f"\tERROR: Tag '{tag}' not found")
            self.refresh_selenium()

    def post(self, image: str, title: str, description: str, link: str,
             board: str, price: float, prefix: str):
        """ Create a single post in pinterest

        Args:
            image (str): Path to local image
            title (str): Title of post
            description (str): Description of post
            link (str): Link to post
            board (str): Name of board
            price (float): Price of product
            prefix (str): Prefix of price (like Cheaper or 2nd)
        """
        
        # crop image
        logger.info("\tremoving background from image...")
        cropped = crop_image(image)
        if not cropped:
            logger.error("\tERROR: Image not cropped, skipping post...")
            return
        
        # Remove background
        product_image = self.canva.remove_bg_image(image)
        if not product_image:
            logger.error("\tERROR: Image not removed background, skipping post...")
            return
        
        # Fix image path for add generator
        image_name = product_image.split("\\")[-1]
        image_path = f"imgs/temp/{image_name}"
                
        # Generate data for add
        ad_data = {}
        if AD_ID == 1:
            ad_data["product_name"] = title
            ad_data["product_image"] = image_path
            ad_data["product_price_prefix"] = prefix
            ad_data["product_price"] = price
            ad_data["product_price_2"] = self.price_2
            ad_data["product_price_3"] = self.price_3
            ad_data["product_price_4"] = self.price_4
            ad_data["image_name"] = image_name
        
        # Create ad
        logger.info("\tcreating ad...")
        ad_image = self.ad_generator.create_ad_1(AD_ID, ad_data)
        crop_image(ad_image)
                
        # Validate login
        self.__login__()

        selectors = {
            "input_image": '#storyboard-upload-input',
            "input_image_errror": '[data-test-id="drag-behavior-container"] '
                                  '[style="max-width: 220px;"]',
            "input_title": '#storyboard-selector-title',
            "input_description": '.notranslate.public-DraftEditor-content',
            "link": '#WebsiteField',
            "btn_done": '[data-test-id="storyboard-creation-nav-done"] > button'
        }

        # Load page
        self.set_page(self.pages["post"])
        self.refresh_selenium(time_units=3)
        
        # Upload image
        try:
            self.send_data(selectors["input_image"], ad_image)
        except Exception:
            logger.error("\tERROR: Error uploading image (input not found), skipped...")
            return
        self.refresh_selenium()
     
        # Detect errors uploading image
        error = self.get_text(selectors["input_image_errror"])
        if error:
            logger.error(f"\tERROR: {error}")
            return

        # Write text data (title, description and link)
        try:
            self.send_data(selectors["input_title"], title)
            self.send_data(selectors["input_description"], description)
            self.send_data(selectors["link"], link)
        except Exception:
            logger.debug(f"\ttitle: {title}")
            logger.debug(f"\tdescription: {description}")
            logger.debug(f"\tlink: {link}")
            logger.error("\tERROR: Error writing text data, skipped...")
            return

        # select or create board
        self.__select_create_board__(board)
        
        # Submit post
        if DEBUG:
            logger.info("\tDEBUG: Post not submitted (DEBUG mode)")
        else:
            self.click_js(selectors["btn_done"])
            sleep(5)
            self.refresh_selenium()
            
    def posts(self, post_data: list):
        """ Create each pinterest post

        Args:
            post_data (list): List of post dicts
        """
        
        # Get 4 lower prices
        lower_prices = post_data[:4]
        self.price_1 = lower_prices[0]["price"]
        self.price_2 = lower_prices[1]["price"]
        self.price_3 = lower_prices[2]["price"]
        self.price_4 = lower_prices[3]["price"]
        
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
            keyword = post["keyword"].title()
            
            description = get_description(
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
            
            # previee page link
            link_price_checker = post["url"].replace(
                "http://localhost:5000",
                "https://www.price-checker.us"
            ).replace(
                "http://127.0.0.1:5000",
                "https://www.price-checker.us"
            )
            
            link_price_checker += f"?product={keyword}"
            link_store = post["link"]
            
            # create post
            self.post(
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