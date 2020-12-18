import pymysql

# MySQL Connection 연결
def select(abc):
    conn = pymysql.connect(host='54.180.101.122', user='root', password='Aa@123456', db='gesture', port = 3306)
    # Connection 으로부터 Cursor 생성
    curs = conn.cursor() #pymysql.cursors.DictCursor
    # SQL문 실행
    sql = "select "+ abc +" from blindOn"
    curs.execute(sql)
    rows = curs.fetchall()    # 데이타 Fetch

    rows = list(rows)
    b = []
    c = []
    for i in range(len(rows)):
        b.append(list(rows[i]))
    for i in range(len(b)):
        c.append(b[i][0])
    conn.commit()
    conn.close()
    return c


def insert(a,b,c,d,e,f,g,h,i,j):
    conn = pymysql.connect(host='54.180.101.122', user='root', password='Aa@123456', db='gesture', port = 3306)
    curs = conn.cursor()
    ##################
    sql = "insert into windowOn (AccX1, AccY1, AccZ1, GyX1, GyY1, GyZ1, FlexA1, FlexB1, FlexC1, FlexD1) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    curs.execute(sql, (a,b,c,d,e,f,g,h,i,j))
    conn.commit()
    conn.close()

def deleteAll():
    conn = pymysql.connect(host='54.180.101.122', user='root', password='Aa@123456', db='gesture', port=3306)
    curs = conn.cursor()
    sql = "delete from blindOn"
    curs.execute(sql)
    conn.commit()
    conn.close()


#insert()
#select()
#deleteAll()
#select()