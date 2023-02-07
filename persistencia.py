import os
import sqlite3
from sqlite3 import Error

class Persistencia:
    def __init__(self,configuracion):
        database_path = configuracion["basedatos"]["path"]
        if not os.path.isfile(database_path):
            print("no existe base datos "+database_path+". Inicializando...")
            try:
                conn = sqlite3.connect(database_path)
            except Error as e:
                print(e)
        else:
            print("Base de datos encontrada.")
            #Check tables and create


