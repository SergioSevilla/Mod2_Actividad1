"""
Módulo para controlar los accesos a la base de datos
"""
import sqlite3
from sqlite3 import IntegrityError

def inicializar(configuracion):
    '''
    Se iniciliza la base de datos, y se llama a crear_esquema para
    crear las tablas si no estuvieran ya creadas

    :param configuracion: Fichero de configuración
    :return: conexion a la base de datos SQLite3
    '''
    database_path = configuracion["basedatos"]["path"]
    conexion = sqlite3.connect(database_path, check_same_thread=False)
    crear_esquema(conexion,configuracion)
    return conexion

def crear_esquema (conexion,configuracion):
    '''
    Se crean las tablas (si no existen) a partir del fichero de configuración.
    En el fichero de configuración se encuentra la información para crear las
     tablas y sus atributos

    :param conexion: conexion a la base de datos SQLite3
    :param configuracion: Fichero de configuración
    '''
    cursor = conexion.cursor()
    for tabla in configuracion["tables"]:
        create_str = "CREATE TABLE IF NOT EXISTS "
        create_str = create_str + tabla + "("
        columnas = configuracion["tables"][tabla]["columns"]
        first = True
        for atributo in columnas:
            if not first:
                create_str = create_str+", "
            create_str = create_str + "[" + atributo + "] " +\
                         configuracion["tables"][tabla]["columns"][atributo]["type"]
            first = False
        create_str = create_str + ")"
        cursor.execute(create_str)

def check_productos(conexion):
    '''
    Comprueba si hay o no productos en la tabla "Articles"

    :param conexion: conexion a la base de datos SQLite3
    :return: Devuelve 0 si no hay y >0 si hay
    '''
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM articles")
    results = cursor.fetchall()
    return len (results)

def check_productos_by_id(conexion, article_id):
    '''
    Comprueba si existe o no un producto en la tabla "Articles" buscando
    por su id

    :param conexion: conexion a la base de datos SQLite3
    :param id: Id del producto de la tabla Articles
    :return: Devuelve 0 si no hay y >0 si hay
    '''
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM articles WHERE id="+str(article_id))
    results = cursor.fetchall()
    return len (results)

def get_cantidad(conexion, article_id):
    '''
    Devuelve la cantidad de productos que hay en la tienda
    buscando por un ID

    :param conexion: conexion a la base de datos SQLite3
    :param id: Id del producto de la tabla Articles
    :return: Cantidad de productos ("amount")
    '''
    cursor = conexion.cursor()
    cursor.execute("SELECT amount FROM articles WHERE id="+str(article_id))
    results = cursor.fetchall()
    return results[0][0]

def set_cantidad(conexion, article_id, amount):
    '''
    Establece la cantidad de articulos disponibles en tienda
     de un producto por su ID

    :param conexion: conexion a la base de datos SQLite3
    :param id: Id del producto de la tabla Articles
    :param amount: Cantidad a actualizar del producto
    '''
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET amount=amount+"+str(amount)+" WHERE id ="+str(article_id))
    conexion.commit()

def get_precio(conexion, article_id):
    '''
    Devuelve el precio de un porducto que hay en la tienda

    :param conexion: conexion a la base de datos SQLite3
    :param id: Id del producto de la tabla Articles
    :return: Precio del producto
    '''
    cursor = conexion.cursor()
    cursor.execute("SELECT price FROM articles WHERE id="+str(article_id))
    results = cursor.fetchall()
    return results[0][0]

def obtener_productos(conexion):
    '''
    Devuelve el listado de productos de la tabla articles

    :param conexion: conexion a la base de datos SQLite3
    :return: Listado de productos
    '''
    cursor = conexion.cursor()
    data = cursor.execute("SELECT * FROM articles")
    datos=[]
    for fila in data:
        datos.append({'id' : fila[0],'name' : fila[1], 'price' : fila[2],
                      'amount' : fila[3], 'sales': fila[4]})
    return datos

def obtener_productos_id(conexion,product_id):
    '''
    Devuelve un productos de la tabla articles buscando por su id

    :param conexion: conexion a la base de datos SQLite3
    :param product_id: Id del producto de la tabla Articles
    :return: Producto de la tabla article
    '''
    cursor = conexion.cursor()
    data = cursor.execute("SELECT * FROM articles WHERE id="+product_id)
    datos={}
    for fila in data:
        datos={'id' : fila[0],'name' : fila[1], 'price' : fila[2],
               'amount' : fila[3], 'sales': fila[4]}
    return datos

