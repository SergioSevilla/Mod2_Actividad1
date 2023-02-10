import os
import sqlite3
from sqlite3 import Error
import json

class Persistencia:
    def __init__(self,configuracion):
        database_path = configuracion["basedatos"]["path"]
        self.conexion = sqlite3.connect(database_path, check_same_thread=False)
        self.crear_esquema(configuracion)
        if self.check_productos() == 0:
            self.inicializar_productos()



    def crear_esquema (self,configuracion):
        c = self.conexion.cursor()
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

    def check_productos(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM productos")
        results = cursor.fetchall()
        return len (results)

    def check_productos_by_id(self, id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE id="+str(id))
        results = cursor.fetchall()
        return len (results)

    def get_cantidad(self, id):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT cantidad FROM productos WHERE id="+str(id))
        results = cursor.fetchall()
        return (results[0][0])

    def inicializar_productos(self):
        #todo: llamar a la API de almacen para poblar la tabla de productos
        print("Consultando almacen...")
        # simulamos almacen
        cursor = self.conexion.cursor()
        cursor.execute("INSERT INTO productos (nombre,precio,cantidad) VALUES ('Nolotil',100.30,5)")
        cursor.execute("INSERT INTO productos (nombre,precio,cantidad) VALUES ('Dalsy',30.55,7)")
        cursor.execute("INSERT INTO productos (nombre,precio,cantidad) VALUES ('Apiretal',10.15,3)")
        self.conexion.commit()

    def obtener_tabla_all(self,nombre_tabla):
        cursor = self.conexion.cursor()
        data = cursor.execute("SELECT * FROM "+nombre_tabla)
        datos=[]
        for fila in data:
            datos.append({'id' : fila[0],'nombre' : fila[1], 'precio' : fila[2], 'cantidad' : fila[3]})
        return datos

    def obtener_por_id(self,nombre_tabla,product_id):
        cursor = self.conexion.cursor()
        data = cursor.execute("SELECT * FROM "+nombre_tabla+" WHERE id="+product_id)
        datos={}
        for fila in data:
            datos={'id' : fila[0],'nombre' : fila[1], 'precio' : fila[2], 'cantidad' : fila[3]}
        return datos

    def borrar_por_id(self,nombre_tabla,product_id):
        cursor = self.conexion.cursor()
        data = cursor.execute("DELETE FROM "+nombre_tabla+" WHERE id="+product_id)
        self.conexion.commit()
        datos={}
        return datos

    def actualizar_producto(self,id,nombre,precio,cantidad):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE productos SET nombre ='"+nombre+"', precio = "+str(precio)+", cantidad = "+str(cantidad)+
                       " WHERE id="+str(id))
        self.conexion.commit()
        data = cursor.execute("SELECT * FROM productos WHERE id=" + str(id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'nombre': fila[1], 'precio': fila[2], 'cantidad': fila[3]}
        return datos

    def cambiar_precio(self, id, precio):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE productos SET  precio = " + str(precio) + " WHERE id=" + str(id))
        self.conexion.commit()
        data = cursor.execute("SELECT * FROM productos WHERE id=" + str(id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'nombre': fila[1], 'precio': fila[2], 'cantidad': fila[3]}
        return datos

    def  crear_producto(self,nombre,precio,cantidad):
        cursor = self.conexion.cursor()
        cursor.execute("INSERT INTO productos (nombre,precio,cantidad) VALUES ('"+nombre+"',"+ str(precio) + ","
                       + str(cantidad)+")")
        last_id = cursor.lastrowid
        self.conexion.commit()
        data = cursor.execute("SELECT * FROM productos WHERE id=" + str(last_id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'nombre': fila[1], 'precio': fila[2], 'cantidad': fila[3]}
        return datos

    def decrementar_cantidad(self,producto_id, cantidad):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE productos SET cantidad = " + str(cantidad-1) + " WHERE id=" + str(producto_id))
        self.conexion.commit()
        data = cursor.execute("SELECT * FROM productos WHERE id=" + str(producto_id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'nombre': fila[1], 'precio': fila[2], 'cantidad': fila[3]}
        return datos

    def vender_producto(self,producto_id):
        if self.check_productos_by_id(producto_id):
            cantidad = self.get_cantidad(producto_id)
            if cantidad == 0:
                print ("no hay producto")
                # todo: el producto existe pero no hay existencias
            else:
                return self.decrementar_cantidad(producto_id,cantidad)
        else:
            print ("no exitte")
            #todo: el producto no existe
        return {}
