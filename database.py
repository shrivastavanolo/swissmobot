from time import sleep
import sqlite3
from datetime import datetime
import aiosqlite

# database -> intern.db
# table -> projects
# primary key -> project_name, listing
    
database = 'intern.db'
table = 'projects'

def list_tables():
    conn = sqlite3.connect('intern.db')
    c = conn.cursor()
    # getting list of all tables on the database
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()

    print(tables)
    print(len(tables))

def create_table():
    conn = sqlite3.connect('intern.db')
    c = conn.cursor()
    # TODO add user_id 
    c.execute(f'''
              CREATE TABLE IF NOT EXISTS {table} (
                listing INTEGER PRIMARY KEY,
                project_name TEXT NOT NULL,
                process TEXT DEFAULT NULL,
                invite TEXT DEFAULT NULL,
                intro TEXT DEFAULT NULL,
                assignment TEXT DEFAULT NULL,
                followup2 TEXT DEFAULT NULL,
                followup4 TEXT DEFAULT NULL,
                status TEXT DEFAULT "INACTIVE",
                date DATE DEFAULT NULL,
                followup2status TEXT DEFAULT "INACTIVE",
                followup4status TEXT DEFAULT "INACTIVE"
            );
        ''')
    pass
    
async def add_one(listing:int,project_name:str, process:str=None, invite:str=None, intro:str=None, assignment:str=None, followup2:str=None, followup4:str=None, status:str=None, date:datetime=datetime.now(), followup2status:str=None, followup4status:str=None) -> None:
    conn = await aiosqlite.connect(database)
    c = await conn.cursor()

    await c.execute(f'''INSERT INTO {table} 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (listing, project_name, process, invite, intro, assignment, followup2, followup4, status, date, followup2status, followup4status))
    
    await conn.commit()
    
    await c.close()
    await conn.close()


async def search(listing: int):
    conn = await aiosqlite.connect(database)
    c = await conn.cursor()

    print(f"SELECT * FROM {table} WHERE listing = {listing}")
    await c.execute(f"SELECT * FROM {table} WHERE listing = {listing}")
    
    items = await c.fetchall()

    await conn.close()
    return items

def search_regular(listing: int):
    conn = sqlite3.connect(database)
    c = conn.cursor()

    print(f"SELECT * FROM {table} WHERE listing = {listing}")
    c.execute(f"SELECT * FROM {table} WHERE listing = {listing}")
    
    items = c.fetchall()

    conn.close()
    return items
 
def show_all():
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute(f"SELECT * from {table}")
    items = c.fetchall()
        
    conn.commit()
    conn.close()
    # clean_print(items)
    return items

async def get_all_active_projects():
    conn = await aiosqlite.connect(database)
    c = await conn.cursor()
    await c.execute(f"SELECT listing from {table}")
    items = await c.fetchall()
        
    await conn.commit()
    await conn.close()
    # clean_print(items)
    return items

def delete_record(listing: int) -> None:
    conn = sqlite3.connect(database)
    c = conn.cursor()

    c.execute("DELETE FROM projects WHERE listing = ?", (listing,))

    conn.commit()
    c.close()
    conn.close()

async def update(listing: str, **kwargs):
    print('Updating ...', '🍎'*7)
    # sleep(3)
    conn = await aiosqlite.connect(database)
    c = await conn.cursor()

    # Constructing the SET clause dynamically based on the provided key-value pairs
    set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
    
    # Collecting the values to be updated
    values = list(kwargs.values())
    
    # Adding the listing for the WHERE clause
    values.append(listing)
    
    print(f'UPDATE projects SET {set_clause} WHERE listing = ?', values)
    # Constructing and executing the SQL query
    await c.execute(f'UPDATE projects SET {set_clause} WHERE listing = ?', values)

    await conn.commit()

    await c.close()
    await conn.close()

def clean_print(items):
    record_count = 1
    cols = ['listing','project_name', 'process', 'invite', 'intro', 'assignment', 'followup2', 'followup4', 'status', 'date', 'followup2status', 'followup4status']
    
    if items == []:
        print('Empty')
        return 
    
    for item in items:
        print("RECORD: #", record_count)
        for i in range(0, len(cols)):
            print(cols[i] + ":" , end=" ")
            print(item[i])
        # print(f'ClientID: {item[0]} \nNormalCredits: {item[1]} \nAdvanceCredits: {item[2]} \nPremium: {item[3]} \nLastSearchDate: {item[4]} \nSearchCount: {item[5]} \nClientName: {item[6]} \nTimeOfEntry: {item[7]} \nSubscribedDate: {item[8]} \nSpecialOffer: {item[9]} \nEnterPremium: {item[10]} \nContactCredit: {item[11]} \nCustomerId: {item[12]} \nRefId: {item[13]} \nBalance: {item[14]}')
        record_count+=1
        print('\n\n')

# create_table()
# list_tables()

# delete_record(123)
# delete_record(456)

# add_one(2472281,'newtest','assignment','new' 'test','new' 'test','new' 'test','new' 'test','mew' 'test','active','2024-05-01','Inactive','Inactive')
# add_one(123, 'p1', 'assignment', 'inv', 'int', 'assignment', 'flw2', 'flw4', 'active', '2024-04-30', 'inactive', 'inactive')
# add_one(456, 'p2', 'assignment', 'inv', 'int', 'assignment', 'flw2', 'flw4', 'active', '2024-04-28', 'inactive', 'inactive')
# add_one(789, 'p2', 'assignment', 'inv', 'int', 'assignment', 'flw2', 'flw4', 'active', '2024-04-28', 'active', 'inactive')


# clean_print(search(24721))
# update(123, followup2status='inactive')
# clean_print(show_all())
# search_res = search_regular(2462410) 
# print(search_res)