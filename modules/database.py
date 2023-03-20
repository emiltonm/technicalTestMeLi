from decouple import Config, RepositoryEnv
from pathlib import Path
import pymongo


class Database:
    __mongo_uri: str
    __mongo_client: None
    __mongo_db: str
    __mongo_collection: str
    __id_field: str
    __data_errors_lines: list = [int]
    __data_errors_messages: list = [int]

    def __init__(self):
        # verificamos que el archivo de configuracion existe
        config_file = Path(__file__).resolve().parent.parent/'.env.database'
        
        if not self.__file_exist(config_file, "Archivo de configuracion .env.database no encontrado"):
            return None
        else:
            # el archivo de configuracion existe, cargo las variables de entorno
            config = Config(RepositoryEnv(config_file))

        # establecemos la conexion con la base de datos
        self.__mongo_uri = "mongodb://"+config('MONGO_HOST')+":"+config('MONGO_PORT')+"/"+config('MONGO_DB')
        print(":"*800)
        print(self.__mongo_uri)
        try:
            self.__mongo_client = pymongo.MongoClient(self.__mongo_uri, serverSelectionTimeoutMS=config('MONGO_TIMEOUT'))
            self.__mongo_client.server_info()
            print("Conectado a MongoDB")
        except pymongo.errors.ServerSelectionTimeoutError as timeError:
            print("Error de conexion se excedido el tiempo: ", timeError)
            return None
        except pymongo.errors.ConnectionFailure as connectionError:
            print("Error de conexion: ", connectionError)
            return None
        self.__mongo_db = self.__mongo_client[config('MONGO_DB')]
        self.__mongo_collection = self.__mongo_db[config('MONGO_COLLECTION')]
        self.__id_field = config('MONGO_ID_FIELD')
        self.__mongo_collection.insert_one({"name": "test"})

    def insert_one(self, document: dict):
        self.__mongo_collection.insert_one(document)

    def insert_many(self, documents: list):
        self.__mongo_collection.insert_many(documents)

    def find_one(self, document: dict) -> dict:
        return self.__mongo_collection.find_one(document)

    def find_many(self, document: dict) -> dict:
        return self.__mongo_collection.find(document)

    def paginate(self, page: int, limit: int) -> list:
        return self.__mongo_collection.find().skip((page-1)*limit).limit(limit)

    def count(self) -> int:
        return self.__mongo_collection.count_documents({})

    def delete_one(self, document: dict):
        self.__mongo_collection.delete_one(document)

    def delete_many(self, document: dict):
        self.__mongo_collection.delete_many(document)

    def update_one(self, document: dict, new_document: dict):
        self.__mongo_collection.update_one(document, new_document)

    def update_many(self, document: dict, new_document: dict):
        self.__mongo_collection.update_many(document, new_document)

    def __process_document(self, dict_data: dict) -> dict:
        # cambio el nombre de la llave que se usara como id por _id
        for dict in dict_data:
            dict['_id'] = dict.pop(self.__id_field)
        return dict_data.copy()

    def __report_error(self, line: int, error_message: str):
        self.__data_errors_lines.append(line)
        self.__data_errors_messages.append(error_message)

    def __file_exist(self, path: str, error_message: str = "") -> bool:
        if path.is_file():
            return True
        else:
            # -1 indica que es un error del archivo en general y no en una linea en particular
            self.__report_error(
                -1, error_message)
            return False
