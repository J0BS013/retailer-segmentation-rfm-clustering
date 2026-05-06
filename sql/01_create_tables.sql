CREATE TABLE IF NOT EXISTS rfm_features (
    "Customer ID" VARCHAR,
    frequency     INTEGER,
    monetary      DOUBLE,
    recency       INTEGER
);

CREATE TABLE IF NOT EXISTS rfm_scores (
    "Customer ID" VARCHAR,
    frequency     INTEGER,
    monetary      DOUBLE,
    recency       INTEGER,
    r_score       INTEGER,
    f_score       INTEGER,
    m_score       INTEGER,
    rfm_score     INTEGER
);

CREATE TABLE IF NOT EXISTS rfm_segments (
    "Customer ID" VARCHAR,
    r_score       INTEGER,
    f_score       INTEGER,
    m_score       INTEGER,
    rfm_score     INTEGER,
    segment       VARCHAR
);
