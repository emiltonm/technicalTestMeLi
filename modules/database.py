import pymongo
import json
from decouple import Config, RepositoryEnv
from pathlib import Path
from pymongo.errors import OperationFailure
from pymongo.errors import ConnectionFailure


class Database:
    __mongo_uri: str
    __mongo_client: None
    __mongo_db: str
    __mongo_collection: str
    __data_errors_lines: list = [int]
    __data_errors_messages: list = [int]
    __id_field: str
    __memory_block: int = 0

    def __init__(self):
        # verificamos que el archivo de configuracion existe
        config_file = Path(__file__).resolve().parent.parent/'.env.database'

        if not self.__file_exist(config_file, "Archivo de configuracion .env.database no encontrado"):
            return None
        else:
            # el archivo de configuracion existe, cargo las variables de entorno
            config = Config(RepositoryEnv(config_file))
        # tamaño de bloques memoria cache
        self.__memory_block = int(config('MB_BLOCKS_SIZE'))
        # establecemos la conexion con la base de datos
        self.__mongo_uri = f"{config('MONGO_PROTOCOL')}://{config('MONGO_HOST')}:{config('MONGO_PORT')}/"
        print("-"*80)
        print(self.__mongo_uri)
        print("-"*80)
        try:
            self.__mongo_client = pymongo.MongoClient(self.__mongo_uri)
            self.__mongo_client.server_info()
            print("Conectado a MongoDB")
        except ConnectionFailure as e:
            print("Could not connect to MongoDB: %s" % e)

        self.__mongo_db = self.__mongo_client[config('MONGO_DB')]
        self.__mongo_collection = self.__mongo_db[config('MONGO_COLLECTION')]

        # linea para probar la conexion a la base de datos
        # self.__mongo_collection.insert_one({"name": "test"})

    def insert_one(self, document: dict):
        self.__mongo_collection.insert_one(document)

    def insert_many(self, data: list):
        self.__full_path_cache = ""
        # si data es una lista de diccionario lo envio directamente a la BD
        # tambien se puede evaluar de la siguiente manera
        # if isinstance(data, list) and all(isinstance(elem, dict) for elem in data):
        # pero podria salir muy cara en cuanto a procesamiento
        if isinstance(data, list):
            try:
                print("Insertando datos en la base de datos...")
                self.__mongo_collection.insert_many(data)
                print("Datos insertados correctamente")
            except OperationFailure as error:
                print("Error al intentar insertar los datos: ", error)
            return None
        if not self.__file_exist(data, "Archivo no encontrado Verifica la ruta y el nombre del archivo"):
            return None
        else:
            # leo el archivo por bloques
            print("Procesando archivo de cache de la API para guardar en la BD...")
            with open(data, 'r', encoding="utf-8") as file:
                while True:
                    # Lee el archivo en bloques de tamaño definido por size_block
                    block = file.read(
                        self.__memory_block * 1024 * 1024)
                    # Si no hay más bloques, finaliza el ciclo
                    if not block:
                        break
                    data_in_text = block.splitlines()
                    # convierto la lista de strings a una lista de diccionarios
                    dict_data = [json.loads(s) for s in data_in_text]

                    try:
                        print(
                            "Insertando datos en la base de datos desde la cache del API...")
                        self.__mongo_collection.insert_many(dict_data)
                        print("Datos insertados correctamente")
                    except OperationFailure as error:
                        print("Error al intentar insertar los datos: ", error)
                    return None

    def find_one(self, document_id: str) -> dict:
        print(
            f"ejecutando consulta a la base de datos del registro con id: {document_id}")
        doc = self.__mongo_collection.find_one({"id": document_id})
        doc["_id"] = str(doc["_id"])
        return json.loads(json.dumps(doc))

    def show_all(self, page: int, items_by_page: int) -> list:
        result = []
        docs = self.__mongo_collection.find().skip((page-1)*items_by_page).limit(items_by_page)
        for doc in docs:
            result.append(json.loads(json.dumps(doc, default=str)))
        return result
    
    def show_errors(self, page: int, items_by_page: int) -> list:
        result = []
        docs = self.__mongo_collection.find({"processing_error":True}).skip((page-1)*items_by_page).limit(items_by_page)
        for doc in docs:
            result.append(json.loads(json.dumps(doc, default=str)))        
        return result

    def count(self) -> int:
        return self.__mongo_collection.count_documents({})

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
