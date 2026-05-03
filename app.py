import streamlit as st
import os
from PIL import Image
from search_images import search_images

# Setup de baza pentru pagina web
st.set_page_config(
    page_title="Image Search",
    layout="wide"
)

# Custom styling pentru a imbunatati aspectul paginii
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

# Functia principala care ruleaza aplicatia
def run_app():
    st.title("Smart Image Search")
    st.write("Search through the database using natural language queries.")

    # Sidebar pentru setarile de cautare
    with st.sidebar:
        st.header("Search Settings")
        limit = st.slider("Max results", 1, 20, 5)
        st.write("Uses CLIP embeddings and Oracle Vector Search.")

    # Layout pentru search bar si buton
    search_col, button_col = st.columns([5, 1], vertical_alignment="bottom")
    
    with search_col:
        query = st.text_input("Ce cauti?", placeholder="e.g. tomato, mango")
    
    with button_col:
        clicked = st.button("Search", use_container_width=True)

    # Daca se apasa butonul sau tasta Enter
    if clicked or query:
        if not query.strip():
            st.warning("Te rog introdu un termen de cautare.")
            return

        with st.spinner("Cautare..."):
            try:
                # Apelam logica de cautare din search_images.py
                matches = search_images(query, top_k=limit)
                
                if not matches:
                    st.info("Nu s-au gasit imagini in baza de date.")
                else:
                    st.success(f"Am gasit {len(matches)} imagini.")
                    
                    # Grid cu 3 coloane pentru rezultate
                    columns = st.columns(3)
                    for i, row in enumerate(matches):
                        name, path, desc, score = row
                        
                        # Folosim modulo pentru a cicla prin coloane
                        with columns[i % 3]:
                            if os.path.exists(path):
                                img = Image.open(path)
                                st.image(img, use_container_width=True, caption=name)
                            else:
                                st.error(f"Fisierul nu exista: {path}")
                            
                            # Detalii suplimentare ascunse intr-un expander
                            with st.expander("Detalii"):
                                st.write(f"**Descriere:** {desc}")
                                st.write(f"**Scor:** {score:.4f}")
            except Exception as e:
                st.error(f"A aparut o eroare: {e}")

# Pornirea aplicatiei
if __name__ == "__main__":
    run_app()
