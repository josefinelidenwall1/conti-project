import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta, date
from report_queries import connect 
from pmqueries import calculate_billable_minutes

# Initialize Faker
fake = Faker()
Faker.seed(1337)
random.seed(1337)

def clean_database(con):
    """
    Wipes the data so script can be re-run.
    """
    print("--- Cleaning database ---")
    tables = ['consultanthours', 'consultants']
    with con.cursor() as cur:
        for table in tables:
            cur.execute(f"TRUNCATE TABLE {table} CASCADE;")
    con.commit()
    print("Tables truncated.")

def create_consultants(con, num_consultants=5):
    """
    Generates N consultants and returns a list of their IDs.
    """
    consultant_ids = []
    print(f"--- Generating {num_consultants} Consultants ---")
    
    sql = "INSERT INTO consultants (consultant_name) VALUES (%s) RETURNING consultant_id;"
    
    with con.cursor() as cur:
        for _ in range(num_consultants):
            name = fake.name()
            cur.execute(sql, (name,))
            # Fetch the new ID to use for the hours table
            new_id = cur.fetchone()[0]
            consultant_ids.append(new_id)
    
    con.commit()
    return consultant_ids

def generate_customer_names(n=5):
    """Generates a list of company names to assign randomly."""
    companies = []
    for _ in range(n):
        companies.append(fake.company())
    return companies

def populate_consultanthours(con, consultant_ids, start_date, days_to_generate=30):
    """
    Populates work hours for the given consultants.
    - Monday to Friday only.
    - 4 to 8 hours randomly.
    """
    print(f"--- Generating Work Hours for {len(consultant_ids)} Consultants ---")
    
    customers = generate_customer_names(5)
    
    # SQL matching schema
    sql = """
        INSERT INTO consultanthours 
        (consultant_id, startingTime, endingTime, balance_minutes, lunchbreak, customername)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    with con.cursor() as cur:
        for cid in consultant_ids:
            current_date = start_date
            
            for _ in range(days_to_generate):
                # Check if Mon (0) to Fri (4)
                if current_date.weekday() < 5:
                    
                    # 1. Randomize Work Specs
                    hours_worked = random.randint(4, 8) # Random int 4-8
                    take_lunch = random.choice([True, False])
                    assigned_customer = random.choice(customers)
                    
                    # 2. Randomize Start Time (e.g., between 08:00 and 10:00)
                    start_hour = random.randint(8, 10)
                    start_minute = random.choice([0, 15, 30, 45])
                    
                    start_dt = datetime.combine(
                        current_date, 
                        datetime.min.time()
                    ).replace(hour=start_hour, minute=start_minute)
                    
                    # 3. Calculate End Time
                    # Base work duration
                    duration = timedelta(hours=hours_worked)
                    if take_lunch:
                        duration += timedelta(minutes=30)
                    
                    end_dt = start_dt + duration
                    
                    balance_minutes = calculate_billable_minutes(start_dt, end_dt, take_lunch)
                    
                    # 4. Insert Data
                    # Note: Schema has totalHours as INT, so we pass hours_worked (int)
                    values = (
                        cid, 
                        start_dt, 
                        end_dt, 
                        balance_minutes, 
                        take_lunch, 
                        assigned_customer
                    )
                    cur.execute(sql, values)
                
                # Move to next day
                current_date += timedelta(days=1)
                
    con.commit()
    print("Work hours populated.")

def main(con):
    try:
        if con:
            print("\n--- Connected to database ---")
            
            # 1. Clean old data
            clean_database(con)

            # 2. Create Consultants and get their IDs
            # IDs first because consultanthours has a Foreign Key constraint
            c_ids = create_consultants(con, num_consultants=15)
            
            # 3. Populate Hours using those IDs
            # Generate data starting from roughly 1 month ago
            start_date = date.today() - timedelta(days=30)
            populate_consultanthours(con, c_ids, start_date, days_to_generate=30)
            
            print("Database population complete.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if con:
            con.rollback()

if __name__ == "__main__":
    try:
        # Use the imported connect function
        connection = connect()
        if connection:
            main(connection)
        else:
            print("Failed to obtain a database connection.")
    except Exception as e:
        print(f"Execution failed: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()