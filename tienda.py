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
from flask import Flask, Response
import yaml
from yaml.loader import SafeLoader
import persistencia


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

#inicio de flask con host y puerto predefinidos
"""app = Flask(__name__)
if __name__ == '__main__':
    app.run(host=args.servidor, port=args.puerto)"""



