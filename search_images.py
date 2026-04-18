import os
import array
import oracledb
import torch
import open_clip
from dotenv import load_dotenv

oracledb.defaults.fetch_lobs = False

load_dotenv()

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DSN = os.environ['DB_DSN']

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

model, _, _ = open_clip.create_model_and_transforms(
    MODEL_NAME,
    pretrained=PRETRAINED
)
tokenizer = open_clip.get_tokenizer(MODEL_NAME)

def get_text_embedding(text: str) -> array.array:
    tokens = tokenizer([text])

    with torch.no_grad():
        features = model.encode_text(tokens)
        features /= features.norm(dim=-1, keepdim=True)

    vec = features[0].cpu().numpy().astype("float32")
    return array.array("f", vec.tolist())

def search_images(query_text: str, top_k: int = 5):
    query_vector = get_text_embedding(query_text)

    conn = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )

    try:
        with conn.cursor() as cur:
            sql = f"""
                SELECT file_name,
                       category,
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
        conn.close()

if __name__ == "__main__":
    query = "forest in sunlight"
    results = search_images(query, top_k=5)

    print(f"\nQuery: {query}\n")
    if not results:
        print("No results found.")
    else:
        for idx, row in enumerate(results, start=1):
            file_name, category, image_path, description, dist = row
            print(f"{idx}. {file_name}")
            print(f"   category: {category}")
            print(f"   path: {image_path}")
            print(f"   description: {description}")
            print(f"   distance: {dist}")
            print()