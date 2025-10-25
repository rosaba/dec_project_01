{%
    set config = {
        "source_table_name":"crashes"
    }
%}

SELECT
crash_date,
crash_time,
borough,
zip_code
FROM {{config["source_table_name"]}};

