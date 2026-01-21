import duckdb
import os

base_path = os.path.dirname(__file__)
csv_path = os.path.join(base_path, 'mock-data.csv')
con_path = os.path.join(base_path, 'mock_data_con.csv')


sql_query = f"""
WITH WeeklyMatrix AS (
    SELECT 
        c.consultant_name,
        h.customername AS company_name,
        strftime(h.startingTime, '%B') AS month_name,  
        'Week ' || CAST(CEIL(EXTRACT(DAY FROM h.startingTime) / 7.0) AS INTEGER) AS week_number,
        
        -- Simplified logic using balance_minutes / 60.0
        SUM(CASE WHEN strftime(h.startingTime, '%w') = '1' THEN h.balance_minutes ELSE 0 END) / 60.0 AS Mon,
        SUM(CASE WHEN strftime(h.startingTime, '%w') = '2' THEN h.balance_minutes ELSE 0 END) / 60.0 AS Tue,
        SUM(CASE WHEN strftime(h.startingTime, '%w') = '3' THEN h.balance_minutes ELSE 0 END) / 60.0 AS Wed,
        SUM(CASE WHEN strftime(h.startingTime, '%w') = '4' THEN h.balance_minutes ELSE 0 END) / 60.0 AS Thu,
        SUM(CASE WHEN strftime(h.startingTime, '%w') = '5' THEN h.balance_minutes ELSE 0 END) / 60.0 AS Fri,
        
        SUM(h.balance_minutes) / 60.0 AS total_weekly_hours
    FROM '{csv_path}' h
    JOIN '{con_path}' c ON h.consultant_id = c.consultant_id
    GROUP BY 1, 2, 3, 4
)
SELECT 
    *,
    SUM(total_weekly_hours) OVER (
        PARTITION BY company_name, month_name  
        ORDER BY week_number
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS customer_cumulative_to_date
FROM WeeklyMatrix
ORDER BY company_name, week_number;
"""

sql_query2=f"""
SELECT 
    c.consultant_name,
    strftime(h.startingTime, '%B') AS month_name, -- 1. Total Monthly Hours
    SUM(h.balance_minutes) / 60.0 AS total_monthly_hours, -- 2. Average Weekly (Total / 4 weeks)
    (SUM(h.balance_minutes) / 60.0) / 4.0 AS avg_weekly_hours, -- 3. Average Daily (Total / 20 working days in a month)
    (SUM(h.balance_minutes) / 60.0) / 20.0 AS avg_daily_hours
FROM '{csv_path}' h
JOIN '{con_path}' c ON h.consultant_id = c.consultant_id
GROUP BY 1, 2;
"""

sql_query3=f"""
SELECT 
    customername AS company_name,
    -- 1. Totals and Averages
    SUM(balance_minutes) / 60.0 AS total_monthly_hours,
    (SUM(balance_minutes) / 60.0) / 4.0 AS avg_weekly_hours,
    
    -- 2. Weekly Breakdown (Simplified Pivoting)
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) = 1 THEN balance_minutes ELSE 0 END) / 60.0 AS week_1,
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) = 2 THEN balance_minutes ELSE 0 END) / 60.0 AS week_2,
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) = 3 THEN balance_minutes ELSE 0 END) / 60.0 AS week_3,
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) >= 4 THEN balance_minutes ELSE 0 END) / 60.0 AS week_4_plus
FROM '{csv_path}'
GROUP BY 1
ORDER BY total_monthly_hours DESC;
"""

# Run the query and show the results in a nice table
print("--- WEEKLY REPORT TEST ---")
duckdb.sql(sql_query).show()
duckdb.sql(sql_query2).show()
duckdb.sql(sql_query3).show()