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
from flask import Flask, Response, request,  jsonify, abort
import yaml
from yaml.loader import SafeLoader
import persistencia

def check_ports(value):
    '''
    Chequea si el puerto introducido por parámetro se encuentra
    dentro del rango correcto

    :param value: valor del puerto introducido
    :return: el puerto introducido
    '''
    ivalue = int(value)
    if not(1 <= ivalue <= 65535):
        raise argparse.ArgumentTypeError(value+" no es un puerto válido [1-65535]")
    return ivalue

def check_file(value):
    '''
    Chequea si el fichero de configuración introducido como parámetro
    existe

    :param value: path del fichero de configuración
    :return: path del fichero de configuración
    '''
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError("El fichero "+value+" no existe.")
    return value

def cargar_configuracion(path_config):
    '''
    Carga el fichero de configuración en formato yaml

    :param path_config: Path del fichero de configuración
    :return: estructura del fichero de configuración
    '''
    with open(path_config) as f_config:
        datos = yaml.load(f_config, Loader=SafeLoader)
    return datos

def inicializar_productos(conexion):
    """
    Se llamará a la API en caso de que no haya productos en la tienda.

    :param conexion: conexion a la BD
    """
    #todo: llamar a la API de almacen para poblar la tabla de productos
    print("Consultando almacen...")
    # simulamos almacen
    conexion.crear_producto(1,'Nolotil',100.30,5,0)
    conexion.crear_producto(2,'Dalsy', 30.55, 7,0)
    conexion.crear_producto(3,'Apiretal', 10.15, 3,0)

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

#se carga elfichero de configuración
configuracion = cargar_configuracion (args.config)

#Se inicializa base de datos
conexion = persistencia.Persistencia(configuracion)

#
if conexion.check_productos() == 0:
    inicializar_productos(conexion)

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
        resultado = conexion.crear_producto(request_json.get('id'),request_json.get('nombre'),request_json.get('precio'),request_json.get('cantidad'), request_json.get('ventas'))
        if resultado == {}:
            abort(409,"The resoruce you are try to update already exists on the server. Please check the resource id and"
                      " try again.")
        else:
            return jsonify(resultado)

@app.route("/productos/<product_id>",methods=['GET','DELETE','PUT'])
def producto_id(product_id):
    if request.method == 'GET':
        resultado = conexion.obtener_por_id ("productos",product_id)
        return jsonify(resultado)
    if request.method == 'DELETE':
        if conexion.check_productos_by_id(product_id) == 0 :
            abort(404,"The requested resource was not found on the server. Please check the resource id and try again.")
        else:
            resultado = conexion.borrar_por_id("productos", product_id)
            return jsonify(resultado)
    if request.method == 'PUT':
        request_json = request.get_json()
        if conexion.check_productos_by_id(product_id) == 0 :
            abort(404,"The requested resource was not found on the server. Please check the resource id and try again.")
        else:
            resultado = conexion.actualizar_producto (request_json.get('nombre'),request_json.get('precio'),
                                                  request_json.get('cantidad'),request_json.get('ventas'),product_id)
            return jsonify(resultado)

#servicio de cambio de precio
@app.route("/productos/<product_id>",methods=['PATCH'])
def modificar_precio(product_id):
    if conexion.check_productos_by_id(product_id) == 0:
        abort(404, "The requested resource was not found on the server. Please check the resource id and try again.")
    else:
        request_json = request.get_json()
        resultado = conexion.modificar_precio( product_id, request_json.get('precio'))
        return jsonify(resultado)

#servicio de venta de producto
@app.route("/productos/<product_id>/vender",methods=['PUT'])
def vender_producto(product_id):
    if conexion.check_productos_by_id(product_id) == 0:
        abort(404, "The requested resource was not found on the server. Please check the resource id and try again.")
    else:
        resultado = conexion.vender_producto( product_id)
        if "error" in resultado:
            abort(409,resultado["error"])
        else:
            return jsonify(resultado)


#inicio de flask con host y puerto predefinidos
if __name__ == '__main__':
    app.run(host=args.servidor, port=args.puerto)
