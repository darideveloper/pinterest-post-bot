import os
import json
import requests
from dotenv import load_dotenv

# Env variables
load_dotenv()
API_KEY_PRICE_CHECKER = os.getenv("API_KEY_PRICE_CHECKER")
HOST_PRICE_CHECKER = os.getenv("HOST_PRICE_CHECKER")


def get_products_data(request_id: int) -> list:
    """ Get products data from price checker api
    
    Args:
        request_id (int): request id
    
    Returns:
        list: dict of products
    """
    
    endpoint = f"{HOST_PRICE_CHECKER}/results/"
    payload = json.dumps({
        "request-id": request_id,
        "api-key": "Sp6pM3VzDN5wIm6bqQJ8"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    res = requests.request("POST", endpoint, headers=headers, data=payload)
    json_data = json.loads(res.text)
    products = json_data["data"]["products"]
    return products
        
        
if __name__ == "__main__":
    products = get_products_data(152)
    print(products)