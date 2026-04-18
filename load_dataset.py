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

DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_DSN = os.environ['DB_DSN']

DATASET_DIR = "dataset"

MODEL_NAME = "ViT-B-32"
PRETRAINED = "openai"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

model, _, preprocess = open_clip.create_model_and_transforms(
    MODEL_NAME,
    pretrained=PRETRAINED
)


def build_description(filename: str) -> str:
    name, _ = os.path.splitext(filename)
    clean = name.replace("_", " ").replace("-", " ").strip()
    return clean


def is_supported_image(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    if ext in SUPPORTED_EXTENSIONS:
        return True

    mime_type, _ = mimetypes.guess_type(path)
    return mime_type is not None and mime_type.startswith("image/")


def get_image_embedding(path: str) -> array.array:
    image = Image.open(path).convert("RGB")
    image_tensor = preprocess(image).unsqueeze(0)

    with torch.no_grad():
        features = model.encode_image(image_tensor)
        features /= features.norm(dim=-1, keepdim=True)

    vec = features[0].cpu().numpy().astype("float32")
    return array.array("f", vec.tolist())


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


def insert_image(cur, file_name: str, image_path: str, description: str, embedding: array.array):
    cur.execute(
        """
        INSERT INTO images_dataset
        (file_name, image_path, description, embedding)
        VALUES (:1, :2, :3, :4)
        """,
        [file_name, image_path, description, embedding],
    )


def main():
    if not os.path.isdir(DATASET_DIR):
        print(f"Folderul '{DATASET_DIR}' nu există.")
        return

    files = sorted(os.listdir(DATASET_DIR))
    image_files = [
        f for f in files
        if os.path.isfile(os.path.join(DATASET_DIR, f)) and is_supported_image(os.path.join(DATASET_DIR, f))
    ]

    if not image_files:
        print(f"Nu am găsit imagini în folderul '{DATASET_DIR}'.")
        return

    print(f"Am găsit {len(image_files)} imagini.")

    conn = oracledb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        dsn=DB_DSN
    )

    inserted = 0
    skipped = 0
    failed = 0

    try:
        with conn.cursor() as cur:
            for file_name in image_files:
                full_path = os.path.join(DATASET_DIR, file_name)

                try:
                    if row_exists(cur, file_name):
                        print(f"[SKIP] Există deja în DB: {file_name}")
                        skipped += 1
                        continue

                    description = build_description(file_name)
                    embedding = get_image_embedding(full_path)

                    insert_image(
                        cur=cur,
                        file_name=file_name,
                        image_path=full_path,
                        description=description,
                        embedding=embedding,
                    )

                    inserted += 1
                    print(f"[OK] Inserat: {file_name}")

                except (UnidentifiedImageError, OSError) as img_err:
                    failed += 1
                    print(f"[ERR] Imagine invalidă '{file_name}': {img_err}")

                except Exception as ex:
                    failed += 1
                    print(f"[ERR] Nu am putut insera '{file_name}': {ex}")

            conn.commit()

    finally:
        conn.close()

    print("\nRezumat:")
    print(f"  Inserate: {inserted}")
    print(f"  Sărite:   {skipped}")
    print(f"  Eșuate:   {failed}")


if __name__ == "__main__":
    main()