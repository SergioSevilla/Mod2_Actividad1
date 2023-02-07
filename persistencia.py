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

    def inicializar_productos(self):
        #todo: llamar a la API de almacen para poblar la tabla de productos
        print("Consultando almacen...")
        # simulamos almacen
        cursor = self.conexion.cursor()
        cursor.execute("INSERT INTO productos (id,nombre,precio,cantidad) VALUES (1,'Nolotil',100.30,5)")
        cursor.execute("INSERT INTO productos (id,nombre,precio,cantidad) VALUES (2,'Dalsy',30.55,7)")
        cursor.execute("INSERT INTO productos (id,nombre,precio,cantidad) VALUES (3,'Apiretal',10.15,3)")
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
        cursor.execute("UPDATE productos SET nombre ='"+nombre+"', precio = "+str(precio)+", cantidad = "+str(cantidad)+" WHERE id="+str(id))
        self.conexion.commit()
        data = cursor.execute("SELECT * FROM productos WHERE id=" + str(id))
        datos = {}
        for fila in data:
            datos = {'id': fila[0], 'nombre': fila[1], 'precio': fila[2], 'cantidad': fila[3]}
        return datos