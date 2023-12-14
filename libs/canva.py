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
            
    def __insert_innerhtml__(self, selector, inner_html):
        """ Insert inner html in element
        
        Args:
            selector (str): Selector of element
            inner_html (str): Inner html to insert
        """
        
        script = f"""document.querySelector ('{selector}').innerHTML = `{inner_html}`"""
        self.scraper.driver.execute_script(script)
    
    def __select_layer__(self, layer_index: int):
        """ Select specific layer in canva aside

        Args:
            layer_index (int): Index of layer to select
        """
        
        selector_show_layers = 'main div:nth-child(1) button'
        selector_layer = f'div:nth-child({layer_index}) > div:nth-child(3) button'
        
        self.scraper.click_js(selector_show_layers)
        self.scraper.refresh_selenium()
        self.scraper.click_js(selector_layer)
        self.scraper.refresh_selenium()
        
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
    
    def create_ad_1(self, title: str, price_1: float,
                    price_2: float, price_3: float, price_4: float,
                    image_path: str) -> str:
        """ Replace data in add template 1, and download image
        
        Args:
            title (str): Title of add
            price_1 (float): Cheaper price
            price_2 (float): 2nd cheaper price
            price_3 (float): 3rd cheaper price
            price_4 (float): 4th cheaper price
            image_path (str): Path of image to upload
            
        Returns:
            str: Path of video downloaded
        """
        
        selectors = {
            # ad texts
            "title": 'div:nth-child(9) p.cgHgbA',
            "price_1": 'div:nth-child(8) p',
            "price_2": 'div:nth-child(5) p.cgHgbA',
            "price_3": 'div:nth-child(5) p.cgHgbA:nth-child(2)',
            "price_4": 'div:nth-child(5) p.cgHgbA:nth-child(3)',
            
            # Ad image
            'delete_btn': 'div.awStMQ div:nth-child(2) > button',
            'files_tab': 'aside div:nth-child(6) > button',
            'input_image': 'input[type="file"]',
            'insert_image_btn': 'div.x6XCCg div:nth-child(2) '
                                '> div.D_ZUcw div[role="button"]',
            
            # scale and position image
            'draw_tab': 'div:nth-child(7) > button',
            'organize_tab': 'div.gezMZQ button.zCtFuA',
            'lock_relation_btn': 'div.Ey7S7w button',
            'height_input': 'div.Ey7S7w > div:nth-child(2) input',
            'center_x_btn': 'div:nth-child(3) > ul > li:nth-child(4) > button',
            'center_y_btn': 'div:nth-child(3) > ul > li:nth-child(3) > button',
            
            # Download ad
            'share_btn': 'header div.g3Pdkg button',
            'download_btn': 'div.Q0yqLQ li > button',
            'confirm_download_btn': 'div.v8cAAw button',
        }
        
        self.scraper.set_page(self.ad_link)
        self.scraper.refresh_selenium()
        
        # Replace titlle
        html = f"""<span class="OYPEnA" style="font-weight: 400; font-style: normal;
                color: rgb(82, 113, 255); text-decoration: none;">{title}</span>"""
        self.__insert_innerhtml__(selectors['title'], html)
        sleep(2)
        
        # Replace cheaper price
        html = f"""<span class="OYPEnA" style="font-weight: 400; font-style: normal;
               color: rgb(54, 48, 98); text-decoration: none;">Cheaper: </span><span
               class="OYPEnA" style="font-weight: 400; font-style: normal; color:
               rgb(82, 113, 255); text-decoration: none;">US ${price_1}</span>"""
        self.__insert_innerhtml__(selectors['price_1'], html)
        sleep(2)

        # Replace 2nd, 3rd and 4th cheaper prices
        seconday_prices = [
            ["2nd", price_2, selectors['price_2']],
            ["3rd", price_3, selectors['price_3']],
            ["4th", price_4, selectors['price_4']],
        ]
        
        for secondary_price in seconday_prices:
            position, price, selector = secondary_price
        
            # Replace price
            html = f"""<span class="OYPEnA" style="font-weight: 400; font-style: normal;
            color: rgb(54, 48, 98); text-decoration: none;">{position} place: </span>
            <span class="OYPEnA" style="font-weight: 400; font-style: normal; color:
            rgb(82, 113, 255); text-decoration: none;">US ${price}</span>"""
            self.__insert_innerhtml__(selector, html)
            sleep(2)
        
        # Delete image
        self.__select_layer__(5)
        self.scraper.click_js(selectors["delete_btn"])
        self.scraper.refresh_selenium()
        
        # Move to files tab
        self.scraper.click_js(selectors["files_tab"])
        self.scraper.refresh_selenium()
        
        # Upload new image
        self.scraper.send_data(selectors["input_image"], image_path)
        sleep(10)
        self.scraper.refresh_selenium()
        self.scraper.click_js(selectors["insert_image_btn"])
        sleep(1)
        
        # Deselect image going to draw tab
        self.scraper.click_js(selectors["draw_tab"])
        self.scraper.refresh_selenium()
        
        # Scale image
        self.__select_layer__(5)
        self.scraper.click_js(selectors["organize_tab"])
        self.scraper.refresh_selenium()
        self.scraper.click_js(selectors["lock_relation_btn"])
        for _ in range(7):
            self.scraper.send_data(selectors["height_input"], Keys.BACKSPACE)
        self.scraper.send_data(selectors["height_input"], "790")
        self.scraper.send_data(selectors["height_input"], Keys.ENTER)
        
        # Center image
        self.scraper.click_js(selectors["center_x_btn"])
        self.scraper.click_js(selectors["center_y_btn"])
        
        # Download image
        old_media = os.listdir(self.media_folder)
        self.scraper.click_js(selectors["share_btn"])
        self.scraper.refresh_selenium()
        self.scraper.click_js(selectors["download_btn"])
        self.scraper.refresh_selenium()
        self.scraper.click_js(selectors["confirm_download_btn"])
        
        # Wait for download ad
        for _ in range(10):
            new_media = os.listdir(self.media_folder)
            new_video = list(set(new_media) - set(old_media))
            if new_video:
                break
            else:
                sleep(5)
            
        # Validate if ad was downloaded
        if not new_video:
            return None
                
        # Return ad path
        video_path = os.path.join(self.media_folder, new_video[0])
        return video_path


if __name__ == "__main__":
    media_folder = os.path.join(parent_folder, "media")
    scraper = WebScraping(
        start_killing=True,
        chrome_folder="C:\\Users\\herna\\AppData\\Local\\Google\\Chrome\\User Data",
        download_folder=media_folder
    )
    canva = Canva(scraper)
    image_path = os.path.join(media_folder, "sample.webp")
    
    canva.create_ad_1(
        title="Sample title",
        price_1=1.99,
        price_2=2.99,
        price_3=3.99,
        price_4=4.99,
        image_path=image_path,
    )