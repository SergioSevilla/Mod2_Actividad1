import requests


def obtener_productos(servidor, puerto, api_key):
    url = "http://" + servidor + ":" + puerto + "/almacen/v1/articles"
    headers = {"api-key": api_key}
    response = requests.get(url, headers=headers)
    return response.json()


def obtener_producto(servidor, puerto, api_key, id):
    url = "http://" + servidor + ":" + puerto + "/almacen/v1/articles/" + id
    headers = {"api-key": api_key}
    response = requests.get(url, headers=headers)
    return response.json()


def enviar_a_tienda(servidor, puerto, api_key, id, cantidad):
    url = "http://" + servidor + ":" + puerto + "/almacen/v1/articles"
    response = requests.get(url)
    return response.json()
