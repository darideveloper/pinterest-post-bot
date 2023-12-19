import os
from time import sleep
from logs import logger
from dotenv import load_dotenv
from scraping.web_scraping import WebScraping
from libs.canva import Canva
from libs.images import crop_image
from libs.ad_generator import AdGenerator
from selenium.webdriver.common.keys import Keys

load_dotenv()
CHROME_FOLDER = os.getenv("CHROME_FOLDER")
WAIT_TIME = os.getenv("WAIT_TIME")
HEADLESS = os.getenv("HEADLESS") == "True"
AD_ID = int(os.getenv("AD_ID"))


class PinterestBot(WebScraping):

    def __init__(self, price_1: float, price_2: float, price_3: float,
                 price_4: float):
        """ Save general ads data

        Args:
            price_1 (float): lower price from scrape
            price_2 (float): 2nd lower price from scrape
            price_3 (float): 3rd lower price from scrape
            price_4 (float): 4th lower price from scrape
        """
        
        self.pages = {
            "home": "https://www.pinterest.com/",
            "post": "https://www.pinterest.com/pin-creation-tool/"
        }

        # Instance parent class
        super().__init__(
            headless=HEADLESS,
            chrome_folder=CHROME_FOLDER,
            start_killing=True
        )
        
        # Connect to canva
        self.canva = Canva(self)
        
        # Connect to ad generator
        self.ad_generator = AdGenerator(self)
        
        # Save lower prices
        self.price_1 = price_1
        self.price_2 = price_2
        self.price_3 = price_3
        self.price_4 = price_4

    def __login__(self):
        """ Open browser go to pinterest and validate session """

        logger.info("Validating session")

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

        # Show board options
        self.click(selectors["display_btn"])
        self.refresh_selenium()

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

    def post(self, image: str, title: str, description: str, link: str, board: str):
        """ Create a post in pinterest

        Args:
            image (str): Path to local image
            title (str): Title of post
            description (str): Description of post
            link (str): Link to post
            board (str): Name of board
            tags (list): List of tags
        """
        
        # remove bg from image with canva
        logger.info("\tremoving background from image...")
        crop_image(image)
        product_image = self.canva.remove_bg_image(image)
        
        # Fix image path for add generator
        image_image_name = product_image.split("\\")[-1]
        image_image_path = f"imgs/temp/{image_image_name}"
                
        # Generate data for add
        ad_data = {}
        if AD_ID == 1:
            ad_data["product_name"] = title
            ad_data["product_image"] = image_image_path
            ad_data["product_price_1"] = self.price_1
            ad_data["product_price_2"] = self.price_2
            ad_data["product_price_3"] = self.price_3
            ad_data["product_price_4"] = self.price_4
        
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
        self.refresh_selenium()
        
        # Upload image
        self.send_data(selectors["input_image"], ad_image)
        self.refresh_selenium()
     
        # Detect errors uploading image
        error = self.get_text(selectors["input_image_errror"])
        if error:
            logger.error(f"\tERROR: {error}")
            return

        # Write text data (title, description and link)
        self.send_data(selectors["input_title"], title)
        self.send_data(selectors["input_description"], description)
        self.send_data(selectors["link"], link)

        # select or create board
        self.__select_create_board__(board)
        
        # Submit post
        self.click_js(selectors["btn_done"])
        sleep(5)
        self.refresh_selenium()


if __name__ == "__main__":
    current_folder = os.path.dirname(__file__)
    media_folder = os.path.join(current_folder, "media")
    file_path = os.path.join(media_folder, "sample.webp")

    pinterest_bot = PinterestBot(
        price_1=2999.0,
        price_2=3999.0,
        price_3=4999.0,
        price_4=5999.0,
    )
    pinterest_bot.post(
        file_path,
        "test 1",
        "sample post",
        "https://www.pinterest.com/pin-creation-tool/",
        "price checker 2999",
    )
    print()
