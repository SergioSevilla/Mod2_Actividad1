"""
Programa que publica el API de tienda y se comunica con almacén

Uso: tienda.py [-h] [-servidor SERVIDOR] [-puerto PUERTO] -config <fichero_YAML> -key API_KEY
    Parámetros requeridos:
        -config <fichero_YAML> : Ruta y nombre del fichero de configuración de la aplicación
        -key API_KEY  : Valor del API KEY para consumir servicios de la aplicación almacén.
    Parámetro opcionales:
        -h, --help : Muestra pantalla de ayuda
        -servidor SERVIDOR : IP o nombre el servidor donde se inicia la aplicación
        -puerto PUERTO : puerto donde se expondrá el API
"""
import os
import argparse
from flask import Flask, Response, request,  jsonify
import yaml
from yaml.loader import SafeLoader
import persistencia
import json


def check_ports(value):
    '''
    Chequea si el puerto introducido por parámetro se encuentra
    dentro del rango correcto

    :param value: valor del puerto introducido
    '''
    ivalue = int(value)
    if not(1 <= ivalue <= 65535):
        raise argparse.ArgumentTypeError(value+" no es un puerto válido [1-65535]")
    return ivalue

def check_file(value):
    '''
    Chequea si el puerto introducido por parámetro se encuentra
    dentro del rango correcto

    :param value: valor del puerto introducido
    '''
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError("El fichero "+value+" no existe.")
    return value

def cargar_configuracion(path_config):
    with open(path_config) as f_config:
        datos = yaml.load(f_config, Loader=SafeLoader)
    return datos

# configuración de todos los parámetros de entrada del programa
parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument("-config", "--config",  required=True, type=check_file,
                           help="Ruta y nombre del fichero de configuración de la aplicación")
requiredNamed.add_argument("-key", "--key", required=True,
                           help="Valor del API KEY para consumir servicios de la aplicación almacén.")
parser.add_argument("-servidor", "--servidor",  default="localhost",
                    help="IP o nombre el servidor donde se inicia la aplicación")
parser.add_argument("-puerto", "--puerto",  default=5000, type=check_ports,
                    help="puerto donde se expondrá el API")

args = parser.parse_args()

configuracion = cargar_configuracion (args.config)

conexion = persistencia.Persistencia(configuracion)


app = Flask(__name__)

#CRUD productos
@app.route("/productos",methods=['GET', 'POST'])
def producto():
    if request.method == 'GET':
        args = request.args
        product_id = args.get("id", default=0, type=int)
        if product_id == 0:
            resultado = conexion.obtener_tabla_all ("productos")
            return jsonify(resultado)
        else:
            resultado = conexion.obtener_por_id("productos", str(product_id))
            return jsonify(resultado)
    if request.method == 'POST':
        request_json = request.get_json()
        resultado = conexion.crear_producto(request_json.get('nombre'),request_json.get('precio'),request_json.get('cantidad'))
        return jsonify(resultado)

@app.route("/productos/<product_id>",methods=['GET','DELETE','PUT'])
def producto_id(product_id):
    if request.method == 'GET':
        resultado = conexion.obtener_por_id ("productos",product_id)
        return jsonify(resultado)
    if request.method == 'DELETE':
        resultado = conexion.borrar_por_id("productos", product_id)
        return jsonify(resultado)
    if request.method == 'PUT':
        request_json = request.get_json()
        resultado = conexion.actualizar_producto (product_id,request_json.get('nombre'),request_json.get('precio'),request_json.get('cantidad'))
        return jsonify(resultado)

#servicio de cambio de precio
@app.route("/productos/<product_id>/cambiar-precio",methods=['PUT'])
def cambiar_precio(product_id):
    request_json = request.get_json()
    resultado = conexion.cambiar_precio( product_id, request_json.get('precio'))
    return jsonify(resultado)

#servicio de cambio de precio
@app.route("/productos/<product_id>/vender",methods=['POST'])
def vender_producto(product_id):
    resultado = conexion.vender_producto( product_id)
    return jsonify(resultado)


#inicio de flask con host y puerto predefinidos
if __name__ == '__main__':
    app.run(host=args.servidor, port=args.puerto)
