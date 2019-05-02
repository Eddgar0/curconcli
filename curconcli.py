"""

curconcli convierte la una moneda a cualquier tipo de currencia, esta asociado a yahoo finance para trabajar en el
Argumentos:
    curconcli <cantidad moneda local> <Abreviacion Moneda Origen> <Abreviacion moneda a convertir>

Ejemplo:
    curconcli 100 USD DOP
    'Convierte 100 Dolares estadounidenses a  Pesos dominicanos'

"""

import json
from urllib.request import urlopen
from urllib import error
import argparse
from decimal import Decimal
import time
from os import path, getenv
start_time = time.time()

parser = argparse.ArgumentParser(description='Convierte valores de intercambio de monedas')

parser.add_argument('local_value', help='cantidad de la moneda Origen', type=float)
parser.add_argument('local_coin', help='Moneda origen en metodo abreviado ej. USD')
parser.add_argument('foreing_coin', help='Moneda a convertir en metodo abrevidado')
parser.add_argument('--force', '-f', action='store_true', help='Fuerza Actualizar la Base de datos de Tasas de Intercambio',)
args = parser.parse_args()


def currency_fetcher(force=False):
    """
    Function: Usa el api Yahoo finance  para obtener los valores de las currencias en Estados Unidos
    Retorna: dictionary object
    Raises: NameError, KeyError, Urllib.error.URLError
    """
    # Variables
    file_not_found = False
    too_old = False
    savepath = path.join(getenv('APPDATA'), 'currency.json')
    # Trata de Abrir el archivo y valida su existencia
    try:
        with open(savepath, 'r') as currency:
            data = json.load(currency)
    except FileNotFoundError as e:
        print('Log, not file lets try to download')
        file_not_found = True
    else:
        jsondate = time.strptime(data['list']['meta']['time'], '%Y-%m-%dT%H:%M:%S%z')
        jsontoday = time.gmtime(time.time())
        if (jsondate.tm_year != jsontoday.tm_year) or (jsondate.tm_mon != jsontoday.tm_mon) or (jsondate.tm_mday != jsontoday.tm_mday):
            too_old = True

    if file_not_found or too_old or force:
        print('Actualizando Tasas...')
        try:
            #Este API esta roto ha de realizarse un cambio en la logica general del programa
            with urlopen('https://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json') as response:
                source = response.read()

        except error.URLError as e:
            print('Could not Open the Link, Do you have internet? or maybe is a broken link?', e.reason)

        else:
            data = json.loads(source)

        # Cleaning the Data and then Saving on Local File
            for i, item in enumerate(data['list']['resources']):
                if not len(item['resource']['fields']):
                    data['list']['resources'].pop(i)
                    data['list']['meta']['count'] -= 1
            data['list']['meta']['time'] = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.gmtime(time.time()))

        try:
            with open(savepath, 'w') as currency:
                json.dump(data, currency, indent=2)
        except PermissionError as e:
            print('No pude escribir en el archivo tienes permisos para escribir?', e)

    usd_rates = dict()
    try:
        for item in data['list']['resources']:
            name = str(item['resource']['fields']['name'])
            price = float(item['resource']['fields']['price'])
            usd_rates[name] = price

    except (KeyError, NameError) as e:
        print("Something went wrong, There not Such Key: {}".format(e))
    return usd_rates


    usd_rates = dict()
    try:
        for item in data['list']['resources']:

                name = str(item['resource']['fields']['name'])
                price = float(item['resource']['fields']['price'])
                usd_rates[name] = price

    except (KeyError, NameError) as e:
        print("Something went wrong, There not Such Key: {}".format(e))
    return usd_rates


TWO_PLACE = Decimal(10) ** -2
USD = 'USD/'
local_coin = args.local_coin
local_value = Decimal(args.local_value)
foreing_coin = args.foreing_coin
local = True
repeat = False
usd_rates = currency_fetcher(args.force)

# Validamos la tasa de intercambio de la moneda normamlmente referida en USD
try:
    if local_coin == foreing_coin:
        rate = Decimal('1')
    elif local_coin != 'USD' and foreing_coin != 'USD':
        # En esta opcion Si las monedas locales y Foraneas no son USD converitermos luego la moneda local a USD
        rate = Decimal(usd_rates[USD + local_coin])
        repeat = True
    elif local_coin != 'USD':
        rate = Decimal(usd_rates[USD + local_coin])
        local = False
    elif foreing_coin != 'USD':
        rate = Decimal(usd_rates[USD + foreing_coin])
    else:
        rate = Decimal('1')

    if repeat:
        local_value = (local_value / rate).quantize(TWO_PLACE)
        rate = Decimal(usd_rates[USD + foreing_coin])
    foreing_value = (local_value * rate).quantize(TWO_PLACE) if local else (local_value / rate).quantize(TWO_PLACE)
    print(foreing_value, foreing_coin)

except KeyError as e:
    print('Hey la Moneda es incorrecta', e)

print("time elapsed: {:.2f}s".format(time.time() - start_time))
