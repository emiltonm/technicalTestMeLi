from flask import Flask, jsonify
from decouple import Config, RepositoryEnv
from pathlib import Path

from modules.data import Data
from modules.api import API
from modules.database import Database

# Aplicacion de Flask
app = Flask(__name__)
# se carga cada uno de los tres modulos de la aplicacion
# source_data para la lectura del archivo principal del cual se  obtendran los valores a consultar en el API
# api_meli para la consulta de los datos en el API de mercadolibre
# database para la carga de los datos en la base de datos
source_data = Data()
api_meli = API()
database = Database()


@app.route('/', methods=['GET'])
def index():
    '''
    Funcion/ruta que sirve como test de la aplicacion y muestra las rutas
    disponibles
    '''
    return jsonify({'/find': 'para buscar un documento en la base de datos',
                    '/process': 'Para procesar el archivo',
                    'Desarrollador': 'Emilton Mendoza Ojeda',
                    })


@app.route('/process', methods=['GET'])
def process():
    '''
    Funcion/ruta encargada de ejecutar todo el proceso de la aplicacion
    desde la lectura del archivo fuente de datos hasta la carga de los
    datos en la base de datos
    '''
    # procesa el archivo fuente de datos lo convierte en un diccionario
    # al cual se accede con el metodo get_data()
    source_data.process_file()
    data = source_data.get_data()
    # source_data.show_errors()

    # con la data obtenida del archivo fuente se crean las url para la
    # consulta de los datos en el API y luego se hace el llamado a las
    # url para obtener los datos
    api_meli.set_api_data(data)
    api_meli.fetch_url_file()
    data_api = api_meli.get_data()

    # api_meli.show_errors()
    # database.show_errors()

    # se carga la data obtenida del API en la base de datos
    database.insert_many(data_api)

    return jsonify({'message': 'Proceso finalizado'})


if __name__ == '__main__':
    # se obtiene la ruta del archivo de configuracion
    config_file = Path(__file__).resolve().parent/'.env.server'
    # si el archivo de configuracion no existe termino la ejecucion
    if not config_file.is_file():
        print("Archivo de configuracion .env no encontrado")
        exit()
    else:
        # el archivo de configuracion existe, cargo las variables de entorno
        config = Config(RepositoryEnv(config_file))
        debug_mode = config('SERVER_DEBUG')
        # convierte String a Boolean
        if debug_mode.upper() == 'TRUE':
            debug_mode = True
        else:
            debug_mode = False

        app.run(host=config('SERVER_HOST'),
                port=config('SERVER_PORT'), debug=debug_mode)
