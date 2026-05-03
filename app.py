import streamlit as st
import os
from PIL import Image
from search_images import search_images

# Basic page setup
st.set_page_config(
    page_title="Image Search",
    layout="wide"
)

# Custom styling to make the grid look a bit better
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        background-color: #ff4b4b;
        color: white;
        height: auto;
    }
    /* Rounded corners for images */
    img {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def run_app():
    st.title("Smart Image Search")
    st.write("Search through the database using natural language queries.")

    # Slider for result count in the sidebar
    with st.sidebar:
        st.header("Search Settings")
        limit = st.slider("Max results", 1, 20, 5)
        st.write("Uses CLIP embeddings and Oracle Vector Search.")

    # Search bar and button layout
    search_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
    
    with search_col:
        query = st.text_input("What are you looking for?", placeholder="e.g. tomato, mango")
    
    with button_col:
        clicked = st.button("Search", use_container_width=True)

    # If search is triggered by button or enter key
    if clicked or query:
        if not query.strip():
            st.warning("Please enter something to search for.")
            return

        with st.spinner("Searching..."):
            try:
                # Call our search logic from search_images.py
                matches = search_images(query, top_k=limit)
                
                if not matches:
                    st.info("No matches found in the database.")
                else:
                    st.success(f"Found {len(matches)} images.")
                    
                    # 3-column grid for results
                    columns = st.columns(3)
                    for i, row in enumerate(matches):
                        name, path, desc, score = row
                        
                        # Use modulo to cycle through columns
                        with columns[i % 3]:
                            if os.path.exists(path):
                                img = Image.open(path)
                                st.image(img, use_container_width=True, caption=name)
                            else:
                                st.error(f"File missing: {path}")
                            
                            # Additional details hidden in an expander
                            with st.expander("View details"):
                                st.write(f"**Description:** {desc}")
                                st.write(f"**Score:** {score:.4f}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

if __name__ == "__main__":
    run_app()
