import os
import sys

# Add parent folder to path
current_folder = os.path.dirname(__file__)
parent_folder = os.path.dirname(current_folder)
sys.path.append(parent_folder)

from scraping.web_scraping import WebScraping


class AdGenerator ():

    def __init__(self, scraper: WebScraping):
        self.scraper = scraper

    def create_ad_1(self, ad_id: int, ad_data: dict) -> str:
        """ Generate ad 1 for pinterest
        
        Args:
            ad_id (int): Id of ad
            ad_data (dict): Dict with ad data
                add 1:
                    product_name (str): Name of product
                    product_image (str): Image of product
                    product_price_prefix (str): Prefix of price (like Cheaper or 2nd)
                    product_price (float): Price of product
                    product_price_2 (float): Price of product
                    product_price_3 (float): Price of product
                    product_price_4 (float): Price of product
        
        Returns:
            str: Path of ad image
        """
        
        # Load ad page
        if ad_id == 1:
            ad_page = f"http://localhost:5001/ad-{ad_id}" \
                f"?product-name={ad_data['product_name']}" \
                f"&product-image={ad_data['product_image']}" \
                f"&product-price-prefix={ad_data['product_price_prefix']}" \
                f"&product-price={ad_data['product_price']}" \
                f"&product-price-2={ad_data['product_price_2']}" \
                f"&product-price-3={ad_data['product_price_3']}" \
                f"&product-price-4={ad_data['product_price_4']}"
                
            self.scraper.set_page(ad_page)
            self.scraper.refresh_selenium()
            
        # Take screenshot
        current_folder = os.path.dirname(__file__)
        parent_folder = os.path.dirname(current_folder)
        static_folder = os.path.join(parent_folder, "static", "imgs", "temp")
        file_path = os.path.join(static_folder, ad_data["image_name"])
        self.scraper.screenshot(file_path)
        
        return file_path
    
    
if __name__ == "__main__":
    ad_generator = AdGenerator(WebScraping())
    ad_data = {
        "product_name": "Product name",
        "product_image": "https://picsum.photos/200",
        "product_price_prefix": "Cheaper",
        "product_price": "100",
        "product_price_2": "200",
        "product_price_3": "300",
        "product_price_4": "400",
    }
    ad_path = ad_generator.create_ad_1(1, ad_data)
    print(ad_path)