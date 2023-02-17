'''
La aplicación recibirá como argumentos opcionales:
a.--servidor: IP o nombre del servidor. Opcional. Por defecto localhost.
b.--puerto: puerto donde se expondrá el API. Opcional. Por defecto 5000.
c.--config: ruta y nombre del fichero de configuración de la aplicación.Obligatorio.
'''
import os
import argparse
from functools import wraps
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_swagger_ui import get_swaggerui_blueprint
import yaml
import db

def check_port(p_port):
    '''
    Check if p_port is an actually valid port

    parav value: port to be checked
    '''
    i_port = int(p_port)
    if not 1 <= i_port <= 65535:
        raise argparse.ArgumentTypeError(p_port + " no es un puerto válido [1-65535]")
    return p_port

def check_file(p_file):
    '''
    Check if the file is an actually valid file and it exists in the OS

    :param value: name of the file to be checked
    '''
    if not os.path.isfile(p_file):
        raise argparse.ArgumentTypeError("El fichero " + p_file + " no existe.")
    return p_file

def return_config (p_config_file_name):
    '''
    Returns a dictionary with the info of a file given than the format is YAML

    :param value: name of the file to be read
    '''
    with open(p_config_file_name, encoding="UTF8") as config_file:
        configdict = yaml.safe_load(config_file)
        config_file.close()
    return configdict

parser = argparse.ArgumentParser(description='Generates tokes JWT from a path where the file payload.json is located and a secret')

parser.add_argument('--servidor', help='Ip or name of the server', type=str, default='Localhost')
parser.add_argument('--puerto', help='Api port', type=check_port, default='5000')
parser.add_argument('--config', help='File configuration path', nargs=1, required=True, type=check_file)

arguments = parser.parse_args()
config_file_name = arguments.config[0]
servidor = arguments.servidor
puerto = arguments.puerto

# open and read the config file
config_dict = return_config(config_file_name)

#Connect to a database
conexion = db.connect_db (config_dict["basedatos"]["path"])

#Prepara la base de datos para su primer uso
db.initialize_db(conexion)

db.populate_tables(conexion, config_dict["basedatos"]["consumidor_almacen"], config_dict["basedatos"]["consumidor_almacen_key"])

def require_store_app_key(func):
    '''
    wrapper function that validates the pair consumer/api_key

    :param value: name of the file to be read
    '''
    @wraps(func)
    def comprueba (*args, **kwargs):
        headers = request.headers
        incoming_consumer = headers.get("consumer")
        incoming_api_key = headers.get("api_key")
        if db.validate_login (conexion, incoming_consumer, incoming_api_key):
            return func(*args, **kwargs)
        abort(403) #Forbidden
    return comprueba

#-------------------------------------------------------------
#Create Flask app
app = Flask(__name__)

SWAGGER_URL = "/api/docs" #url where the document is showed
API_URL = "./api_doc.yaml" #where the document is in the flask server

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Modulo2 Actividad 5"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/almacen/v1/articles', methods=['GET', 'POST'])
@require_store_app_key
def articulo():
    '''
    GET and POST methods por this URL
    '''
    if request.method == 'GET':
        try:
            out_json_data = db.get_all_rows_articles (conexion)
            return jsonify(out_json_data), 200
        except conexion.Error as error:
            print(f'Exception: {format(error)}')
            abort (400) #Bad request
    elif request.method == 'POST':
        input_json_data = request.get_json(force=True)

        if input_json_data.get('article_name') is None:
            abort(428) #Precondition required
        else:
            try:
                out_json_data = db.create_article (conexion, input_json_data)
                return jsonify( out_json_data ), 201
            except conexion.Error as error:
                print(f'Exception: {format(error)}')
                abort (400) #Bad request

@app.route('/almacen/v1/articles/<article_id>', methods=['GET', 'PUT', 'DELETE'])
@require_store_app_key
def articulo_id( article_id ):
    '''
    GET, PUT and DELETE methods por this URL

    :param value1: Article id
    '''
    try:
        exists = db.exists_article_by_id(conexion, article_id)
        if not exists:
            abort (404) #Not found
        if request.method == 'GET':
            out_json_data = db.get_article_by_id (conexion, article_id)
            return jsonify(out_json_data), 200
        if request.method == 'PUT':
            input_json_data = request.get_json(force=True)
            if input_json_data.get('article_name') is None:
                abort(428) #Precondition required
            else:
                out_json_data = db.update_article (conexion, article_id, input_json_data)
                return jsonify(out_json_data), 200
        if request.method == 'DELETE':
            out_json_data = db.delete_by_id(conexion, article_id)
            return jsonify(out_json_data), 200
    except conexion.Error as error:
        print(f'Exception: {format(error)}')
        abort (400) #Bad request

@app.route('/almacen/v1/articles/<article_id>/receive', methods=['PUT'])
@require_store_app_key
def recibir_articulo_id( article_id ):
    '''
    PUT methods por this URL

    :param value1: Article id
    '''
    try:
        exists = db.exists_article_by_id(conexion, article_id)
        if not exists:
            abort (404) #Not found

        input_json_data = request.get_json(force=True)
        amount = input_json_data.get('amount')
        if amount is None:
            abort(428) #Precondition required
        out_json_data = db.receive_article_by_id (conexion, article_id, amount)
        return jsonify(out_json_data), 200
    except conexion.Error as error:
        print(f'Exception: {format(error)}')
        abort (400) #Bad request

@app.route('/almacen/v1/articles/<article_id>/send', methods=['PUT'])
@require_store_app_key
def enviar_articulo_id( article_id ):
    '''
    PUT methods por this URL

    :param value1: Article id
    '''
    try:
        exists = db.exists_article_by_id(conexion, article_id)
        if not exists:
            abort (404) #Not found

        input_json_data = request.get_json(force=True)
        amount = input_json_data.get('amount')
        if amount is None:
            abort(428) #Precondition required

        out_json_data = db.send_article_by_id (conexion, article_id, amount)
        return jsonify(out_json_data), 200
    except conexion.Error as err:
        print(f'Exception: {format(err)}')
        abort (400) #Bad request

@app.route("/api/docs/api_doc.yaml")
def specs():
    '''
    Methods that shows yaml apic doc
    '''
    return send_from_directory(os.getcwd(), "api_doc.yaml")

if __name__ == '__main__':
    app.run(host=servidor, port=puerto, debug=True)
