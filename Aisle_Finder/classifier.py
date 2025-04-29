import requests
import json
import os
import re
from dotenv import load_dotenv
import streamlit as st

# Load API Key
load_dotenv()
# Use environment variable or Streamlit secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY") # Use .get() for safety

if not GROQ_API_KEY:
    st.error("Error: GROQ_API_KEY not found. Please set it in a .env file or Streamlit secrets.")


def classify_item(item_name, aisle_data):
    """Classifies an item into a category using AI."""
    if not GROQ_API_KEY:
        return "Error: Missing API Key."

    # Extract actual categories from the structure
    # Create a lower-case version of category titles for case-insensitive matching
    CATEGORIES = sorted(set(
        aisle_info.get("category", "").lower()
        for aisle_info in aisle_data["aisles"].values()
        if aisle_info.get("category") # Only include if category is not None or empty
    ))

    blacklist = [x.lower() for x in aisle_data.get("blacklist", [])]

    # Check if the item is blacklisted before sending to AI
    if item_name.lower() in blacklist:
        return "Item Not Found"

    # Check if the item is listed directly in the JSON items (direct match first)
    for aisle_key, aisle_info in aisle_data["aisles"].items():
        aisle_items = [item.lower() for item in aisle_info.get("items", [])]
        if item_name.lower() in aisle_items:
            # If direct match, return the aisle key and the matched item
            # We'll handle the final output in find_aisle
            return {"type": "item", "item": item_name.lower(), "aisle": aisle_key}


    # If no direct match, use AI to classify into a broader category
    prompt = f"""
    Classify the item '{item_name}' into one of these store categories:
    {", ".join(CATEGORIES)}.

    **Only return the category name. Do NOT explain your reasoning.**
    If the item is NOT found in these store categories, return: "Category Not Found".

    Additionally, if the item is considered **inappropriate for a store (e.g., {", ".join(blacklist)})**, return: "Category Not Found".

    Example Outputs:
    - "Paper & Presentation Supplies" (for 65lb paper)
    - "Shipping, Mailing & Filing Supplies" (for packing tape)
    - "Category Not Found" (for Toyota)
    - "Category Not Found" (for gun)
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
            print(f"API Error Response: {response.text}") # Added for debugging
            return f"Error: API returned status {response.status_code}."

        result = response.json()
        print("Groq API Response:", json.dumps(result, indent=2)) # Debugging

        if "choices" in result and result["choices"]:
            response_text = result["choices"][0]["message"]["content"].strip() # Keep original casing for category matching
            # Convert CATEGORIES to lowercase for case-insensitive check
            categories_lower = [cat.lower() for cat in CATEGORIES]

            if response_text.lower() in categories_lower:
                 # Find the original category name with correct casing
                original_category = next((cat for cat in CATEGORIES if cat.lower() == response_text.lower()), response_text)
                return {"type": "category", "category": original_category} # Valid category
            elif "category not found" in response_text.lower():
                 return "Category Not Found"

        return "Category Not Found"

    except requests.exceptions.RequestException as e:
        return f"Error: API request failed ({e})."

def find_aisle(item_name, aisle_data):
    """Find the aisle based on direct item match or classified category."""
    classification_result = classify_item(item_name, aisle_data)

    if isinstance(classification_result, str):
        # Handle errors or "Item/Category Not Found" from classify_item
        if classification_result.startswith("Error"):
            return f"An error occurred: {classification_result}"
        else: # "Item Not Found" or "Category Not Found"
            return f"❌ '{item_name}' is not sold at Staples."

    # If classification_result is a dictionary, it's either a direct item match or a classified category
    if classification_result["type"] == "item":
        # Direct item match found in classify_item
        aisle_key = classification_result["aisle"]
        aisle_info = aisle_data["aisles"][aisle_key]
        # Find the original casing of the item in the aisle for display
        original_item = next((item for item in aisle_info.get("items", []) if item.lower() == classification_result["item"]), classification_result["item"])
        return f"✅ {original_item.capitalize()} is in {aisle_key} ({aisle_info.get('category', 'No Title')})."

    elif classification_result["type"] == "category":
        # Classified into a category by the AI
        classified_category = classification_result["category"]
        # Search for the aisle containing this classified category
        for aisle_key, aisle_info in aisle_data["aisles"].items():
            if aisle_info.get("category", "").lower() == classified_category.lower():
                # Return aisle number and category title
                return f"✅ '{item_name.capitalize()}' is likely in {aisle_key} ({aisle_info.get('category', 'No Title')})."

        # If the classified category doesn't match an aisle category (shouldn't happen with correct CATEGORIES list)
        return f"❌ Could not find an aisle for the category '{classified_category}'."

    # Should not reach here, but as a fallback
    return f"❌ Could not determine the location for '{item_name}'."