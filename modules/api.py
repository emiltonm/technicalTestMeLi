import re
import requests
from decouple import Config, RepositoryEnv
from pathlib import Path


class API:
    __url_base: str
    __path: str
    __file_name: str
    __full_path: str
    __list_file = None
    __dict_data: dict = {}
    __api_data: list = []

    __data_errors_lines: list = []
    __data_errors_messages: list = []

    def __init__(self, dict_data: dict):
        # validar que el archivo de configuracion exista
        config_file = Path(__file__).resolve().parent.parent/'.env.api'
        if self.__file_exist(config_file, "Archivo de configuracion data.env no encontrado"):
            # Cargar variables de entorno desde un archivo específico
            config = Config(RepositoryEnv(config_file))
        else:
            return None

        self.__dict_data = dict_data.copy()
        print(f"El diccionario de datos es: {self.__dict_data}")
        self.__url_base = config('URL_BASE')
        #  valido que url base termine con / sino lo agrego
        if self.__url_base[-1] != "/":
            self.__url_base += "/"
        self.__path = Path(__file__).resolve(
        ).parent.parent/config('PATH_TO_APIS')
        self.__file_name = config('FILE_API')
        self.__full_path = self.__path/self.__file_name

        # cargo el archivo de las plantillas url
        self.__load_url_file()

        # configuracion del manejo de errores
        self.__data_errors_messages.clear()
        self.__data_errors_lines.clear()

    def __file_exist(self, path: str, error_message: str = "") -> bool:
        if path.is_file():
            return True
        else:
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

    def __load_url_file(self):
        process_url: str = ""
        key_list: list = []
        self.__api_data.clear()
        if self.__file_exist(self.__full_path, "Archivo no encontrado Verifica la ruta y el nombre del archivo"):
            print("Archivo de APIS encontrado")
            self.__list_file = open(self.__full_path, 'r', encoding="utf-8")
            for template in self.__list_file:
                template = template.strip()
                # salto las lineas en blanco y las que comienzan con #
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

            self.__list_file.close()
            print("+"*80)
            for i in self.__dict_data:
                print(i)
        else:
            print("Archivo no encontrado")
            self.__list_file = None

    def __resolve_url(self, url: str, data: dict, key_list: list):
        # agrego al diccionario principal los datos que necesito
        # data["nuevo_campo"] = "nuevo_valor"
        # data["new_field"] = "new_value"
        response = requests.get(url)

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

    def __parse_string_url(self, template: str, data: dict) -> str:
        print("-"*80)
        print(f"La plantilla a procesar es: {template}")
        for tag in re.findall("<(.+?)>", template):
            if tag in data:
                template = self.__url_base + \
                    template.replace(f"<{tag}>", str(data[tag]))
        return template
    
    # getters
    def get_data(self):
        return self.__dict_data
    
    # setters
