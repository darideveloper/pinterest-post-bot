import os
import sys
import csv
from time import sleep
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
load_dotenv()

# Add parent folder to path
current_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(current_folder)
sys.path.append(parent_folder)

from scraping.web_scraping import WebScraping
from logs import logger

AD_ID = int(os.getenv("AD_ID"))


class Canva ():
    
    def __init__(self, scraper: WebScraping):
        """ Constructor """
        
        self.scraper = scraper
        self.pages = {
            "home": "https://www.canva.com/",
        }
        self.media_folder = os.path.join(parent_folder, "media")
        
        # Get current ad link
        csv_path = os.path.join(parent_folder, "ads.csv")
        with open(csv_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            ads_links = list(reader)
        
        self.ad_link = None
        for id, ad_link in ads_links:
            if id == str(AD_ID):
                self.ad_link = ad_link
                break
        
        # Validate ad link
        if not self.ad_link:
            logger.error(f"\tERROR: Ad with id {AD_ID} not found in ads.csv file")
            quit()
            
        # Organize add functions
        ad_functions = [
            self.create_ad_1,
        ]
        
        # Validate ad id
        ads_function_len = len(ad_functions)
        if AD_ID > ads_function_len:
            logger.error(f"\tERROR: Only {ads_function_len} ads are available")
            quit()
        
        print()
        
    def __validate_login__(self):
        """ Validate if user is logged in """
        
        selectors = {
            "login_btn": 'header > .PYoGFg.DwB3TQ button:last-child',
        }
        
        login_text = self.scraper.get_text(selectors["login_btn"])
        if login_text and login_text.lower().strip() == "log in":
            logger.error("\tERROR: You should login manually to canva")
            quit()
        
    def remove_bg_image(self, image_path: str) -> str:
        """ Remove background image from canva
        
        Args:
            image_path (str): Path of image to remove background
            
        Returns:
            str: Path of image without background
        """
        
        selectors = {
            "new_btn": 'header > div:nth-child(7) [type="button"]',
            'input_image': '[type="file"]',
            'remove_bg_btn': 'button._6RLMEQ',
            'save_btn': 'button.zKTE_w',
            'download_btn': '.x6XCCg > button:last-child'
        }
        
        # Go to canva home page
        self.scraper.set_page(self.pages["home"])
        self.scraper.refresh_selenium()
        
        # Validate login
        self.__validate_login__()
        
        # Upload image
        self.scraper.click_js(selectors["new_btn"])
        self.scraper.refresh_selenium()
        self.scraper.send_data(selectors["input_image"], image_path)
        sleep(5)
        self.scraper.refresh_selenium()
        
        # Remove background
        self.scraper.click_js(selectors["remove_bg_btn"])
        sleep(5)
        self.scraper.refresh_selenium()
        
        # Download image
        old_media = os.listdir(self.media_folder)
        self.scraper.click_js(selectors["save_btn"])
        self.scraper.refresh_selenium()
        self.scraper.click_js(selectors["download_btn"])
        sleep(3)
        new_media = os.listdir(self.media_folder)
        
        # Detect new image
        new_image = list(set(new_media) - set(old_media))[0]
        image_path = os.path.join(self.media_folder, new_image)
        return image_path
    
    
if __name__ == "__main__":
    media_folder = os.path.join(parent_folder, "media")
    scraper = WebScraping(
        start_killing=True,
        chrome_folder="C:\\Users\\herna\\AppData\\Local\\Google\\Chrome\\User Data",
        download_folder=media_folder
    )
    canva = Canva(scraper)
    image_path = os.path.join(media_folder, "sample.webp")
    
    # Remove background
    new_image = canva.remove_bg_image(image_path)