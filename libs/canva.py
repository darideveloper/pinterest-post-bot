import os
import sys
from time import sleep
from dotenv import load_dotenv
load_dotenv()

# Add parent folder to path
current_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(current_folder)
imgs_folder = os.path.join(parent_folder, "static", "imgs", "temp")
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
        
        self.__validate_login__()
        
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
        old_imgs = os.listdir(imgs_folder)
        self.scraper.click_js(selectors["save_btn"])
        self.scraper.refresh_selenium()
        self.scraper.click_js(selectors["download_btn"])
        sleep(3)
        new_imgs = os.listdir(imgs_folder)
        
        # Detect new image
        new_image = list(set(new_imgs) - set(old_imgs))[0]
        image_path = os.path.join(imgs_folder, new_image)
        return image_path
    
    
if __name__ == "__main__":
    scraper = WebScraping(
        start_killing=True,
        chrome_folder="C:\\Users\\herna\\AppData\\Local\\Google\\Chrome\\User Data",
        download_folder=imgs_folder
    )
    canva = Canva(scraper)
    image_path = os.path.join(imgs_folder, "sample.png")
    
    # Remove background
    new_image = canva.remove_bg_image(image_path)