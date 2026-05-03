import os
import array
import mimetypes
import oracledb
import torch
import open_clip
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv

oracledb.defaults.fetch_lobs = False

load_dotenv()

# Date conexiune baza de date (Oracle)
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DSN = os.environ['DB_DSN']

# Directorul cu dataset-ul de imagini
DATASET_DIR = "dataset"

# Model pre-antrenat open-clip
MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

# Extensii de fisiere suportate
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Incarcam modelul open-clip pre-antrenat si transformatiile
model, _, preprocess = open_clip.create_model_and_transforms(
    MODEL_NAME,
    pretrained=PRETRAINED
)


# Functia de construire a descrierii dintr-un nume de fisier
def build_description(filename: str) -> str:
    name, _ = os.path.splitext(filename)
    clean = name.replace("_", " ").replace("-", " ").strip()
    return clean

# Functia de verificare a extensiei de fisier
def is_supported_image(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if ext in SUPPORTED_EXTENSIONS:
        return True

    mime_type, _ = mimetypes.guess_type(path)
    return mime_type is not None and mime_type.startswith("image/")


# Functia de transformare a unei imagini intr-un vector de embedding
def get_image_embedding(path: str) -> array.array:
    image = Image.open(path).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        features = model.encode_image(image_tensor)
        features /= features.norm(dim=-1, keepdim=True)

    vec = features[0].cpu().numpy().astype("float32")
    return array.array("f", vec.tolist())


# Functia de verificare a existentei unei imagini in baza de date
def row_exists(cur, file_name: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM images_dataset
        WHERE file_name = :1
        FETCH FIRST 1 ROWS ONLY
        """,
        [file_name],
    )
    return cur.fetchone() is not None


# Functia de inserare a unei imagini in baza de date
def insert_image(cur, file_name: str, image_path: str, description: str, embedding: array.array):
    cur.execute(
        """
        INSERT INTO images_dataset
        (file_name, image_path, description, embedding)
        VALUES (:1, :2, :3, :4)
        """,
        [file_name, image_path, description, embedding],
    )

# Functia principala pentru incarcarea dataset-ului de imagini in baza de date Oracle
def main():
    if not os.path.isdir(DATASET_DIR):
        print(f"Folderul '{DATASET_DIR}' nu exista.")
        return

    # Sortam lista de fisiere in ordine alfabetica
    files = sorted(os.listdir(DATASET_DIR))
    image_files = [
        f for f in files
        if os.path.isfile(os.path.join(DATASET_DIR, f)) and is_supported_image(os.path.join(DATASET_DIR, f))
    ]

    if not image_files:
        print(f"Nu am gasit imagini in folderul '{DATASET_DIR}'.")
        return

    # Afisam numarul de imagini gasite
    print(f"Am gasit {len(image_files)} imagini.")

    # Stabilim conexiunea la baza de date
    conn = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )

    inserted = 0
    skipped = 0
    failed = 0

    # Blocul try-finally pentru a ne asigura ca conexiunea la baza de date este inchisa
    try:
        with conn.cursor() as cur:
            for file_name in image_files:
                full_path = os.path.join(DATASET_DIR, file_name)

                try:
                    if row_exists(cur, file_name):
                        print(f"[SKIP] Exista deja in DB: {file_name}")
                        skipped += 1
                        continue

                    # Construim descrierea imaginii
                    description = build_description(file_name)
                    # Calculam vectorul de embedding pentru imagine
                    embedding = get_image_embedding(full_path)

                    # Inseram imaginea in baza de date
                    insert_image(
                        cur=cur,
                        file_name=file_name,
                        image_path=full_path,
                        description=description,
                        embedding=embedding,
                    )

                    inserted += 1
                    print(f"[OK] Inserat: {file_name}")

                # Verificam daca imaginea este invalida
                except (UnidentifiedImageError, OSError) as img_err:
                    failed += 1
                    print(f"[ERR] Imagine invalida '{file_name}': {img_err}")
                # Orice alte erori la procesarea imaginii
                except Exception as ex:
                    failed += 1
                    print(f"[ERR] Nu am putut insera '{file_name}': {ex}")

            # Comitem modificarile in baza de date
            conn.commit()

    finally:
        # Inchidem conexiunea la baza de date
        conn.close()

    # Afisam un rezumat al operatiunilor
    print("\nRezumat:")
    print(f"  Inserate: {inserted}")
    print(f"  Sarite:   {skipped}")
    print(f"  Esuate:   {failed}")


# Rulare script
if __name__ == "__main__":
    main()