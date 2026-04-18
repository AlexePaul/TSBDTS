DROP TABLE demo_vectors PURGE;

CREATE TABLESPACE vector_ts
DATAFILE 'vector_ts01.dbf' SIZE 500M
AUTOEXTEND ON NEXT 100M MAXSIZE 5G
EXTENT MANAGEMENT LOCAL
SEGMENT SPACE MANAGEMENT AUTO;

CREATE TABLE images_dataset (
    image_id     NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name    VARCHAR2(255),
    image_path   VARCHAR2(500),
    description  CLOB,
    embedding    VECTOR(512, FLOAT32)
) TABLESPACE vector_ts
LOB (description) STORE AS SECUREFILE (
    TABLESPACE vector_ts
);

select * from images_dataset;