def borrar_por_id(conexion,product_id):
    '''
    Borra un producto de la tabla articles por su ID

    :param conexion: conexion a la base de datos SQLite3
    :param product_id: Id del producto de la tabla Articles
    :return: Producto de la tabla article
    '''
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM articles WHERE id="+product_id)
    conexion.commit()
    datos={}
    return datos

def actualizar_producto(conexion,request_json,id_act):
    '''
    Realiza Update de un producto por su ID

    :param conexion: conexion a la base de datos SQLite3
    :param request_json: json con los datos a actualizar
    :return: Producto actualziado
    '''
    nombre=request_json.get('name')
    precio=request_json.get('price')
    cantidad=request_json.get('amount')
    ventas=request_json.get('sales')
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET name ='"+nombre+"', price = "+str(precio)+
                   ", amount = "+str(cantidad)+", sales = "+str(ventas)+" WHERE id="+str(id_act))
    conexion.commit()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(id_act))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2],
                 'amount': fila[3], 'sales': fila[4]}
    return datos


def modificar_precio(conexion, article_id, precio):
    '''
    Modifica el precio de un producto por su ID

    :param conexion: conexion a la base de datos SQLite3
    :param id: Id del producto de la tabla Articles
    :param precio: precio a actualizar
    :return: Producto actualziado
    '''
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET price = " + str(precio) + " WHERE id=" + str(article_id))
    conexion.commit()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(article_id))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2],
                 'amount': fila[3], 'sales': fila[4]}
    return datos

def crear_producto(conexion,json_article):
    '''
    Inserta un producto en la tabla articles

    :param conexion: conexion a la base de datos SQLite3
    :param json_article: Datos del producto a insertar
    :return: Producto insertado
    '''
    cursor = conexion.cursor()
    article_id = json_article.get('id')
    nombre = json_article.get('name')
    precio = json_article.get('price')
    cantidad = json_article.get('amount')
    ventas = json_article.get('sales')
    try:
        cursor.execute("INSERT INTO articles (id,name,price,amount,sales) VALUES ("
                       +str(article_id)+",'"+nombre+"',"+ str(precio) + ","+ str(cantidad)+","
                       +str(ventas)+")")
        last_id = cursor.lastrowid
        conexion.commit()
        data = cursor.execute("SELECT * FROM articles WHERE id=" + str(last_id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'name': fila[1], 'price': fila[2],
                     'amount': fila[3], 'sales': fila[4]}
        return datos
    except IntegrityError:
        return {}


def decrementar_cantidad(conexion,producto_id, cantidad):
    '''
    Procedimiento que actualiza la cantidad del producto decrementa ésta en 1

    :param conexion: conexion a la base de datos SQLite3
    :param producto_id: Id del producto de la tabla Articles
    :param cantidad: Cantidad del nuevo producto
    :return: Porducto actualizado
    '''
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET amount = " + str(cantidad-1) +
                   " WHERE id=" + str(producto_id))
    conexion.commit()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(producto_id))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2],
                 'amount': fila[3], 'sales': fila[4]}
    return datos

def aumentar_venta(conexion,producto_id):
    '''
    Aumenta en 1 la venta de un producto

    :param conexion: conexion a la base de datos SQLite3
    :param producto_id: Id del producto de la tabla Articles
    '''
    cursor = conexion.cursor()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(producto_id))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2],
                 'amount': fila[3], 'sales': fila[4]}
    cursor.execute("UPDATE articles SET sales = " + str(datos["sales"]+1) +
                   " WHERE id=" + str(producto_id))
    conexion.commit()

def vender_producto(conexion,producto_id):
    '''
    Procedimiento de venta de un producto. Comprueba que su precio
    o cantidad no sea cero y si no es así decrementa la cantidad y
    aumenta la venta

    :param conexion: conexion a la base de datos SQLite3
    :param producto_id: Id del producto de la tabla Articles
    :return: Producto actualizado o error producido
    '''
    cantidad = get_cantidad(conexion,producto_id)
    if cantidad == 0:
        datos = {'error': 'There is not enough quantity to sell the article'}
    else:
        precio = get_precio(conexion,producto_id)
        if precio > 0:
            aumentar_venta(conexion,producto_id)
            datos = decrementar_cantidad(conexion,producto_id,cantidad)
        else:
            datos = {'error': 'The prize of the article is equal to zero'}
    return datos
