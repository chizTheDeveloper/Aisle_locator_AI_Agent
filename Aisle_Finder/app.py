import streamlit as st
from speech import get_voice_input
from classifier import find_aisle
import json

# Load aisle data
with open("aisles.json") as f:
    aisle_data = json.load(f)

st.title("🛒 Grocery Aisle Finder")

# UI for Voice Input
st.markdown(
    """
    <style>
    .mic-button {
        background-color: #f8f9fa;
        border: none;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        font-size: 30px;
        cursor: pointer;
        transition: 0.3s;
    }
    .mic-button:hover {
        background-color: #e9ecef;
    }
    .listening {
        color: red;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

option = st.radio("How do you want to search?", ("Type", "Voice"))

if option == "Type":
    item_name = st.text_input("Enter item name:")
    if st.button("Find Aisle"):
        if item_name:
            aisle_info = find_aisle(item_name, aisle_data)
            st.success(aisle_info)

elif option == "Voice":
    st.markdown('<button class="mic-button">🎤</button>', unsafe_allow_html=True)
    
    if st.button("Start Listening"):
        st.write('<p class="listening">Listening...</p>', unsafe_allow_html=True)
        item_name = get_voice_input()
        st.write(f"🗣️ You said: **{item_name}**")

        if item_name and not item_name.startswith("❌"):
            aisle_info = find_aisle(item_name, aisle_data)
            st.success(aisle_info)
        else:
            st.error(item_name)
