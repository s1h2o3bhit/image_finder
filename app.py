import streamlit as st
import requests
import pandas as pd
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.getcwd(), '.env'))

API_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
BASE_URL = "https://api.unsplash.com/search/photos"

# --- Page Configuration ---
st.set_page_config(page_title="AI Image Engine & Analytics", layout="wide")

# --- 1. Performance Optimization: Caching ---
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_images(query, count, orientation, page=1):
    """
    Handles the API request logic with caching to prevent redundant API calls.
    """
    headers = {"Authorization": f"Client-ID {API_KEY}"}
    params = {
        "query": query,
        "per_page": count,
        "orientation": orientation,
        "page": page
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()["results"]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []

def download_image(url):
    """
    Converts image URL to bytes for the Streamlit download button.
    """
    try:
        response = requests.get(url)
        return BytesIO(response.content)
    except:
        return None

# --- 2. Session State Initialization (Pagination) ---
if "page_number" not in st.session_state:
    st.session_state.page_number = 1

# --- UI Layout ---
st.title(" Advanced Image Finder & Analytics")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("Search Settings")
query = st.sidebar.text_input("Enter Keyword", placeholder="e.g., Cyberpunk, Nature")
num_results = st.sidebar.slider("Results per Page", min_value=5, max_value=30, value=12)
orientation = st.sidebar.selectbox("Orientation", ["landscape", "portrait", "squarish"])

# Reset page number if a new keyword is entered
if st.sidebar.button("Refresh Search"):
    st.session_state.page_number = 1

# Execution Logic
if query:
    with st.spinner(f"Fetching page {st.session_state.page_number} for '{query}'..."):
        results = fetch_images(query, num_results, orientation, st.session_state.page_number)

    if results:
        # --- 3. The Analytics Dashboard (EDA) ---
        with st.expander(" View Search Data Analytics"):
            # Convert raw JSON to DataFrame
            df = pd.DataFrame([{
                'Width': img['width'],
                'Height': img['height'],
                'Photographer': img['user']['name'],
                'Likes': img['likes'],
                'Color': img['color']
            } for img in results])

            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Image Aspect Ratio Distribution")
                # Using scatter chart to show resolution trends
                st.scatter_chart(data=df, x='Width', y='Height', color='Color')
            
            with col_b:
                st.subheader("Top Contributors in this Search")
                # Visualizing which photographers dominate the results
                st.bar_chart(df['Photographer'].value_counts())

        st.markdown(f"### Showing Page {st.session_state.page_number}")
        
        # Create a responsive grid layout
        cols = st.columns(3) 
        
        for index, img_data in enumerate(results):
            img_url = img_data["urls"]["regular"]
            download_url = img_data["urls"]["full"]
            photographer = img_data["user"]["name"]
            description = img_data["alt_description"] or "Untitled"
            
            with cols[index % 3]:
                st.image(img_url, use_container_width=True)
                st.caption(f"**{description.title()}**")
                st.write(f"{photographer} |  {img_data['likes']} likes")
                
                # Download System
                img_bytes = download_image(download_url)
                if img_bytes:
                    st.download_button(
                        label="Download High-Res",
                        data=img_bytes,
                        file_name=f"{query}_pg{st.session_state.page_number}_{index}.jpg",
                        mime="image/jpeg",
                        key=f"btn_{st.session_state.page_number}_{index}"
                    )
                st.markdown("---")

        # --- Pagination Control ---
        st.markdown("### Browse More")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
        
        with nav_col1:
            if st.session_state.page_number > 1:
                if st.button("Previous Page"):
                    st.session_state.page_number -= 1
                    st.rerun()
        
        with nav_col2:
            st.write(f"Page {st.session_state.page_number}")

        with nav_col3:
            if st.button("Next Page"):
                st.session_state.page_number += 1
                st.rerun()

    else:
        st.info("No results found. Try a different keyword.")
else:
    st.info(" Enter a keyword in the sidebar to start exploring.")
