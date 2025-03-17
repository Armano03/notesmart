import pymysql

conn = pymysql.connect(
    host='localhost',
    user='notesmart_user',
    password='your_password',
    database='notesmart'
)
print("Connection successful!")
conn.close()