import streamlit as st
from speech import get_voice_input
from classifier import find_aisle, classify_item
import json

# Load aisle data
with open("aisles.json") as f:
    aisle_data = json.load(f)

# Initialize session state for user input
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

st.markdown(
    """
    <style>
    .input-container {
        display: flex;
        align-items: center;
        width: 100%;
        border: 1px solid #ccc;
        border-radius: 30px;
        background-color: #f1f1f1;
        padding: 5px;
    }
    .mic-button {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        margin-right: 10px;
    }
    .mic-button:hover {
        opacity: 0.8;
    }
    .text-input {
        flex: 1;
        padding: 10px;
        border: none;
        background-color: transparent;
        font-size: 16px;
        outline: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Staples Finder 2.0")

# Initialize session state for user input
if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""
    
# **CREATE A 2-COLUMN LAYOUT** (Mic Button | Text Input)
col1, col2 = st.columns([1, 5])  # Adjust width ratio for better alignment

# **Mic Button (Triggers Voice Input)**
with col1:
    mic_clicked = st.button("🎤", key="mic_button")

# **Text Input (Triggers Search on Enter)**
with col2:
    user_input = st.text_input(" ", placeholder="Where is ...", label_visibility="collapsed")

# **Classify and Search when "Enter" is Pressed**
if user_input and user_input != st.session_state["user_input"]:
    st.session_state["user_input"] = user_input  # Store new input
    st.write('<p class="listening">Searching...</p>', unsafe_allow_html=True)
    item_name = st.session_state["user_input"]
    st.write(f"**User:** {st.session_state['user_input']}") 

    if item_name and not item_name.startswith("❌"):
        aisle_info = find_aisle(item_name, aisle_data)
        st.success(aisle_info)
    else:
        st.error(item_name)

# **Handle Mic Button Click**
if mic_clicked:
    st.write('<p class="listening">Listening...</p>', unsafe_allow_html=True)
    item_name = get_voice_input()
    st.write(f"**User:**{item_name}")

    if item_name and not item_name.startswith("❌"):
        aisle_info = find_aisle(item_name, aisle_data)
        st.success(aisle_info)
    else:
        st.error(item_name)
