import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

API_KEY_OPENAI = os.getenv("API_KEY_OPENAI")


def get_tags_description(keyword: str, title: str, price: float, rate_number: int,
                         reviews_number: int, store: str, best_seller: bool,
                         store_url: str) -> tuple:
    """ Generate description and keyword for specific product
    
    Args:
        keyword (str): Keyword that led to the selection of said product
        title (str): Title of the product
        price (float): Price
        rate_number (int): Rate number
        reviews_number (int): Reviews number
        store (str): Seller
        best_seller (bool): Bestseller
        store_url (str): Seller URL
        
    Returns:
        tuple: (description: str, tags: list)
    """

    client = OpenAI(
        # This is the default and can be omitted
        api_key=API_KEY_OPENAI
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f""" Aim:
                1.- Generate the related keywords, hashtags, and description necessary so that a Pinterest pin, in my Pinterest account "Price Checker US" has the best chance of positioning itself in the Pinterest and Google search engines and consequently being more visible to the public. public.
                2.- Persuade the pin viewer to click on the only link in said pin either to review the comparison or to purchase the item.

                Context or Inputs:
                1.- The Pinterest account "Price Checker US" promotes my price comparison tool, with the same name, and main Internet page: https://www.price-checker.us/", comparisons that are made between the products from the Amazon, eBay, and Walmart platforms based on a keyword entered by the user of my Price Checker US tool.
                2.- The pins that will be generated will be about products of any category that come from both the Amazon, eBay, and Walmart platforms.
                3.- The informative data we have about said products is the following: Keyword that led to the selection of said product, Title of the product, Price, Rate number, Number of reviews, Seller, and the information of whether it is a Best Seller when so be and the URL of the seller who sells it.
                4.- The audience is regular Pinterest users in the United States of America.
                5.- The theme originates from the Keyword, the Product Title, and the rest of the product data that I provide below in brackets:

                {{
                    keyword: {keyword}
                    Title: {title}
                    Price: {price} USD
                    Rate number: {rate_number}
                    Reviews number: {reviews_number}
                    Seller: {store}
                    Bestseller: {best_seller}
                    Seller URL: {store_url}
                }}

                Details of Tasks:
                1.- Please carry out a search based on the "keyword" in the search engines of Google, Pinterest, and the seller's URL. Based on this search, establish between 3 and 7 related keywords, and between 3 and 7 hashtags, but do not present them to me in your response but store them so that with them you generate the point "2.-". Both related keywords and hashtags should only be those strictly attached to the intention of the pin viewer, which is always: to find the best offer and buy the product.
                2.- Once the elements of point "1.-" have been determined, make a description in the English language of the USA, optimized for SEO, of no less than 400 and no more than 500 characters, in a colloquial and at the same time persuasive tone that induces the viewer of the pin to click on the link either to review the comparison or to purchase the item. Integrate as many related keywords into this description as the syntax allows without losing coherence. After the description, in a continuous paragraph paste all the between 3 and 7 hashtags one after the other, only separated by a space. Take as long as necessary.
                3.- Only present to me the elements of point "2.-".
                    
                Be sure that the response description including tags is not longer than 500 characters
                
                Return the respnse in json with the keys: "keywords", and "description". Be sure to don't add the keyword to the description.
                """
            }
        ],
        model="gpt-3.5-turbo",
    )
    
    # Get chatgpt response
    content = chat_completion.choices[0].message.content
    
    # Return response as dict
    json_data = json.loads(content)
    return json_data["keywords"], json_data["description"]

if __name__ == "__main__":
    get_tags_description("iphone", "iphone 12", 1000, 5, 100, "Amazon", True, "https://www.apple.com/")