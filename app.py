import streamlit as st
import os
from search_images import search_images
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Image Finder",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a more "premium" look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        width: 100%;
        background-color: #ff4b4b;
        color: white;
    }
    .image-card {
        background-color: #1e2128;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("Smart Image Search")
    st.markdown("Search through your database using natural language.")

    # Sidebar for filters/settings
    with st.sidebar:
        st.header("Settings")
        top_k = st.slider("Number of results", min_value=1, max_value=20, value=5)
        st.info("This app uses CLIP embeddings and Oracle Vector Search to find relevant images.")

    # Main search interface
    col1, col2 = st.columns([4, 1])
    
    with col1:
        query = st.text_input("Enter your query (e.g., 'tomato', 'mango')", placeholder="Search for images...")
    
    with col2:
        st.write("") # Spacer
        st.write("") # Spacer
        search_button = st.button("Search")

    if search_button or query:
        if query:
            with st.spinner("Searching for the best matches..."):
                try:
                    results = search_images(query, top_k=top_k)
                    
                    if not results:
                        st.warning("No images found for that query.")
                    else:
                        st.success(f"Found {len(results)} matches!")
                        
                        # Display results in a grid
                        cols = st.columns(3)
                        for idx, row in enumerate(results):
                            file_name, image_path, description, dist = row
                            
                            with cols[idx % 3]:
                                with st.container():
                                    # Try to load and display the image
                                    if os.path.exists(image_path):
                                        try:
                                            img = Image.open(image_path)
                                            st.image(img, use_container_width=True, caption=file_name)
                                        except Exception as e:
                                            st.error(f"Error loading image: {e}")
                                    else:
                                        st.error(f"Image not found at: {image_path}")
                                    
                                    with st.expander("Details"):
                                        st.write(f"**Description:** {description}")
                                        st.write(f"**Distance:** {dist:.4f}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a query first.")

if __name__ == "__main__":
    main()
