import os
from time import sleep
from logs import logger
from dotenv import load_dotenv
from scraping.web_scraping import WebScraping

load_dotenv()
CHROME_FOLDER = os.getenv("CHROME_FOLDER")
WAIT_TIME = os.getenv("WAIT_TIME")
HEADLESS = os.getenv("HEADLESS") == "True"


class PinterestBot(WebScraping):

    def __init__(self):
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

        # Validate login
        self.__login__()

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
             board: str, tags: list):
        """ Create a post in pinterest

        Args:
            image (str): Path to local image
            title (str): Title of post
            description (str): Description of post
            link (str): Link to post
            board (str): Name of board
            tags (list): List of tags
        """
        
        logger.info(f"Posting {title}: {description}")

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
        self.send_data(selectors["input_image"], image)
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

        # select tags
        self.__select_tags__(tags)
        
        # Submit post
        self.click_js(selectors["btn_done"])
        sleep(5)
        self.refresh_selenium()


if __file__ == "__main__":
    current_folder = os.path.dirname(__file__)
    images_folder = os.path.join(current_folder, "images")
    file_path = os.path.join(images_folder, "sample.jpeg")

    pinterest_bot = PinterestBot()
    pinterest_bot.post(
        file_path,
        "test 1",
        "sample post",
        "https://www.pinterest.com/pin-creation-tool/",
        "price checker 2999",
        ["sample", "audio"]
    )
    print()
