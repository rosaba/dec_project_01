{%
    set config = {
        "source_table_name":"crashes"
    }
%}

SELECT key AS column, COUNT(*) AS null_values
FROM {{config["source_table_name"]}} t
CROSS JOIN jsonb_each_text(to_jsonb(t))
WHERE value IS NULL
GROUP BY key
ORDER BY null_values DESC; 