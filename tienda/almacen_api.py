"""
Módulo para el manejo de las APIs del almacen

"""
import requests

def obtener_productos( api_key, configuracion):
    '''
    Obtiene un listado de todos los productos que hay en el almacen.
    Se obtiene servidor, puerto y nombre de consumidor del fichero de
    configuracion.


    :param api_key: API-KEY necesario para consumir los servicios del almacen
    :param configuracion: Fichero de configuración
    :return: Respuesta obtenida
    '''
    servidor = configuracion["almacen"]["servidor"]
    puerto = configuracion["almacen"]["puerto"]
    consumer = configuracion["consumidor"]["nombre"]
    url = "http://" + servidor + ":" + str(puerto) + "/almacen/v1/articles"
    #pasamos como cabecera la api-key y el nombre del consumidor
    headers = {"api-key": api_key, "consumer" : consumer}
    response = requests.get(url, headers=headers)
    return response

def obtener_producto(api_key, configuracion, id):
    '''
    Obtiene un producto que hay en el almacen por id.
    Se obtiene servidor, puerto y nombre de consumidor del fichero de
    configuracion.

    :param api_key: API-KEY necesario para consumir los servicios del almacen
    :param configuracion: Fichero de configuración
    :param id: ID del producto del almacen
    :return: Respuesta obtenida
    '''
    servidor = configuracion["almacen"]["servidor"]
    puerto = configuracion["almacen"]["puerto"]
    consumer = configuracion["consumidor"]["nombre"]
    url = "http://" + servidor + ":" + str(puerto) + "/almacen/v1/articles/" + str(id)
    headers = {"api-key": api_key, "consumer" : consumer}
    response = requests.get(url, headers=headers)
    return response

def enviar_a_tienda( api_key, id, cantidad, configuracion):
    '''
    Se llama a servicio de almacen para obtener artículo

    :param api_key: API-KEY necesario para consumir los servicios del almacen
    :param id: ID del producto del almacen
    :param cantidad: Cantidad de productos que se quiere enviar a la tienda
    :param configuracion: Fichero de configuración
    :return: Respuesta obtenida
    '''
    servidor = configuracion["almacen"]["servidor"]
    puerto = configuracion["almacen"]["puerto"]
    consumer = configuracion["consumidor"]["nombre"]
    url = "http://" + servidor + ":" + str(puerto) + "/almacen/v1/articles/" + str(id) + "/send"
    data = {"amount" : cantidad }
    headers = {"api-key": api_key, "consumer": consumer}
    response = requests.put(url, headers=headers, json=data)
    return response
