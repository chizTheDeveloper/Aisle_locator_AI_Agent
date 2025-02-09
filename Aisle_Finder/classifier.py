import requests
import json
import os
import re
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Define valid grocery categories
GROCERY_CATEGORIES = ["Fruits", "Vegetables", "Dairy", "Bakery", "Beverages",
                      "Snacks", "Meat", "Frozen Foods", "Cereal", "Canned Goods", "Cleaning Supplies"]

def classify_item(item_name):
    """Classifies an item into a category using AI."""
    if not GROQ_API_KEY:
        return "Error: Missing API Key."

    prompt = f"""
    Classify the item '{item_name}' into one of these grocery store categories:
    {", ".join(GROCERY_CATEGORIES)}.

    **Only return the category name. Do NOT explain your reasoning.**
    If the item is NOT found in a grocery store, return: "Item Not Found".
    
    Example Outputs:
    - "Vegetables" (for Carrot)
    - "Beverages" (for Coca-Cola)
    - "Item Not Found" (for Toyota)
    """

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "gemma2-9b-it", "messages": [{"role": "user", "content": prompt}], "temperature": 0}
        )

        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}."

        result = response.json()
        print("Groq API Response:", json.dumps(result, indent=2))  # Debugging

        if "choices" in result and result["choices"]:
            response_text = result["choices"][0]["message"]["content"].strip()

            # Validate response
            if response_text in GROCERY_CATEGORIES:
                return response_text  # Valid category
            elif "Item Not Found" in response_text:
                return "Item Not Found"

        return "Error: AI did not return a valid category."

    except requests.exceptions.RequestException as e:
        return f"Error: API request failed ({e})."

def find_aisle(item_name, aisle_data):
    """Find the aisle based on the classified category."""
    category = classify_item(item_name)
    
    if category == "Item Not Found":
        return f"❌ '{item_name}' is not sold in a grocery store."

    if category.startswith("Error"):
        return category  # Return error message

    for aisle, categories in aisle_data["aisles"].items():
        if category in categories:
            return f"✅ {item_name} is in {aisle} ({category})."
    
    return f"❌ {item_name} not found in the database."
