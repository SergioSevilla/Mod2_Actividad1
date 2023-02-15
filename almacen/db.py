import sqlite3

def connect_db (p_database_file):
    '''
    Returns a valid conexion object to the database located in the given file

    :param value: name of the database file
    '''
    con = sqlite3.connect(p_database_file, check_same_thread=False)

    return con

def initialize_db(conexion):
    '''
    Create required tables in the db

    :param value: conexion to the db
    '''
    cur = conexion.cursor()

    res = cur.execute("SELECT name FROM sqlite_master WHERE name='articles'")
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE articles(article_id INTEGER PRIMARY KEY, article_name NOT NULL, description, stock_units DEFAULT 0, available DEFAULT 'Y')")
        conexion.commit()

    res = cur.execute("SELECT name FROM sqlite_master WHERE name='consumers'")
    if (res.fetchone() is None):
        cur.execute("CREATE TABLE consumers(consumer_id INTEGER PRIMARY KEY, consumer NOT NULL, api_key NOT NULL)")
        conexion.commit()

def populate_tables(conexion, default_consumer, default_api_key):
    '''
    Inserts some rows into articles table

    :param value: conexion to the db
    '''
    cur = conexion.cursor()
    statement = "SELECT count(*) FROM articles"
    res=cur.execute(statement)
    if (res.fetchone() == (0,)):
        data = [
                (1, 'article1', 'desc of article1', 101, 'Y'),
                (2, 'article2', 'desc of article2', 122, 'Y'),
                (3, 'article3', 'desc of article3', 333, 'N')
                ]
        statement  = "INSERT INTO articles VALUES(?, ?, ?, ?, ?)"
        cur.executemany(statement, data)
        conexion.commit()

    statement = "SELECT count(*) FROM consumers"
    res=cur.execute(statement)
    if (res.fetchone() == (0, )):
        data = (1, default_consumer, default_api_key)
        statement  = "INSERT INTO consumers VALUES(?, ?, ?)"
        cur.execute(statement, data)
        conexion.commit()

def get_all_rows_articles (conexion):
    '''
    Returns all the rows of the articles table

    :param value: conexion to the db
    '''
    cur = conexion.cursor()
    datos_json=[]
    for row in cur.execute("SELECT * FROM articles"):
        datos_json.append({'article_id' : row[0],'article_name' : row[1], 'description' : row[2], 'stock_units' : row[3], 'availabe' : row[4]})
    return datos_json

def get_article_by_id(conexion, p_article_id):
    '''
    Returns only one of the articles identified by its id

    :param value1: conexion to the db
    :param value2: unique id of an article
    '''
    cur = conexion.cursor()
    data = cur.execute("SELECT * FROM articles WHERE article_id = " + str(p_article_id) )
    row = data.fetchone()
    datos_json={'article_id' : row[0],'article_name' : row[1], 'description' : row[2], 'stock_units' : row[3], 'available' : row[4]}
    return datos_json

def exists_article_by_id(conexion, p_article_id):
    '''
    Returns True if the article identified by its id exists, otherwise returns false

    :param value1: conexion to the db
    :param value2: unique id of an article
    '''
    cur = conexion.cursor()
    data = cur.execute("SELECT * FROM articles WHERE article_id = " + str(p_article_id) )
    row = data.fetchone()
    if (row == None):
        return False
    else:
        return True

def delete_by_id(conexion, p_article_id):
    '''
    Deletes only one of the articles identified by its id

    :param value1: conexion to the db
    :param value2: unique id of an article
    '''
    cur = conexion.cursor()
    cur.execute("DELETE FROM articles WHERE article_id = " + str(p_article_id))
    conexion.commit()
    datos_json={}
    return datos_json

