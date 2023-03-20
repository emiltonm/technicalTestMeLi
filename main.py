from flask import Flask, jsonify
from decouple import Config, RepositoryEnv
from pathlib import Path

from modules.data import Data
from modules.api import API
from modules.database import Database

# Aplicacion de Flask
app = Flask(__name__)
# se cargan cada uno de los tres modulos de la aplicacion
# data, api y database
source_data = Data()
api_meli = API()
database = Database()


@app.route('/', methods=['GET'])
def index():
    return jsonify({'/find': 'para buscar un documento en la base de datos',
                    '/process': 'Para procesar el archivo',
                    'Desarrollador': 'Emilton Mendoza Ojeda',
                    })


@app.route('/process', methods=['GET'])
def process():
    # procesamos el archivo fuente de datos convirtiendolo en una lista de diccionario
    source_data.process_file()
    # source_data.show_errors()
    # pasamos la informacion almacenada en source_data al objeto api_meli
    api_meli.set_api_data(source_data.get_data())
    # ejecuto las url API con los datos de source_data
    api_meli.fetch_url_file()
    # api_meli.show_errors()
    # obtengo la respuesta de la API
    response_api = api_meli.get_data()
    # database.show_errors()
    database.insert_many(response_api)
    return jsonify({'message': 'Proceso finalizado'})


if __name__ == '__main__':
    print("Entrando al main")
    # resuelvo el path del archivo de configuracion
    config_file = Path(__file__).resolve().parent/'.env.server'
    # si el archivo de configuracion no existe termino la ejecucion
    if not config_file.is_file():
        print("Archivo de configuracion no encontrado")
        exit()
    else:
        # el archivo de configuracion existe, cargo las variables de entorno
        config = Config(RepositoryEnv(config_file))
        debug_mode = config('SERVER_DEBUG')
        # convertimos de String a Boolean
        if debug_mode.upper() == 'TRUE':
            debug_mode = True
        else:
            debug_mode = False
        
        app.run(host=config('SERVER_HOST'),
                port=config('SERVER_PORT'), debug=debug_mode)
