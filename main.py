from modules.data import Data
from modules.api import API

if __name__ == '__main__':

    source_data = Data()
    source_data.process_file()
    # source_data.show_errors()
    input_data = source_data.get_data()

    api_meli = API(input_data)
    # api_meli.show_errors()
    response_api = api_meli.get_data()

    # database = Database()
    # database.load_file(documents)
    # database.show_errors()
