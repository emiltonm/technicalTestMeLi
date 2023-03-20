from flask import Flask, jsonify
from decouple import Config, RepositoryEnv
from pathlib import Path

from modules.data import Data
from modules.api import API
from modules.database import Database

app = Flask(__name__)
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
    source_data.process_file()
    # source_data.show_errors()
    input_data = source_data.get_data()
    api_meli.set_api_data(input_data)
    api_meli.fetch_url_file()
    # api_meli.show_errors()
    response_api = api_meli.get_data()

    # database.show_errors()
    database.insert_many(response_api)
    return jsonify({'message': 'Proceso finalizado'})


if __name__ == '__main__':
    config_file = Path(__file__).resolve().parent/'.env.server'
    print(config_file)
    if config_file.is_file():
        config = Config(RepositoryEnv(config_file))
        debug_mode = config('SERVER_DEBUG')
        if debug_mode.upper() == 'TRUE':
            debug_mode = True
        else:
            debug_mode = False
        app.run(host=config('SERVER_HOST'),
                port=config('SERVER_PORT'), debug=debug_mode)
    else:
        print("Archivo de configuracion no encontrado")
        exit()
