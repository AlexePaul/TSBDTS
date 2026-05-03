-- Verificarea datelor din tabelul demo_vectors
DROP TABLE demo_vectors PURGE;

-- Crearea unui nou tablespace pentru vectori
CREATE TABLESPACE vector_ts
DATAFILE 'vector_ts01.dbf' SIZE 500M
AUTOEXTEND ON NEXT 100M MAXSIZE 5G
EXTENT MANAGEMENT LOCAL
SEGMENT SPACE MANAGEMENT AUTO;

-- Crearea tabelului pentru stocarea datelor si vectorilor
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


-- Verificarea datelor din tabelul images_dataset
select * from images_dataset;