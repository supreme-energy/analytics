import pymysql


def connection():
    conn = pymysql.connect(host='35.202.91.126',
                         user='postgres',
                         password='sses2019',
                         db='postgres')

    c=conn.cursor()

    return c, conn
