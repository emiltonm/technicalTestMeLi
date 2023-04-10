from flask import Flask, jsonify
from decouple import Config, RepositoryEnv
from pathlib import Path

from modules.data import Data
from modules.api import API
from modules.database import Database

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
    return jsonify({'/process': 'Para procesar el archivo',
                    '/find': 'para buscar un documento en la base de datos a partir de su id ej: localhost:5000/find/MLA123456',
                    '/show/int:pagina/int:items_por_pagina': 'para mostrar todos los documentos de la base de datos ej: localhost:5000/show/1/10',
                    '/show/errors/int:pagina/int:items_por_pagina': 'para mostrar todos los documentos de la base de datos que no pudieron ser procesados ej: localhost:5000/show/errors/1/10',
                    'Desarrollador': 'Emilton Mendoza Ojeda',
                    })


@app.route('/process', methods=['GET'])
def procesar():
    '''
    Funcion/ruta encargada de ejecutar todo el proceso de la aplicacion
    desde la lectura del archivo fuente de datos hasta la carga de los
    datos en la base de datos
    '''
    print("ejecutando el microservicio [procesar] de la ruta [/process]")
    # procesa el archivo fuente de datos lo convierte en un diccionario
    # o en un archivo de cache dependiendo de la configuracion elegida
    # al cual se accede con el metodo get_data()
    source_data.process_file()

    # obtengo la lista de datos o una url del archivo de cache
    data = source_data.get_data()

    # con la data obtenida del archivo fuente se crean las url para la
    # consulta de los datos en el API y luego se hace el llamado a las
    # url para obtener los datos
    api_meli.fetch_api_data(data)

    # obtengo la data del API o una url del archivo de cache
    new_data = api_meli.get_data()
    # se carga la data obtenida del API en la base de datos
    database.insert_many(new_data)

    return jsonify({'message': 'Proceso finalizado'})


@app.route('/find/<id>', methods=['GET'])
def get_by_id(id: str):
    '''
    Funcion encargada de obtener un documento de la base de datos mediante su id
    '''
    print("ejecutando el microservicio [get_by_id] de la ruta [/find]")
    document = database.find_one(id)
    return jsonify(document)


@app.route('/show/<int:page>/<int:items>', methods=['GET'])
def show_all(page: int, items: int):
    '''
    Funcion encargada de mostrar todos los documentos de la base de datos
    '''
    print("ejecutando el microservicio [show_all] de la ruta [/show]")
    documents = database.show_all(page, items)
    return jsonify(documents)


@app.route('/show/errors/<int:page>/<int:items>', methods=['GET'])
def show_errors(page: int, items: int):
    '''
    Funcion encargada de mostrar los registros que no pudieron ser procesados
    '''
    print("ejecutando el microservicio [show_all] de la ruta [/show/errors]")
    documents = database.show_errors(page, items)
    return jsonify(documents)


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
