CREATE TABLE IF NOT EXISTS search_job (
    id SERIAL PRIMARY KEY,

    url TEXT NOT NULL,
    max_items INTEGER NOT NULL,
    status TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL,

    error TEXT
);

CREATE TABLE IF NOT EXISTS offer (
    id SERIAL PRIMARY KEY,

    search_id INTEGER NOT NULL,

    titre TEXT,
    link TEXT NOT NULL UNIQUE,

    sector TEXT,
    experience TEXT,
    region TEXT,
    formation TEXT,
    competences_personnelles TEXT,

    contrat TEXT,
    teletravail TEXT,

    description TEXT,
    date_limite TEXT,

    CONSTRAINT fk_offer_search_job
        FOREIGN KEY (search_id)
        REFERENCES search_job(id)
);