import mysql.connector
import os

def conectar():
    db_host = os.environ['DB_HOST']
    db_user = os.environ['DB_USER']
    db_name = os.environ['DB_NAME']
    db_port = int(os.environ['DB_PORT']) 

    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        database=db_name,
        port=db_port 
    )
    return connection

