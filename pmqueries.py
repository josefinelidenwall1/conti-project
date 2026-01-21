#pmqueries

import psycopg2
from psycopg2.extras import RealDictCursor
from config import config
import json
from datetime import datetime,timedelta

def db_get_consultants(): #works
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'SELECT * FROM consultants;'
        cursor.execute(SQL)
        data = cursor.fetchall()
        cursor.close()
        return json.dumps({"consultant_list": data})
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

#print(db_get_consultants()) #tester

def get_hours(): 
    con = None
    try:
        con = psycopg2.connect(**config())
        cursor = con.cursor(cursor_factory=RealDictCursor)
        SQL = 'SELECT * FROM consultanthours;'
        cursor.execute(SQL)
        data = cursor.fetchall()
        cursor.close()
        return json.dumps({"totalhours_list": data}, default=str) #default str fixes datetime JSON serializable issue
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if con is not None:
            con.close()

#print(get_hours())

def insert_hours(consultant_id: int, starttime :datetime, endtime :datetime, lunchbreak : bool, customername: str):
    con = None
    try: 
        starttime = datetime.fromisoformat(starttime)
        endtime = datetime.fromisoformat(endtime)
       
        worktime= endtime-starttime #calculating totalwork hours with lunchbreak
        if lunchbreak:
            worktime-=timedelta(minutes=30)
        balance_minutes= round(worktime.total_seconds() / 60, 2) #divide by 3600 for hours, 60 for minutes

        con = psycopg2.connect(**config())
        cursor =con.cursor(cursor_factory=RealDictCursor)

        SQL = """
            INSERT INTO consultanthours (consultant_id,startingtime, endingtime,balance_minutes, lunchbreak,customername)
            VALUES (%s,%s,%s, %s,%s,%s)
            RETURNING consultant_id, startingtime,endingtime,balance_minutes,lunchbreak,customername """
        values=(consultant_id, starttime, endtime, balance_minutes, lunchbreak, customername)

        cursor.execute(SQL,values)
        inserted_row = cursor.fetchone()
        con.commit()
        cursor.close()
        return json.dumps(inserted_row, default =str)

    except (Exception, psycopg2.DatabaseError) as error:
        if con:
            con.rollback()
        print(error)
    finally:
        if con is not None:
            con.close()

print(insert_hours(2,'2025-01-12 09:00:00', '2025-01-12 16:30:00', False, 'staterailroads'))