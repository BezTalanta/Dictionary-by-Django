import sqlite3

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
with open('transfered_data.txt', 'w') as file:
    for item in cur.execute('SELECT * FROM word_table WHERE user_id == 1').fetchall():
        file.write(str(item) + '\n')
print(f'{bcolors.OKGREEN}Saved to transfered_data.txt')