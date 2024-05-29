import sqlite3

cx = sqlite3.connect("swiss-bot.db")
cx.row_factory = sqlite3.Row

cx.executescript("""
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS projects (
  listing INTEGER,
  name TEXT PRIMARY KEY,
  assignment TEXT NOT NULL,
  process TEXT DEFAULT NULL,
  date DATE DEFAULT NULL,
  invite TEXT DEFAULT NULL,
  intro TEXT DEFAULT NULL,
  followup2 TEXT DEFAULT NULL,
  followup4 TEXT DEFAULT NULL,
  status BOOLEAN DEFAULT 0,
  followup2status BOOLEAN DEFAULT 0,
  followup4status BOOLEAN DEFAULT 0);
  
CREATE TABLE IF NOT EXISTS leaders (
  chat_id INTEGER,
  project_name TEXT,
  join_message INTEGER,
  UNIQUE(chat_id, project_name),
  FOREIGN KEY(project_name) REFERENCES projects(name) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS candidates (
  chat_id INTEGER PRIMARY KEY,
  project_name TEXT,
  daily_update INTEGER,
  daily_counter INTEGER DEFAULT 0,
  daily_message BOOLEAN DEFAULT FALSE,
  valid BOOLEAN DEFAULT TRUE, 
  UNIQUE(chat_id, project_name)
  FOREIGN KEY(project_name) REFERENCES projects(name) ON DELETE CASCADE);
""")
cx.commit()

def add_project(listing: int, name: str, assignment: str, process: str, date:str, invite:str, intro:str, status:bool=False, followup2:str="", followup4:str="", followup2status:bool=False, followup4status:bool=False) -> bool:
  cursor = cx.cursor()
  result = True
  try:
    cursor.execute(
            '''
            INSERT INTO projects (listing, name, assignment, process, date, invite, intro, followup2, followup4, status, followup2status, followup4status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (listing, name, assignment, process, date, invite, intro, followup2, followup4, status, followup2status, followup4status)
        )
    cx.commit()
  except sqlite3.IntegrityError as e:
    print("Project already added")
    result = False
  
  cursor.close()
  return result

def update_project(project_name: str, **kwargs):
  cursor = cx.cursor()
  result = True
  
  set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
    
  values = list(kwargs.values())
  
  values.append(project_name)
  
  try:
    cursor.execute(f'UPDATE projects SET {set_clause} WHERE listing = ?', values)
    cx.commit()
    print(f'UPDATE projects SET {set_clause} WHERE name = ?', values)
  except :
    print('''couldn't update the project''')
    result = False      
  
  cursor.close()
  return result

def search_project(project: str):
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM projects WHERE name = "{project}";')
  result = cursor.fetchone()

  cursor.close()
  return result

def query_get_one(query: str, params = ()):
  cursor = cx.cursor()
  cursor.execute(query, params)
  result = cursor.fetchone()

  cursor.close()
  return result

def query_get_many(query: str, params = ()):
  cursor = cx.cursor()
  cursor.execute(query, params)
  result = cursor.fetchall()

  cursor.close()
  return result

def query_update(query: str, params = ()):
  cursor = cx.cursor()
  result = True
  try:
    cursor.execute(query, params)
  except:
    result = False
  cx.commit()
  cursor.close()
  return result

def remove_project(project: str):
  cursor = cx.cursor()
  cursor.execute(f'DELETE FROM projects WHERE name = "{project}";')
  cx.commit()
  cursor.close()

def add_leader(chat_id: int, name: str) -> bool:
  cursor = cx.cursor()
  result = True
  try:
    cursor.execute(f'INSERT INTO leaders(chat_id, project_name) VALUES({chat_id}, "{name}");')
    cx.commit()
  except sqlite3.IntegrityError as e:
    print("Leader already added")
    result = False
  
  cursor.close()
  return result

def get_leaders(project_name: str) -> list:
  """ Get all leaders for a project """
  
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM leaders WHERE project_name = "{project_name}";')
  result = cursor.fetchall()

  cursor.close()
  return result

def search_leader(chat_id: int):
  cursor = cx.cursor()

  cursor.execute(f'SELECT * FROM leaders WHERE chat_id = {chat_id};')
  result = cursor.fetchone()

  cursor.close()
  return result

def update_leader(chat_id: int, join_message: int):
  cursor = cx.cursor()
  cursor.execute(f'UPDATE leaders SET join_message = {join_message} WHERE chat_id = {chat_id};')

  cx.commit()
  cursor.close()

def add_candidate(chat_id: int, name: str, daily_update: int) -> bool:
  cursor = cx.cursor()
  result = True
  try:
    # cursor.execute(f'INSERT INTO candidates(chat_id, project_name, daily_update) VALUES({chat_id}, "{name}", {daily_update});')
    cursor.execute('INSERT INTO candidates(chat_id, project_name, daily_update) VALUES(?, ?, ?);', 
                       (chat_id, name, daily_update))
    cx.commit()
  except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {e}")
        result = False
  except sqlite3.OperationalError as e:
        print(f"OperationalError: {e}")
        result = False
  except sqlite3.DatabaseError as e:
        print(f"DatabaseError: {e}")
        result = False
  finally:
        cursor.close()
  
  cursor.close()
  return result

def get_candidates(project_name: str) -> list:
  """ Get all candidates for a project """
  
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM candidates WHERE project_name = "{project_name}";')
  result = cursor.fetchall()

  cursor.close()
  return list(result)

def search_candidate(chat_id: int):
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM candidates WHERE chat_id = {chat_id};')
  result = cursor.fetchone()

  cursor.close()
  return result

def update_candidate(chat_id, daily_update = None, daily_counter = None, daily_message =  None, valid =  True):
  cursor = cx.cursor()
  cursor.execute(f"""
  UPDATE
    candidates 
  SET
    valid = {"TRUE" if valid else "FALSE"}
    {", daily_update = " + str(daily_update) if daily_update is not None else ""}
    {", daily_counter = " + str(daily_counter) if daily_counter is not None else ""}
    {", daily_message = " + str(daily_message).upper() if daily_message is not None else ""}
  WHERE
    chat_id = {chat_id};
  """)

  cx.commit()
  cursor.close()

def get_candidate_count(project_name: str):
  """ Get all candidate count for a project """
  cursor = cx.cursor()
  cursor.execute(f'SELECT COUNT(*) as "count" FROM candidates WHERE project_name = "{project_name}";')
  result = cursor.fetchone()

  cursor.close()
  return result

