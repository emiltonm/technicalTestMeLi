import re
import json
import requests
from decouple import Config, RepositoryEnv
from pathlib import Path


class API:
    __url_base: str
    __path: str
    __file_name: str
    __full_path: str
    __dict_data: dict = {}
    __memory_block: int = 0
    __full_path_cache: str = ""
    __data_errors_lines: list = []
    __data_errors_messages: list = []

    def __init__(self):
        # validar que el archivo de configuracion exista
        config_file = Path(__file__).resolve().parent.parent/'.env.api'
        if self.__file_exist(config_file, "Archivo de configuracion data.env no encontrado"):
            # Cargar variables de entorno desde un archivo específico
            config = Config(RepositoryEnv(config_file))
        else:
            return None

        if Path(self.__full_path_cache).exists():
            self.__clear_cache()

        self.__url_base = config('URL_BASE')
        #  valido que url base termine con / sino lo agrego
        if self.__url_base[-1] != "/":
            self.__url_base += "/"
        self.__path = Path(__file__).resolve(
        ).parent.parent/config('PATH_TO_APIS')
        self.__file_name = config('FILE_API')
        self.__full_path = self.__path/self.__file_name

        self.__memory_block = int(config('MB_BLOCKS_SIZE'))
        self.__full_path_cache = ""
        # configuracion del manejo de errores
        self.__data_errors_messages.clear()
        self.__data_errors_lines.clear()

    def fetch_api_data(self, data: any):
        self.__full_path_cache = ""
        # si data es una lista de diccionario lo copio a la variable dict_data
        # tambien se puede evaluar de la siguiente manera
        # if isinstance(data, list) and all(isinstance(elem, dict) for elem in data):
        # pero podria salir muy cara en cuanto a procesamiento
        if isinstance(data, list):
            self.__dict_data = data.copy()
            self.__process_url_file()
            return None
        if not self.__file_exist(data, "Archivo no encontrado Verifica la ruta y el nombre del archivo"):
            self.__dict_data.clear()
            # necesito saber si estoy trabajando con cache o no
            # para saber donde guardar la data una vez la procese
            # tener en cuenta que el api guarda directamente en dict_data
        else:
            self.__full_path_cache = data.parent/'api_cache.txt'
            if self.__full_path_cache.exists():
                self.__clear_cache()
            # leo el archivo por bloques
            print("Procesando archivo de cache...")
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
                    self.__dict_data = [json.loads(s) for s in data_in_text]
                    self.__process_url_file()

    def __file_exist(self, path: str, error_message: str = "", print_in_screen: bool = True) -> bool:
        if path.is_file():
            return True
        else:
            if print_in_screen:
                print(error_message)
            # -1 indica que es un error del archivo en general y no en una linea en particular
            self.__report_error(
                -1, error_message)
            return False

    def __report_error(self, line: int, error_message: str):
        self.__data_errors_lines.append(line)
        self.__data_errors_messages.append(error_message)

    def show_errors(self):
        for index, error in enumerate(self.__data_errors_messages):
            print(f"Error Linea {self.__data_errors_lines[index]}: {error}")

    def __process_url_file(self):
        process_url: str = ""
        key_list: list = []
        instruction_file = None
        if not self.__file_exist(self.__full_path, "Archivo no encontrado Verifica la ruta y el nombre del archivo"):
            instruction_file = None
        else:
            print("Archivo de instrucciones para las APIS encontrado")
            instruction_file = open(self.__full_path, 'r', encoding="utf-8")
            for template in instruction_file:
                template = template.strip()
                # salto las lineas en blanco y las que comienzan con # para poder comentar
                if template == "" or template[0] == "#":
                    continue
                for d in self.__dict_data:
                    # la url es la primera parte de la plantilla separada por ->
                    process_url = self.__parse_string_url(
                        template.split("->")[0], d)
                    # los nombres de las llaves son los string que se encuentran despues de ->
                    print(f"la URL resultante es: {process_url}")
                    key_list = template.split("->")[1].split(",")
                    if "processing_error" in d:
                        continue
                    else:
                        self.__resolve_url(process_url, d, key_list)
                    print(f"Diccionario: {d}")

            instruction_file.close()
            print("+"*80)
            for i in self.__dict_data:
                print(i)
            # si esta activo el cache guardo la data en el
            self.__save_cache()

    def __resolve_url(self, url: str, data: dict, key_list: list):
        # agrego al diccionario principal dict_data (llamado data en esta funcion) los datos que necesito
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print("Error al procesar la url")
            data["processing_error"] = True
            return None

        if response.status_code == 200:
            # print(f"la respuesta de la url es: {response.json()}")
            if isinstance(response.json(), list):
                # un for que extraiga las categorias y las guarde en data
                if response.json()[0]["code"] == 200:
                    for key in key_list:
                        data[key] = response.json()[0]["body"][key]
                else:
                    data["processing_error"] = True
                    print("Error al procesar la url")
            else:
                for key in key_list:
                    data[key] = response.json()[key]
        else:
            data["processing_error"] = True
            print("Error al procesar la url")
        #

    def __parse_string_url(self, template: str, data: dict) -> str:
        print("-"*80)
        print(f"La plantilla a procesar es: {template}")
        for tag in re.findall("<(.+?)>", template):
            if tag in data:
                template = self.__url_base + \
                    template.replace(f"<{tag}>", str(data[tag]))
        return template

    def __save_cache(self):
        if self.__full_path_cache:
            print("guardando datos del bloque API en cache")
            with open(self.__full_path_cache, 'a') as file:
                for d in self.__dict_data:
                    json.dump(d, file)
                    file.write("\n")
            self.__dict_data.clear()
            print(f"...{self.__dict_data}")

    def __clear_cache(self):
        if self.__full_path_cache:
            print("limpiando api cache")
            with open(self.__full_path_cache, 'w') as file:
                file.write("")

    # getters

    def get_data(self):
        if not self.__full_path_cache:
            print(f"Data enviada desde memoria")
            return self.__dict_data.copy()
        else:
            print(f"Se envio el archivo de cache API")
            return self.__full_path_cache

    # setters
