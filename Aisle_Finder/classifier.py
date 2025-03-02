import requests
import json
import os
import re
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# import items

CATEGORIES ={ "Laser paper",
      "inkjet paper",
      "multi-use paper",
      "copy paper",
      "colour paper",
      "card & cover stock paper",
      "paper & thermal rolls",
      "refill paper",
      "paper pads",
      "laminating",
      "binding",
      "case paper",
      "safes",
      "easels",
      "easels pads/specialty boards",
      "home & office boards",
      "whiteboards",
      "corkboards",
      "binders",
      "containers",
      "storage containers",
      "storage boxes",
      "indexes",
      "sheet protectors",
      "report covers",
      "presentation folders",
      "plastic storage",
      "portable files",
      "sign & literature holders",
      "calenders & planners",
      "Agendas",
      "packing tape",
      "corrugate boxes",
      "pack & ship",
      "packaging protection",
      "post-it Notes & Flags",
      "Moving supplies",
      "Scales",
      "vinyl",
      "letters & Signs",
      "specialty Envelopes",
      "envelopes",
      " I.D. & Filing",
      "Clear Mailing Labels",
      "White Mailing Labels",
      "Name Badges",
      "Labels",
      "Folders Tabs & Frames",
      "Hanging Files",
      "File folders",
      "expandable Files",
      "Cash Boxes",
      "coin rollers",
      "literature & mail sorter",
      "notebooks",
      "business stationery",
      "journals",
      "envelopes",
      "stationery & invitations",
      "T-shirt transfer/ cards",
      "Travel Accessories",
      "travel luggage",
      "backpacks",
      "business cases",
      "art supplies",
      "drafting & design",
      "staplers",
      "presentation boards",
      "arts + crafts",
      "health & safety",
      "cleaning supplies",
      "waste supplies",
      "cleaning supplies",
      "janitorial supplies",
      "bathroom tissue",
      "single brew coffee",
      "small appliances",
      "break room",
      "lunch",
      "accounting",
      "business forms",
      "padfolios & card holders",
      "Tape",
      "Glue",
      "Rubber bands",
      "paper clips",
      "binder clips",
      "hanging supplies",
      "index cards",
      "index storage",
      "daytimers",
      "planners",
      "Stamps",
      "highlighters",
      "white-out",
      "shapeners",
      "pencil",
      "pens",
      "snacks",
      "puzzzle",
      "kids toys",
      "educational books",
      "lego",
      "pen refills",
      "Makers",
      "Eraser",
      "play dough",
      "Clipboards",
      " (scissors, rulers & punches)",
      "Trimmers",
      "calculators",
      "tablet accessories",
      "tablets + tablet accessories",
      "laptop cases",
      "smartwatches",
      "cell phone accessories",
      "unlocked phones",
      "bell services",
      "speakers",
      "media streaming",
      "in-earphones",
      "over-earphones",
      "kids headphones",
      "PC gaming",
      "gaming consoles",
        "computer cleaning supplies",
      "gaming consoles",
      "gift card",
      "gaming equipment",
      "keyboards",
      "smart home + office",
      "printers",
      "networking",
      "office furniture",
        " printers",
      "labellers",
      "pos & time clocks",
      "shredders",
      " toner cartridges",
      "ink cartridges"
    }


def classify_item(item_name):
    """Classifies an item into a category using AI."""
    if not GROQ_API_KEY:
        return "Error: Missing API Key."

      # Load JSON file
    with open("aisles.json", "r") as f:
        aisle_data = json.load(f)

    blacklist = [x.lower() for x in aisle_data["blacklist"]]
    
    # Check if the item is blacklisted before sending to AI
    if item_name.lower() in blacklist:
        return "Item Not Found at Staples."
    
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
            if response_text in CATEGORIES:
                return response_text  # Valid category
            elif "Item Not Found" in response_text:
                return f"❌ '{item_name}' is not sold at staples."

        return f"❌ '{item_name}' is not sold at staples."

    except requests.exceptions.RequestException as e:
        return f"Error: API request failed ({e})."

def find_aisle(item_name, aisle_data):
    """Find the aisle based on the classified category."""
    category = classify_item(item_name)
    
    if category == "Item Not Found":
        return f"❌ '{item_name}' is not sold at staples."

    if category.startswith("Error"):
        return category  # Return error message

    for aisle, categories in aisle_data["aisles"].items():
        if category in categories:
            return f"{aisle} ({category})."
    
    return f"❌ '{item_name}' is not sold at staples."
