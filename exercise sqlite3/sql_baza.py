import sqlite3
connection = sqlite3.connect("baza1.db")

cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS player (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,surname TEXT )")


cursor.execute("CREATE TABLE IF NOT EXISTS round (date DATE, name TEXT, id INTEGER PRIMARY KEY AUTOINCREMENT, no INTEGER)")


cursor.execute("CREATE TABLE IF NOT EXISTS match (id INTEGER  PRIMARY KEY AUTOINCREMENT, round_id INTEGER, player_id INTEGER, order_no INTEGER, FOREIGN KEY (round_id) REFERENCES round(id), FOREIGN KEY (player_id) REFERENCES player(id))")

cursor.execute("CREATE TABLE IF NOT EXISTS results (match_id INTEGER, player_won INTEGER, player_loss INTEGER, result TEXT, FOREIGN KEY (player_won) REFERENCES player(id), FOREIGN KEY (player_loss) REFERENCES player(id))")


connection.commit()

