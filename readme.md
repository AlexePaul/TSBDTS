# Smart IMAGE Search - Cautare semantica de imagini folosind Oracle AI Vector Search

Acest proiect este un motor simplu de cautare semantica a imaginilor. Foloseste CLIP pentru a genera descrieri vectoriale si Oracle AI Vector Search pentru a gasi cele mai relevante imagini dintr-o baza de date.

- Sandu Eduard Alexandru
- Alexe Vasile Paul
- Grupa: 505

## Ce face proiectul

- `load_dataset.py`: prelucreaza imaginile din folderul `dataset`, genereaza embedding-uri CLIP pentru fiecare imagine si le insereaza in tabela `images_dataset` din Oracle.
- `search_images.py`: construieste un embedding CLIP pentru textul introdus de utilizator si cauta in Oracle Database cele mai apropiate imagini folosind `VECTOR_DISTANCE(..., COSINE)`.
- `app.py`: interfata Streamlit pentru cautare interactiva, afiseaza rezultatele cu imagini, descriere si distanta.
- `embed_one_image.py`: un exemplu simplu care calculeaza embedding-ul pentru o singura imagine.

## Tehnologii folosite

- CLIP (`open_clip_torch`) pentru embedding de text si imagine
- Oracle Database 26ai + Oracle AI Vector Search pentru stocarea si interogarea vectorilor
- Streamlit pentru interfata web de cautare

## Configurare

1. Creaza un fisier `.env` in acelasi folder cu cheile:

```
DB_USER= Utilizator DB
DB_PASSWORD= Parola DB
DB_DSN= DB Server Name / FREEPDB1
```

2. Adaugarea imaginilor in folderul `dataset`.
3. Instalarea dependintelor:

```
pip install -r requirements.txt
```

4. Rularea `python load_dataset.py` incarca imaginile din folderul `dataset` in DB
5. Pornirea interfetei aplicatiei folosind

```
streamlit run app.py
```
