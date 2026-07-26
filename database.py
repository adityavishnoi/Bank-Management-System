import psycopg2

def connect_to_database():
    try:
        con=psycopg2.connect(
            host="localhost",
            database="bank",
            user="postgres",
            password="",
            port="5432"
        )
        if con:
            print("Connection established!!")
        return con
    except Exception as err:
        print("Connection failed!!: ",err)
        return None
if __name__=="__main__":
    conn=connect_to_database()
    if conn:
        conn.close()
        print("connection closed")