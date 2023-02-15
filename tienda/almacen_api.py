import requests


def obtener_productos( api_key, configuracion):
    servidor = configuracion["almacen"]["servidor"]
    puerto = configuracion["almacen"]["puerto"]
    consumer = configuracion["consumidor"]["nombre"]
    url = "http://" + servidor + ":" + str(puerto) + "/almacen/v1/articles"
    headers = {"api-key": api_key, "consumer" : consumer}
    response = requests.get(url, headers=headers)
    return response


def obtener_producto(api_key, configuracion, id):
    servidor = configuracion["almacen"]["servidor"]
    puerto = configuracion["almacen"]["puerto"]
    consumer = configuracion["consumidor"]["nombre"]
    url = "http://" + servidor + ":" + str(puerto) + "/almacen/v1/articles/" + str(id)
    headers = {"api-key": api_key, "consumer" : consumer}
    response = requests.get(url, headers=headers)
    return response


def enviar_a_tienda( api_key, id, cantidad, configuracion):
    servidor = configuracion["almacen"]["servidor"]
    puerto = configuracion["almacen"]["puerto"]
    consumer = configuracion["consumidor"]["nombre"]
    url = "http://" + servidor + ":" + str(puerto) + "/almacen/v1/articles/" + str(id) + "/send"
    data = {"amount" : cantidad }
    headers = {"api-key": api_key, "consumer": consumer}
    response = requests.put(url, headers=headers, json=data)
    return response
