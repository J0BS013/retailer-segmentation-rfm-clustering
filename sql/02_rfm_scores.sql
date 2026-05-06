CREATE OR REPLACE TABLE rfm_scores AS
SELECT
    "Customer ID",
    frequency,
    monetary,
    recency,
    -- Score 5 = best. NTILE assigns 1 to the first rows in sort order,
    -- so we sort each dimension so that the WORST values come first.
    -- Recency:  worst = many days ago  → ORDER BY DESC (738 days first → score 1)
    -- Frequency: worst = few orders    → ORDER BY ASC  (1 order first → score 1)
    -- Monetary:  worst = low spend     → ORDER BY ASC  (£2 first → score 1)
    NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
FROM rfm_features;

ALTER TABLE rfm_scores
ADD COLUMN rfm_score INTEGER;

UPDATE rfm_scores
SET rfm_score = r_score + f_score + m_score;
