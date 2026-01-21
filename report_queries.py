import psycopg2
import logging
from decimal import Decimal
from kv_secrets import get_database_credentials



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
            f.write("--- Consultant Time Report ---\n")

            with con.cursor() as cursor:
                f.write("High Level Consultant Time Report")
                query1 = """
                WITH WeeklyMatrix AS (
                SELECT 
                c.consultant_name,
                h.customername AS company_name,
                TO_CHAR(h.startingTime, 'Month') AS month_name,  
                'Week ' || CAST(CEIL(EXTRACT(DAY FROM h.startingTime) / 7.0) AS INTEGER) AS week_number,
            
                SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 1 THEN h.balance_minutes ELSE 0 END) / 60.0 AS Mon,
                SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 2 THEN h.balance_minutes ELSE 0 END) / 60.0 AS Tue,
                SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 3 THEN h.balance_minutes ELSE 0 END) / 60.0 AS Wed,
                SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 4 THEN h.balance_minutes ELSE 0 END) / 60.0 AS Thu,
                SUM(CASE WHEN EXTRACT(ISODOW FROM h.startingTime) = 5 THEN h.balance_minutes ELSE 0 END) / 60.0 AS Fri,
            
                SUM(h.balance_minutes) / 60.0 AS total_weekly_hours
                FROM consultanthours AS h
                JOIN consultants AS c ON h.consultant_id = c.consultant_id
                GROUP BY 1, 2, 3, 4
                )
                SELECT *,
                SUM(total_weekly_hours) OVER (
                PARTITION BY company_name, month_name  
                ORDER BY week_number
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS customer_cumulative_to_date
                FROM WeeklyMatrix
                ORDER BY company_name, week_number;
                """

                cursor.execute(query1)


                # Fetching data and writing to file
                #format number before writing 
                for row in cursor.fetchall():
                    formatted_row = []
                    for item in row:
                        # Check if the item is a number (Decimal or float)
                        if isinstance(item, (Decimal, float)):
                            # Format to 2 decimal places (e.g., "4.00")
                            formatted_row.append(f"{item:.2f}")
                        elif item is None:
                            formatted_row.append("0.00")
                        else:
                            formatted_row.append(str(item))
                    
                    f.write(" | ".join(formatted_row) + "\n")
                f.write("\n" + "="*50 + "\n\n")

            print(f"Successfully generated {report_file}")

    except Exception as e:
        print(f"Query failed: {e}")

    finally:
        con.close()





if __name__ == "__main__":
    testing_report_conn()
    run_report()





