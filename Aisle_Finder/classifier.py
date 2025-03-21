import requests
import json
import os
import re
from dotenv import load_dotenv
import streamlit as st

# Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets["groq"]["GROQ_API_KEY"]

def classify_item(item_name):
    """Classifies an item into a category using AI."""
    if not GROQ_API_KEY:
        return "Error: Missing API Key."

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the JSON file
    json_path = os.path.join(script_dir, "aisles.json")
    # Load JSON file
    with open(json_path) as f:
        aisle_data = json.load(f)

    # Extract categories from the new structure
    CATEGORIES = sorted(set(
        item.lower() 
        for aisle in aisle_data["aisles"].values() 
        for item in aisle.get("items", [])
    ))
    blacklist = [x.lower() for x in aisle_data.get("blacklist", [])]

    # Check if the item is blacklisted before sending to AI
    if item_name.lower() in blacklist:
        return "Item Not Found"

    prompt = f"""
    Classify the item '{item_name}' into one of these office supply retailer store categories:
    {", ".join(CATEGORIES)}.

    **Only return the category name. Do NOT explain your reasoning.**
    If the item is NOT found in an office supply retailer store, return: "Item Not Found".
    
    Additionally, if the item is considered **inappropriate for a store (e.g., {", ".join(blacklist)})**, return: "Item Not Found".

    Example Outputs:
    - "paper" (for 65lb paper)
    - "laminating" (for laminator)
    - "Item Not Found" (for Toyota)
    - "Item Not Found" (for gun)
    """

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={"model": "gemma2-9b-it", "messages": [{"role": "user", "content": prompt}], "temperature": 0}
        )

        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}."

        result = response.json()
        print("Groq API Response:", json.dumps(result, indent=2))  # Debugging

        if "choices" in result and result["choices"]:
            response_text = result["choices"][0]["message"]["content"].strip().lower()

            # Validate response: response_text should be one of the categories
            if response_text in CATEGORIES:
                return response_text  # Valid category
            elif "item not found" in response_text:
                return "Item Not Found"

        return "Item Not Found"

    except requests.exceptions.RequestException as e:
        return f"Error: API request failed ({e})."

def find_aisle(item_name, aisle_data):
    """Find the aisle based on the classified category."""
    category = classify_item(item_name)
    
    if category == "Item Not Found" or category.startswith("Error"):
        return f"❌ '{item_name}' is not sold at Staples."

    # Search for the aisle containing the classified category
    for aisle_key, aisle_info in aisle_data["aisles"].items():
        # Create a lower-case version of items for case-insensitive matching
        aisle_items = [item.lower() for item in aisle_info.get("items", [])]
        if category in aisle_items:
            # Return aisle number, title, and matched category
            return f"{aisle_key} ({aisle_info.get('category', 'No Title')}): {category}"
    
    return f"❌ '{item_name}' is not sold at Staples."

