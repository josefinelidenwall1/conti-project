

-- TABLE SCHEMA

--    id SERIAL PRIMARY KEY,
--    startingTime TIMESTAMP, 
--    endingTime TIMESTAMP, 
--    totalHours INT,  -- calculated
--    lunchbreak BOOLEAN DEFAULT FALSE, 
--    consultantName VARCHAR (100),
--    customername VARCHAR (100)


-- Query 1 - General Matrix showing consultants hours for a specific month, broken down in weeks inc the company
WITH WeeklyMatrix AS (
    SELECT 
        consultant_name,
        company_name,
        strftime(clock_in, '%B') AS month_name,  
        'Week ' || CAST(CEIL(EXTRACT(DAY FROM clock_in) / 7.0) AS INTEGER) AS week_number,
        SUM(CASE WHEN strftime(clock_in, '%w') = '1' THEN 
            CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END ELSE 0 END) / 60.0 AS Mon,
        SUM(CASE WHEN strftime(clock_in, '%w') = '2' THEN 
            CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END ELSE 0 END) / 60.0 AS Tue,
        SUM(CASE WHEN strftime(clock_in, '%w') = '3' THEN 
            CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END ELSE 0 END) / 60.0 AS Wed,
        SUM(CASE WHEN strftime(clock_in, '%w') = '4' THEN 
            CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END ELSE 0 END) / 60.0 AS Thu,
        SUM(CASE WHEN strftime(clock_in, '%w') = '5' THEN 
            CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END ELSE 0 END) / 60.0 AS Fri,
        -- Total weekly 
        SUM(CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) / 60.0 AS total_weekly_hours
    FROM 'mock-data.csv'
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


-- Query for average weekly and daily hours

WITH weekly_totals AS (
    SELECT 
        consultant_name,
        strftime(clock_in, '%B') AS month_name,
        CEIL(EXTRACT(DAY FROM clock_in) / 7.0) AS week_num,
        SUM(CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) / 60.0 AS hours_in_this_week
    FROM 'mock-data.csv'
    GROUP BY consultant_name, month_name, week_num
)
SELECT 
    consultant_name,
    month_name,
    SUM(hours_in_this_week) AS total_monthly_hours,
    AVG(hours_in_this_week) AS avg_weekly_hours,
    AVG(hours_in_this_week) / 5.0 AS avg_daily_hours
FROM weekly_totals
GROUP BY consultant_name, month_name;



-- Query for customer information

SELECT 
    company_name,
    SUM(CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) / 60.0 AS total_monthly_hours,
    (SUM(CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) / 60.0) / 4.0 AS avg_weekly_hours,
    -- Weekly Breakdown
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM clock_in) / 7.0) = 1 THEN 
        (CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) ELSE 0 END) / 60.0 AS week_1_hours,
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM clock_in) / 7.0) = 2 THEN 
        (CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) ELSE 0 END) / 60.0 AS week_2_hours,
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM clock_in) / 7.0) = 3 THEN 
        (CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) ELSE 0 END) / 60.0 AS week_3_hours,
    SUM(CASE WHEN CEIL(EXTRACT(DAY FROM clock_in) / 7.0) = 4 THEN 
        (CASE WHEN "lunch-break" = 'Yes' THEN total_minutes - 30 ELSE total_minutes END) ELSE 0 END) / 60.0 AS week_4_hours
FROM 'mock-data.csv'
GROUP BY company_name
ORDER BY total_monthly_hours DESC;