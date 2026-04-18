DROP TABLE demo_vectors PURGE;

CREATE TABLESPACE vector_ts
DATAFILE 'vector_ts01.dbf' SIZE 500M
AUTOEXTEND ON NEXT 100M MAXSIZE 5G
EXTENT MANAGEMENT LOCAL
SEGMENT SPACE MANAGEMENT AUTO;

CREATE TABLE demo_vectors (
    id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    label       VARCHAR2(100),
    embedding   VECTOR(3, FLOAT32)
);

CREATE TABLE images_dataset (
    image_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name    VARCHAR2(255),
    category     VARCHAR2(100),
    image_path   VARCHAR2(500),
    description  CLOB,
    embedding    VECTOR(512, FLOAT32)
) TABLESPACE vector_ts
LOB (description) STORE AS SECUREFILE (
    TABLESPACE vector_ts
);

select * from images_dataset;