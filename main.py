from flask import Flask, jsonify

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
    app.run(debug=True, port=5000)