def update_article (conexion, p_article_id, p_json_data):
    '''
    Update the article identified by its id with p_json_data

    :param value1: conexion to the db
    :param value2: unique id of an article
    :param value3: Data in formato json
    '''
    cur = conexion.cursor()
    cur.execute("UPDATE articles SET article_id = " + p_json_data["article_id"] + ", article_name = '" + p_json_data["article_name"] + "', description = '" + p_json_data["description"] + "', stock_units = " + str(p_json_data["stock_units"]) + ", available ='" + p_json_data["available"] +"' WHERE article_id = " + str(p_article_id) )
    conexion.commit()
    row = cur.execute("SELECT * FROM articles WHERE article_id = " + str(p_json_data["article_id"]))
    ans=row.fetchone()
    datos_json={'article_id' : ans[0],'article_name' : ans[1], 'description' : ans[2], 'stock_units' : ans[3], 'available' : ans[4]}
    return datos_json

def create_article (conexion, p_data):
    '''
    Create a new article with p_json_data

    :param value1: conexion to the db
    :param value2: Data in formato json
    '''
    cur = conexion.cursor()
    statement  = "INSERT INTO articles VALUES(:article_id, :article_name, :description, :stock_units, :available)"
    cur.execute(statement, p_data)
    conexion.commit()
    row = cur.execute("SELECT * FROM articles WHERE article_id=" + str(cur.lastrowid))
    ans = row.fetchone()
    datos_json ={'article_id' : ans[0],'article_name' : ans[1], 'description' : ans[2], 'stock_units' : ans[3], 'available' : ans[4]}
    return datos_json

def send_article_by_id (conexion, p_article_id, p_amount):
    '''
    Extract a p_amount quantity of articles identified by article_id

    :param value1: conexion to the db
    :param value2: unique id of an article
    :param value3: amount of articles to be sended
    '''
    cur = conexion.cursor()
    row = cur.execute("SELECT stock_units FROM articles WHERE article_id = " + str(p_article_id))
    ans = row.fetchone()
    existing_amount = int(ans[0])
    solicited_amount = int(p_amount)
    if (existing_amount >= solicited_amount):
        if ( existing_amount - solicited_amount == 0 ):
            availability = 'N'
        else:
            availability = 'Y'
        statement = "UPDATE articles SET stock_units = "+ str(existing_amount - solicited_amount) + ", available = '" + availability + "' WHERE article_id=" + str(p_article_id)
        row = cur.execute(statement)
        conexion.commit()
    else:
        return -1
    row = cur.execute("SELECT * FROM articles WHERE article_id=" + str(p_article_id))
    ans = row.fetchone()
    datos_json ={'article_id' : ans[0],'article_name' : ans[1], 'description' : ans[2], 'stock_units' : ans[3], 'available' : ans[4]}
    return datos_json

def receive_article_by_id (conexion, p_article_id, p_amount):
    '''
    Receive a p_amount quantity of articles identified by article_id

    :param value1: conexion to the db
    :param value2: unique id of an article
    :param value3: amount of articles to be received
    '''
    cur = conexion.cursor()
    statement = "UPDATE articles SET stock_units = stock_units + "+ p_amount + ", available = 'Y' WHERE article_id=" + str(p_article_id)
    row = cur.execute(statement)
    conexion.commit()
    row = cur.execute("SELECT * FROM articles WHERE article_id=" + str(p_article_id))
    ans = row.fetchone()
    datos_json ={'article_id' : ans[0],'article_name' : ans[1], 'description' : ans[2], 'stock_units' : ans[3], 'available' : ans[4]}
    return datos_json

def validate_login (conexion, p_consumer, p_api_key):
    '''
    Given a p_consumer and p_api_key search in the database if it exists

    :param value1: conexion to the db
    :param value2: consumer id
    :param value3: password of that consumer
    '''
    if p_api_key is None or p_consumer is None:
        return False
    else:
        cur = conexion.cursor()
        statement = "SELECT consumer_id FROM consumers WHERE consumer = '" + p_consumer + "' AND api_key = '" + p_api_key + "'"
        row = cur.execute(statement)
        ans = row.fetchone()
        if (ans == None):
            return False
        else:
            return True
