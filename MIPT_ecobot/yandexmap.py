import os
from yandex_geocoder import Client
from dotenv import load_dotenv
from decimal import Decimal

config = load_dotenv()
client = Client(os.getenv("yandexmapapikey"))

def geo_decoder(address: str):
    try:
        coordinates = client.coordinates(address)
        pos = {}
        pos['x'] = coordinates[1]
        pos['y'] = coordinates[0]
        return pos

    except Exception as e:
        return 'error'

def get_address_by_coordinates(x: float, y: float):
    address = client.address(Decimal(f'{y}'), Decimal(f'{x}'))
    return address
