import os
import sqlite3
from sqlite3 import Error

class Persistencia:
    def __init__(self,configuracion):
        database_path = configuracion["basedatos"]["path"]
        self.conexion = sqlite3.connect(database_path)
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