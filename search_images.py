import os
import array
import oracledb
import torch
import open_clip
from dotenv import load_dotenv

oracledb.defaults.fetch_lobs = False

load_dotenv()

# Date conexiune baza de date (Oracle)
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DSN = os.environ['DB_DSN']

# Model pre-antrenat open-clip
MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

# Incarcam modelul open-clip pre-antrenat si tokenizer-ul
model, _, _ = open_clip.create_model_and_transforms(
    MODEL_NAME,
    pretrained=PRETRAINED
)
tokenizer = open_clip.get_tokenizer(MODEL_NAME)

# Transforma textul intr-un vector de embedding
def get_text_embedding(text: str) -> array.array:
    tokens = tokenizer([text])

    with torch.no_grad():
        features = model.encode_text(tokens)
        features /= features.norm(dim=-1, keepdim=True)

    vec = features[0].cpu().numpy().astype("float32")
    return array.array("f", vec.tolist())


# Logica principala pentru cautarea de imagini in baza de date Oracle
def search_images(query_text: str, top_k: int = 5):
    # Convertim textul de intrare intr-un vector de embedding
    query_vector = get_text_embedding(query_text)

    # Stabilim conexiunea la baza de date folosind variabilele de environment
    conn = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )

    try:
        with conn.cursor() as cur:
            # SQL pentru gasirea celor mai similare imagini folosind distanta cosinus
            sql = f"""
                SELECT file_name,
                       image_path,
                       description,
                       VECTOR_DISTANCE(embedding, :1, COSINE) AS dist
                FROM images_dataset
                ORDER BY dist
                FETCH FIRST {top_k} ROWS ONLY
            """

            cur.execute(sql, [query_vector])
            rows = cur.fetchall()
            return rows
    finally:
        # Inchidem conexiunea la baza de date
        conn.close()