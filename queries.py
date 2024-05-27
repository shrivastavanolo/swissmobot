import sqlite3

cx = sqlite3.connect("swiss-bot.db")
cx.row_factory = sqlite3.Row

cx.executescript("""
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS projects (
  listing INTEGER,
  name TEXT PRIMARY KEY,
  assignment TEXT,
  process TEXT DEFAULT NULL,
  date DATE DEFAULT NULL,
  invite TEXT DEFAULT NULL,
  intro TEXT DEFAULT NULL,
  followup2 TEXT DEFAULT NULL,
  followup4 TEXT DEFAULT NULL,
  status TEXT DEFAULT "INACTIVE",
  followup2status TEXT DEFAULT "INACTIVE",
  followup4status TEXT DEFAULT "INACTIVE");
  
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
  FOREIGN KEY(project_name) REFERENCES projects(name) ON DELETE CASCADE);
""")


cx.commit()

def add_project(project: str, assignment: str) -> bool:
  cursor = cx.cursor()
  result = True
  try:
    cursor.execute(f'INSERT INTO projects(name, assignment) VALUES("{project}", "{assignment}");')
    cx.commit()
  except sqlite3.IntegrityError as e:
    print("Project already added")
    result = False
  
  cursor.close()
  return result

def search_project(project: str):
  cursor = cx.cursor()
  cursor.execute(f'SELECT * FROM projects WHERE name = "{project}";')
  result = cursor.fetchone()

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

