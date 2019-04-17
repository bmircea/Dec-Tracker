import sqlite3

# Create DB, conn and cursor

conn = sqlite3.connect("store.db")
c = conn.cursor()

#Create tables
c.execute(''' CREATE TABLE CLIENTS
                ([generated_id] INTEGER PRIMARY KEY,[Client_Name] text, [Country_ID] integer, [Date] date)''')


conn.commit()
