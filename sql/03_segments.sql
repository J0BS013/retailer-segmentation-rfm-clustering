CREATE OR REPLACE TABLE rfm_segments AS
SELECT
    "Customer ID",
    r_score,
    f_score,
    m_score,
    rfm_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3                  THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2                  THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3                  THEN 'At Risk'
        ELSE                                                     'Lost'
    END AS segment
FROM rfm_scores;
