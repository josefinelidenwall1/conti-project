import psycopg2
import logging
from kv_secrets import get_database_credentials
from tabulate import tabulate



logger = logging.getLogger(__name__)

def connect():
    """Connect to the Azure PostgreSQL database using Key Vault secrets"""
    try:
        vault_url = "https://conti-vault.vault.azure.net/"
        host, database, user, password, port = get_database_credentials(vault_url)

        # using credentials to connect via psycopg2
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        
        logger.info("Database connection successful")
        return conn

    except Exception as error:
        logger.error(f"Database connection failed: {error}")
        return None

# ------------------------------------------------------------------------

# Test function to query columns in consultants table
def testing_report_conn():
    con=connect()
    if con is None:
        return
    
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM consultants LIMIT 0;")  

        # Extract and print only the column names
        columns = [desc[0] for desc in cursor.description]
        print(columns)

    finally:
        cursor.close()
        con.close()

# ------------------------------------------

def run_report():
    con=connect()
    if con is None:
        return
    report_file = "consultant_report.txt"

    try:
        with open(report_file, "w") as f:
            f.write("="*80 + "\n")
            f.write("      CONTI - CONSULTANT TIME REPORT \n")
            f.write("="*80 + "\n\n")

            with con.cursor() as cursor:
                # ---  CONSULTANT PERFORMANCE table ---
                f.write("1. CONSULTANT PERFORMANCE SUMMARY\n")
                sql_query2 = """
                SELECT 
                    c.consultant_name,
                    TO_CHAR(h.startingTime, 'Month') AS month_name,
                    ROUND(SUM(h.balance_minutes) / 60.0, 2) AS total_monthly_hours,
                    ROUND((SUM(h.balance_minutes) / 60.0) / 4.0, 2) AS avg_weekly_hours,
                    ROUND((SUM(h.balance_minutes) / 60.0) / 20.0, 2) AS avg_daily_hours
                FROM consultanthours h
                JOIN consultants c ON h.consultant_id = c.consultant_id
                GROUP BY 1, 2
                ORDER BY 1, 2;
                """
                cursor.execute(sql_query2)
                headers2 = [desc[0] for desc in cursor.description]
                f.write(tabulate(cursor.fetchall(), headers=headers2, tablefmt="psql") + "\n\n")

                # --- CUSTOMER BILLING SUMMARY table ---
                f.write("2. CUSTOMER BILLING & WEEKLY LOAD\n")
                sql_query3 = """
                SELECT 
                    customername AS company_name,
                    TO_CHAR(startingTime, 'Month') AS month_name,
                    ROUND(SUM(balance_minutes) / 60.0, 2) AS total_monthly_hours,
                    ROUND((SUM(balance_minutes) / 60.0) / 4.0, 2) AS avg_weekly_hours,
                    ROUND(SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) = 1 THEN balance_minutes ELSE 0 END) / 60.0, 2) AS week_1,
                    ROUND(SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) = 2 THEN balance_minutes ELSE 0 END) / 60.0, 2) AS week_2,
                    ROUND(SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) = 3 THEN balance_minutes ELSE 0 END) / 60.0, 2) AS week_3,
                    ROUND(SUM(CASE WHEN CEIL(EXTRACT(DAY FROM startingTime) / 7.0) >= 4 THEN balance_minutes ELSE 0 END) / 60.0, 2) AS week_4_plus
                FROM consultanthours
                GROUP BY 1, 2 -- group by company_name and month_name
                ORDER BY 2, 1;  -- order by month_name then company_name
                """
                cursor.execute(sql_query3)
                headers3 = [desc[0] for desc in cursor.description]
                f.write(tabulate(cursor.fetchall(), headers=headers3, tablefmt="psql") + "\n\n")

                # --- DETAILED WEEKLY TIME MATRIX table ---
                f.write("3. DETAILED WEEKLY TIME MATRIX\n")
                query1 = """
                WITH WeeklyMatrix AS (
                SELECT 
                    c.consultant_name,
                    h.customername AS company_name,
                    TO_CHAR(h.startingTime, 'Month') AS month_name,  
                    'Week ' || CAST(CEIL(EXTRACT(DAY FROM h.startingTime) / 7.0) AS INTEGER) AS week_number,
                
                    ROUND(SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 1 THEN h.balance_minutes ELSE 0 END) / 60.0, 2) AS Mon,
                    ROUND(SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 2 THEN h.balance_minutes ELSE 0 END) / 60.0, 2) AS Tue,
                    ROUND(SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 3 THEN h.balance_minutes ELSE 0 END) / 60.0, 2) AS Wed,
                    ROUND(SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 4 THEN h.balance_minutes ELSE 0 END) / 60.0, 2) AS Thu,
                    ROUND(SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 5 THEN h.balance_minutes ELSE 0 END) / 60.0, 2) AS Fri,
                
                    ROUND(SUM(h.balance_minutes) / 60.0, 2) AS total_weekly_hours
                FROM consultanthours AS h
                JOIN consultants AS c ON h.consultant_id = c.consultant_id
                GROUP BY 1, 2, 3, 4
                )
                SELECT *,
                ROUND(SUM(total_weekly_hours) OVER (
                    PARTITION BY company_name, month_name  
                    ORDER BY week_number
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ), 2) AS customer_cumulative_to_date
                FROM WeeklyMatrix
                ORDER BY company_name, week_number;
                """
                
                cursor.execute(query1)
                
                headers = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                
                # Using tabulate and converting to psql format to create a nice table
                pretty_table = tabulate(data, headers=headers, tablefmt="psql")
                
                f.write("High Level Consultant Time Report\n")
                f.write(pretty_table)
                f.write("\n\n" + "="*80 + "\n\n")

            print(f"Successfully generated {report_file}")

    except Exception as e:
        print(f"Query failed: {e}")

    finally:
        con.close()





if __name__ == "__main__":
    testing_report_conn()
    run_report()





