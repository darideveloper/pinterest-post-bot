import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

API_KEY_OPENAI = os.getenv("API_KEY_OPENAI")
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
PROJECT_FOLDER = os.path.dirname(CURRENT_FOLDER)
CHATGTP_PROMPT_FOLDER = os.path.join(PROJECT_FOLDER, "prompts")


def get_description(keyword: str, title: str, price: float, rate_number: int,
                    reviews_number: int, store: str, best_seller: bool,
                    store_url: str) -> str:
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
        str: chatgpt description
    """

    # Get prompt data
    prompt_path = os.path.join(CHATGTP_PROMPT_FOLDER, "pinterest.txt")
    with open(prompt_path, "r") as file:
        prompt = file.read()

    # Replace values
    prompt_values = {
        "keyword": keyword,
        "title": title,
        "price": price,
        "rate_number": rate_number,
        "reviews_number": reviews_number,
        "store": store,
        "best_seller": best_seller,
        "store_url": store_url
    }
    for prompt_key, prompt_value in prompt_values.items():
        prompt = prompt.replace(f"<{prompt_key}>", str(prompt_value))

    client = OpenAI(
        # This is the default and can be omitted
        api_key=API_KEY_OPENAI
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    # Get chatgpt response
    content = chat_completion.choices[0].message.content

    # Get only text
    separator = "Description: "
    if separator in content:
        content = content.split("Description: ")[1]
    else:
        content = ""
    
    # Remove all emojis from text, like 💻✨
    content = content.encode('ascii', 'ignore').decode('ascii')

    # Return response as dict
    return content


if __name__ == "__main__":
    response = get_description(
        "iphone",
        "iphone 12",
        1000,
        5,
        100,
        "Amazon",
        True,
        "https://www.apple.com/"
    )
    print(response)
    print(f"chars: {len(response)}")
