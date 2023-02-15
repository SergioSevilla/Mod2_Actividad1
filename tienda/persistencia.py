import sqlite3
from sqlite3 import Error, IntegrityError

def inicializar(configuracion):
    database_path = configuracion["basedatos"]["path"]
    conexion = sqlite3.connect(database_path, check_same_thread=False)
    crear_esquema(conexion,configuracion)
    return conexion

def crear_esquema (conexion,configuracion):
    c = conexion.cursor()
    for tabla in configuracion["tables"]:
        create_str = "CREATE TABLE IF NOT EXISTS "
        create_str = create_str + tabla + "("
        columnas = configuracion["tables"][tabla]["columns"]
        first = True
        for atributo in columnas:
            if not first : create_str = create_str+", "
            create_str = create_str + "[" + atributo + "] " +configuracion["tables"][tabla]["columns"][atributo]["type"]
            first = False
        create_str = create_str + ")"
        c.execute(create_str)

def check_productos(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM articles")
    results = cursor.fetchall()
    return len (results)

def check_productos_by_id(conexion, id):
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM articles WHERE id="+str(id))
    results = cursor.fetchall()
    return len (results)

def get_cantidad(conexion, id):
    cursor = conexion.cursor()
    cursor.execute("SELECT amount FROM articles WHERE id="+str(id))
    results = cursor.fetchall()
    return (results[0][0])

def set_cantidad(conexion, id, amount):
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET amount=amount+"+str(amount)+" WHERE id ="+str(id))
    conexion.commit()

def get_precio(conexion, id):
    cursor = conexion.cursor()
    cursor.execute("SELECT price FROM articles WHERE id="+str(id))
    results = cursor.fetchall()
    return (results[0][0])

def obtener_productos(conexion):
    cursor = conexion.cursor()
    data = cursor.execute("SELECT * FROM articles")
    datos=[]
    for fila in data:
        datos.append({'id' : fila[0],'name' : fila[1], 'price' : fila[2], 'amount' : fila[3], 'sales': fila[4]})
    return datos

def obtener_productos_id(conexion,product_id):
    cursor = conexion.cursor()
    data = cursor.execute("SELECT * FROM articles WHERE id="+product_id)
    datos={}
    for fila in data:
        datos={'id' : fila[0],'name' : fila[1], 'price' : fila[2], 'amount' : fila[3], 'sales': fila[4]}
    return datos

def borrar_por_id(conexion,product_id):
    cursor = conexion.cursor()
    data = cursor.execute("DELETE FROM articles WHERE id="+product_id)
    conexion.commit()
    datos={}
    return datos

def actualizar_producto(conexion,nombre,precio,cantidad,ventas,id_act):
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET name ='"+nombre+"', price = "+str(precio)+
                   ", amount = "+str(cantidad)+", sales = "+str(ventas)+" WHERE id="+str(id_act))
    conexion.commit()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(id_act))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2], 'amount': fila[3], 'sales': fila[4]}
    return datos


def modificar_precio(conexion, id, precio):
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET price = " + str(precio) + " WHERE id=" + str(id))
    conexion.commit()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(id))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2], 'amount': fila[3], 'sales': fila[4]}
    return datos

def crear_producto(conexion,id, nombre,precio,cantidad,ventas):
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO articles (id,name,price,amount,sales) VALUES ("+str(id)+",'"+nombre+"',"+ str(precio) + ","
                       + str(cantidad)+","+str(ventas)+")")
        last_id = cursor.lastrowid
        conexion.commit()
        data = cursor.execute("SELECT * FROM articles WHERE id=" + str(last_id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'name': fila[1], 'price': fila[2], 'amount': fila[3], 'sales': fila[4]}
        return datos
    except IntegrityError:
        return {}


def decrementar_cantidad(conexion,producto_id, cantidad):
    cursor = conexion.cursor()
    cursor.execute("UPDATE articles SET amount = " + str(cantidad-1) + " WHERE id=" + str(producto_id))
    conexion.commit()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(producto_id))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2], 'amount': fila[3], 'sales': fila[4]}
    return datos

def aumentar_venta(conexion,producto_id):
    cursor = conexion.cursor()
    data = cursor.execute("SELECT * FROM articles WHERE id=" + str(producto_id))
    datos = {}
    for fila in data:
        datos = {'id': fila[0], 'name': fila[1], 'price': fila[2], 'amount': fila[3], 'sales': fila[4]}
    cursor.execute("UPDATE articles SET sales = " + str(datos["sales"]+1) + " WHERE id=" + str(producto_id))
    conexion.commit()

def vender_producto(conexion,producto_id):
    cantidad = get_cantidad(conexion,producto_id)
    if cantidad == 0:
        result_error = {}
        datos = {'error': 'There is not enough quantity to sell the article'}
        return datos
    else:
        precio = get_precio(conexion,producto_id)
        if precio > 0:
            aumentar_venta(conexion,producto_id)
            return decrementar_cantidad(conexion,producto_id,cantidad)
        else:
            datos = {'error': 'The prize of the article is equal to zero'}
            return datos
