from decouple import Config, RepositoryEnv
from pathlib import Path
from pymongo import MongoClient


class Database:
    __mongo_uri: str
    __mongo_client: MongoClient
    __mongo_db: str
    __mongo_collection: str
    __id_field: str
    __data_errors_lines: list = [int]
    __data_errors_messages: list = [int]

    def __init__(self):
        # validar que el archivo de configuracion exista
        config_file = Path(__file__).resolve().parent.parent/'.env.database'

        if self.__file_exist(config_file, "Archivo de configuracion data.env no encontrado"):
            # Cargar variables de entorno desde un archivo específico
            config = Config(RepositoryEnv(config_file))
        else:
            return None
        # configuracion de ruta del archivo
        self.__mongo_uri = config('MONGO_URI')
        self.__mongo_client = MongoClient(self.__mongo_uri)
        self.__mongo_db = self.__mongo_client[config('MONGO_DB')]
        self.__mongo_collection = self.__mongo_db[config('MONGO_COLLECTION')]
        self.__id_field = config('MONGO_ID_FIELD')
        #  self.__mongo_collection.insert_one({"name": "test"})

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
