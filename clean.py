import sqlite3

def delete_table(database_name, table_name):
    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE IF EXISTS {table_name};')

        conn.commit()
        conn.close()
        
        print(f"Table '{table_name}' deleted successfully.")
    except sqlite3.Error as e:
        print("Error deleting table:", e)

# Example usage:
delete_table('swiss-bot.db','candidates')
# delete_table('swiss-bot.db','leaders')
# delete_table('swiss-bot.db','projects')
