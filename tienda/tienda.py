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
from flask import Flask, request, jsonify, abort
from flask_swagger_ui import get_swaggerui_blueprint
import yaml
from yaml.loader import SafeLoader
from yaml import Loader, load
import persistencia
import almacen_api


def check_ports(value):
    '''
    Chequea si el puerto introducido por parámetro se encuentra
    dentro del rango correcto

    :param value: valor del puerto introducido
    :return: el puerto introducido
    '''
    ivalue = int(value)
    if not (1 <= ivalue <= 65535):
        raise argparse.ArgumentTypeError(value + " no es un puerto válido [1-65535]")
    return ivalue


def check_file(value):
    '''
    Chequea si el fichero de configuración introducido como parámetro
    existe

    :param value: path del fichero de configuración
    :return: path del fichero de configuración
    '''
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError("El fichero " + value + " no existe.")
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


def inicializar_productos(conexion, configuracion, key):
    '''
    Se llamará a la API en caso de que no haya productos en la tienda.
    Se traerá un máximo de 2 productos del almacen

    :param conexion: conexion a la base de datos
    :param configuracion: fichero de configuración
    :param key: api-key
    '''
    productos_almacen = almacen_api.obtener_productos(key, configuracion) #obtenemos productos del almacén
    for article_json in productos_almacen.json():
        # por cada artículo con unidades positivas que haya en el almacen, se traerá un máximo de 2
        if article_json["available"] == "Y" and article_json["stock_units"] > 0:
            if article_json["stock_units"] < 2:

                almacen_api.enviar_a_tienda(key,article_json["article_id"], 1, configuracion)
                persistencia.crear_producto(conexion,article_json["article_id"], article_json["article_name"],
                                            0.0, 1, 0)
            else:
                almacen_api.enviar_a_tienda(key,article_json["article_id"], 2, configuracion)
                persistencia.crear_producto(conexion, article_json["article_id"], article_json["article_name"],
                                            0.0, 2, 0)


# configuración de todos los parámetros de entrada del programa
parser = argparse.ArgumentParser()
requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument("-config", "--config", required=True, type=check_file,
                           help="Ruta y nombre del fichero de configuración de la aplicación")
requiredNamed.add_argument("-key", "--key", required=True,
                           help="Valor del API KEY para consumir servicios de la aplicación almacén.")
parser.add_argument("-servidor", "--servidor", default="localhost",
                    help="IP o nombre el servidor donde se inicia la aplicación")
parser.add_argument("-puerto", "--puerto", default=5000, type=check_ports,
                    help="puerto donde se expondrá el API")

args = parser.parse_args()

# se carga elfichero de configuración
configuracion = cargar_configuracion(args.config)

# Se inicializa base de datos
conexion = persistencia.inicializar(configuracion)

#Si no hubiera productos en la base de datos, se poblará llamando a las APIs de almacén
if persistencia.check_productos(conexion) == 0:
    inicializar_productos(conexion, configuracion, args.key)

app = Flask(__name__)

SWAGGER_URL = '/api/docs'  # Es la ruta donde estará expuesto nuestro Swagger UI
with open('./tienda_api_doc.yaml', 'r', encoding='utf-8') as api_doc:
    swagger_yml = load(api_doc, Loader=Loader)

# Utilizando falsk_swagger_ui se creará el servicio:
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    './api_doc.yaml',
    config={
        'spec': swagger_yml
    },
)

app.register_blueprint(swaggerui_blueprint)



# CRUD productos
@app.route("/tienda/v1/articles", methods=['GET', 'POST'])
def producto():
    if request.method == 'GET':
        args = request.args
        product_id = args.get("id", default=0, type=int)
        if product_id == 0:
            resultado = persistencia.obtener_productos(conexion)
            return jsonify(resultado), 200
        else:
            resultado = persistencia.obtener_productos_id(conexion, str(product_id))
            return jsonify(resultado), 200
    if request.method == 'POST':
        request_json = request.get_json()
        resultado = persistencia.crear_producto(conexion,request_json.get('id'), request_json.get('name'),
                                            request_json.get('price'), request_json.get('amount'),
                                            request_json.get('sales'))
        if resultado == {}:
            abort(409,
                  "The resoruce you are try to update already exists on the server. Please check the resource id and"
                  " try again.")
        else:
            return jsonify(resultado), 201


@app.route("/tienda/v1/articles/<product_id>", methods=['GET', 'DELETE', 'PUT'])
def producto_id(product_id):

    if request.method == 'GET':
        resultado = persistencia.obtener_productos_id(conexion,product_id)
        return jsonify(resultado), 200
    if persistencia.check_productos_by_id(conexion,product_id) == 0:
        abort(404,
              "The requested resource was not found on the server. Please check the resource id and try again.")
    elif request.method == 'DELETE':
        resultado = persistencia.borrar_por_id(conexion, product_id)
        return jsonify(resultado), 200
    elif request.method == 'PUT':
        request_json = request.get_json()
        resultado = persistencia.actualizar_producto(conexion,request_json.get('name'), request_json.get('price'),
                                                     request_json.get('amount'), request_json.get('sales'),
                                                     product_id)
        return jsonify(resultado), 200


# servicio de cambio de precio
@app.route("/tienda/v1/articles/<product_id>", methods=['PATCH'])
def modificar_precio(product_id):
    if persistencia.check_productos_by_id(conexion,product_id) == 0:
        abort(404, "The requested resource was not found on the server. Please check the resource id and try again.")
    else:
        request_json = request.get_json()
        resultado = persistencia.modificar_precio(conexion, product_id, request_json.get('price'))
        return jsonify(resultado), 200


# servicio de venta de producto
@app.route("/tienda/v1/articles/<product_id>/sell", methods=['PUT'])
def vender_producto(product_id):
    if persistencia.check_productos_by_id(conexion,product_id) == 0:
        abort(404, "The requested resource was not found on the server. Please check the resource id and try again.")
    else:
        resultado = persistencia.vender_producto(conexion,product_id)
        if "error" in resultado:
            abort(409, resultado["error"])
        else:
            return jsonify(resultado), 200


# servicio para recibir artículos del almacen
@app.route("/tienda/v1/articles/<product_id>/receive", methods=['PUT'])
def receive_article(product_id):
    respuesta = almacen_api.obtener_producto(args.key, configuracion, product_id)
    if respuesta.status_code == 200:
        request_json = request.get_json()
        response_json = respuesta.json()
        if response_json["stock_units"] >= request_json["amount"] and response_json["available"] == "Y":
            response_send = almacen_api.enviar_a_tienda(args.key, product_id,request_json["amount"], configuracion)
            if response_send.status_code == 200:
                persistencia.set_cantidad(conexion, product_id, request_json["amount"])
                return jsonify(persistencia.obtener_productos_id(conexion, product_id)), 200
            else:
                abort(400)
        else:
            abort(404)
    else:
        abort(respuesta.status_code)


# inicio de flask con host y puerto predefinidos
if __name__ == '__main__':
    app.run(host=args.servidor, port=args.puerto, debug=True)