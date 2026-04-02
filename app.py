import streamlit as st
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# This tells Python to look in the current folder specifically
load_dotenv(os.path.join(os.getcwd(), '.env'))

API_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
BASE_URL = "https://api.unsplash.com/search/photos"

# --- Page Configuration ---
st.set_page_config(page_title="Pro Image Finder", layout="wide", page_icon="📸")

# --- Helper Functions ---
def fetch_images(query, count, orientation):
    """
    Handles the API request logic.
    Returns a list of image objects or None if the request fails.
    """
    headers = {"Authorization": f"Client-ID {API_KEY}"}
    params = {
        "query": query,
        "per_page": count,
        "orientation": orientation,
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["results"]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def download_image(url):
    """
    Converts image URL to bytes for the Streamlit download button.
    """
    response = requests.get(url)
    return BytesIO(response.content)

# --- UI Layout ---
st.title(" Advanced Image Finder")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("Search Settings")
query = st.sidebar.text_input("Enter Keyword", placeholder="e.g., Cyberpunk, Nature")
num_results = st.sidebar.slider("Number of Results", min_value=5, max_value=30, value=12)
orientation = st.sidebar.selectbox("Orientation", ["landscape", "portrait", "squarish"])

# Execution Logic
if query:
    with st.spinner(f"Searching for '{query}'..."):
        results = fetch_images(query, num_results, orientation)

    if results:
        # Create a responsive grid layout
        cols = st.columns(3) # 3-column grid
        
        for index, img_data in enumerate(results):
            # Extract Metadata
            img_url = img_data["urls"]["regular"]
            download_url = img_data["urls"]["full"]
            photographer = img_data["user"]["name"]
            description = img_data["alt_description"] or "Untitled"
            
            # Determine which column to place the image in
            with cols[index % 3]:
                st.image(img_url, use_container_width=True)
                st.caption(f"**{description.title()}**")
                st.write(f" {photographer}")
                
                # Download System
                img_bytes = download_image(download_url)
                st.download_button(
                    label="Download High-Res",
                    data=img_bytes,
                    file_name=f"{query}_{index}.jpg",
                    mime="image/jpeg",
                    key=f"btn_{index}"
                )
                st.markdown("---")
    else:
        st.info("No results found. Try a different keyword.")
else:
    st.info(" Enter a keyword in the sidebar to start exploring.")