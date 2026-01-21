#timemanagement software

#inputs:
#1) consultant_id -> basically same as consultant name for program, but unique which name is not necessarily
#2)starttime -check in YYYY-MM-DD HH:MM:SS
#3)endtime -check out YYYY-MM-DD HH:MM:SS
#4)lunchbreak Bool ; -> if lunchbreak, subtract 30min from total time
#5)customername str

#TO DO: ADD Excepts

import queries
import psycopg2
import config 
from datetime import datetime,timedelta

#JN -we will assume that profiles already exists in db? so we can just connect to this
def worked_hours(consultant_id: int, starttime :datetime, endtime :datetime, lunchbreak : bool, customername: str):
    con = None
    try: 
        starttime = datetime.fromisoformat(starttime)
        endtime = datetime.fromisoformat(endtime)
       
        worktime= endtime-starttime #calculating totalwork hours with lunchbreak
        if lunchbreak:
            worktime-=timedelta(minutes=30)
        totalhours= round(worktime.total_seconds() / 60, 2) #divide by 3600 for hours, 60 for minutes

        con = psycopg2.connect(**config.config())
        cursor =con.cursor()

        SQL = """
            INSERT INTO consultanthours (consultant_id,startingtime, endingtime,totalhours, lunchbreak,customername)
            VALUES (%s,%s,%s, %s,%s,%s)"""
        values=(consultant_id, starttime, endtime,totalhours, lunchbreak, customername)

        cursor.execute(SQL,values)
        con.commit()
        print('workday information updated')

        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        if con:
            con.rollback()
        print(error)
    finally:
        if con is not None:
            con.close()

worked_hours(4,'2025-01-07 11:00:00', '2025-01-07 16:30:00', False, 'bankcustomer2')