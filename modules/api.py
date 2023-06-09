import re
import json
import requests
from requests import Response
from decouple import Config, RepositoryEnv
from pathlib import Path


class API:
    __url_base: str
    __path: str
    __file_name: str
    __full_path: str
    __dict_data: list = []
    __memory_block: int = 0
    __multiget: int = 0
    __full_path_cache: str = ""
    __data_errors_lines: list = []
    __data_errors_messages: list = []
    __relation: str = ""
    __key_to_request: str = ""
    __is_persistent_cache: bool = False
    __persistent_cache_path: str = ""

    def __init__(self):
        # validar que el archivo de configuracion exista
        config_file = Path(__file__).resolve().parent.parent/'.env.api'
        if not self.__file_exist(config_file, "Archivo de configuracion data.env no encontrado"):
            return None
        else:
            # Cargar variables de entorno desde un archivo específico
            config = Config(RepositoryEnv(config_file))

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

        self.__persistent_cache_path = Path(__file__).resolve(
        ).parent.parent/config('PERSISTENT_CACHE_PATH')

        self.__memory_block = int(config('MB_BLOCKS_SIZE'))
        self.__multiget = int(config('MULTIGET'))

        self.__full_path_cache = ""
        # configuracion del manejo de errores
        self.__data_errors_messages.clear()
        self.__data_errors_lines.clear()

    def fetch_api_data(self, data: any):
        print("="*80)
        print("EJECUTANDO MODULO API")
        print("="*80)
        self.__full_path_cache = ""
        # si data es una lista de diccionario lo copio al diccionario de datos principal (dict_data)
        if isinstance(data, list):
            self.__dict_data = data.copy()
            self.__process_url_file()
            return None
        # si data no es una lista se asume que es un string con la ruta del archivo donde estan almacenados los datos
        # esto sucedera cuando se trabaje con cache
        if not self.__file_exist(data, "Archivo no encontrado Verifica la ruta y el nombre del archivo"):
            self.__dict_data.clear()
        else:
            self.__full_path_cache = data.parent/'api_cache.csv'
            if self.__full_path_cache.exists():
                self.__clear_cache()
            # leo el archivo por bloques
            print("Procesando archivo de data cache desde el modulo api")
            with open(file=data, mode='r', encoding="utf-8") as file:
                while True:
                    # Lee el archivo en bloques de tamaño definido por size_block
                    block = file.read(
                        self.__memory_block * 1024 * 1024)
                    # Si no hay más bloques, finaliza el ciclo
                    if not block:
                        break
                    data_in_text = block.splitlines()
                    #elimino posibles entradas redundantes convirtiendo la lista en un set y nuevamente a una lista
                    data_in_text = list(set(data_in_text))
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
        if not self.__file_exist(self.__full_path, "Archivo de instrucciones API no encontrado verifica la ruta y el nombre del archivo"):
            instruction_file = None
        else:
            print(
                f"Archivo de instrucciones para las APIS [{self.__file_name}] encontrado")
            instruction_file = open(self.__full_path, 'r', encoding="utf-8")
            # por cada linea del archivo de instrucciones
            for template in instruction_file:
                block_data = []
                template = template.strip()
                # salto las lineas en blanco y las que comienzan con # para poder comentar
                if template == "" or template[0] == "#":
                    print(f"Saltando linea de instruccion en blanco o en comentario")
                    continue
                # si el simbolo es - guardara los datos en un archivo para no tener que consultar el api cada vez
                self.__is_persistent_cache = (template[0] == "-")
                # ismultiget sera True si el primer caracter de template es un * falso en caso contrario
                # el * indica que la url se debe procesar con multiget
                ismultiget = (template[0] == "*") and (self.__multiget > 0)
                if ismultiget:
                    # envio los datos en bloques
                    for i in range(0, len(self.__dict_data), self.__multiget):
                        block_data.append(
                            self.__dict_data[i:i+self.__multiget])
                else:
                    # bloque de un solo elemento
                    for i in range(0, len(self.__dict_data), 1):
                        block_data.append(self.__dict_data[i:i+1])
                # por cada REGISTRO (d) de la data (dict_data)
                for d in block_data:
                    # proceso la plantilla de instrucciones agregando los valores de las llaves
                    # la url es la primera parte de la plantilla separada por ->
                    process_url = self.__parse_string_url(
                        template[1:].split("->")[0], d)
                    print(
                        f"la URL resultante despues de procesar la plantilla es:\n{process_url}")

                    # elemento no valido no se agrega al bloque
                    if "processing_error" in d:
                        print(f"Elemento no valido {d}")
                        continue
                    # obtengo la lista de variables que voy a guardar de la peticion a la api
                    # los nombres de las llaves son los string que se encuentran despues de ->
                    key_list = template.split("->")[1].split(",")
                    if process_url:
                        self.__resolve_url(process_url, d, key_list)
                    print(f"Diccionario: {d}")
                    # d.clear()
            instruction_file.close()
            print("+"*80)
            for i in self.__dict_data:
                print(i)
            # si esta activo el cache guardo la data en el
            self.__save_cache()

    def __resolve_url(self, url: str, data: list, key_list: list):
        # reviso a ver si lo que busco ya esta en cache antes de ejecutar una peticion a la api
        response = None
        if self.__is_persistent_cache:
            response = self.__read_persistent_cache(
                self.__relation, self.__key_to_request)
        if not response:
            try:
                response = requests.get(url)
            except requests.exceptions.RequestException as e:
                print("Problemas con el request de la url")
                # data["processing_error"] = True
                return None
        else:
            print(f"Datos obtenidos de la cache persistente para {self.__relation}: {self.__key_to_request} peticion request no necesaria")
        
        if response.status_code == 200:
            # print(f"la respuesta de la url es: {response.json()}")
            if isinstance(response.json(), list):
                # por cada registro de la respuesta del json
                for r in response.json():
                    if r["code"] == 200:
                        # el api no devuelve los valores en el orden
                        # que se le pidio asi que necesito establecer
                        # una relacion entre mi data y la respuesta del api
                        # una clave unica y comun
                        for d in data:
                            if self.__relation in d:
                                if d[self.__relation] == r["body"]["id"]:
                                    for key in key_list:
                                        if key in r["body"]:
                                            d[key] = r["body"][key]
                                            # guardo en cache persistente el key y su valor
                                            if self.__is_persistent_cache:
                                                self.__save_persistent_cache(
                                                    self.__relation, d[self.__relation], r)
                    else:
                        for d in data:
                            if self.__relation in d:
                                if d[self.__relation] == r["body"]["id"]:
                                    d["processing_error"] = True
                                    print(f"Error al procesar el registro {d}")
            else:
                r = response.json()
                for d in data:
                    for key in key_list:
                        if key in r:
                            d[key] = r[key]
                            # guardo en cache persistente el key y su valor
                            if self.__is_persistent_cache:
                                self.__save_persistent_cache(
                                    self.__relation, d[self.__relation], r)

        else:  # es un 404 de toda la lista
            # print("Error al procesar la url")
            pass

    def __save_persistent_cache(self, file_name: str, key: str, value: any):

        p_cache = self.__persistent_cache_path / (file_name+".pcache")
        # si el archivo no existe se crea
        if not self.__file_exist(p_cache, f"Creando archivo  de cache permanente para {file_name}"):
            p_cache.touch()
        # si el archivo existe se revisa si el valor ya esta registrado
        with open(p_cache, mode='r', encoding='utf-8') as f:
            for line in f:
                record = json.loads(line.strip())
                if key in record:
                    return
        # si no esta registrado se guarda en el archivo
        with open(p_cache, mode='a', encoding='utf-8') as f:
            record = {key: value}
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            print(
                f"El dato {record} ha sido guardado en el cache persistente.")

    def __read_persistent_cache(self, file_name: str, key: str):
        p_cache = self.__persistent_cache_path / (file_name+".pcache")
        if self.__file_exist(p_cache, f"Buscando en cache permanente para {file_name}"):
            with open(p_cache, mode='r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line.strip())
                    if key in record:
                        response_json = json.dumps(record[key])
                        response=requests.models.Response()
                        response.status_code =200
                        response.headers['Content-Type'] = 'application/json'
                        response._content = response_json.encode()
                        response.encoding = 'utf-8'
                        response.reason = 'OK'
                        response.url = 'http://any_url.com'
                        return response
        return None

    def __parse_string_url(self, template: str, data: list) -> str:
        # data es un list[dict]
        print("-"*80)
        print(f"La plantilla a procesar es: {template}")
        # busco las llaves en la plantilla y reemplazo por los valores de las llaves
        # devuelvo las llaves en una lista que se itera con tag
        for tag in re.findall("<(.+?)>", template):
            # creo el string de los datos para la peticion por bloques
            items_to_query = ""
            for d in data:
                # si la llave tag esta en el diccionario d agrego el valor de la llave a items_to_query
                if tag in d:
                    items_to_query += str(d[tag])+","
                else:
                    # si la llave no esta en el diccionario creo una llave processing_error con valor True
                    print(f"Error: la llave {tag} no esta en el diccionario")
                    d["processing_error"] = True
            # elimino la ultima coma
            items_to_query = items_to_query[:-1]
            if items_to_query:
                template = template.replace(f"<{tag}>", items_to_query)
                self.__relation = tag
                self.__key_to_request = items_to_query
            else:
                template = ""
                self.__relation = ""
                self.__key_to_request = ""
        if template:
            template = self.__url_base + template
        return template

    def __save_cache(self):
        if self.__full_path_cache:
            print("guardando datos del bloque API en cache")
            with open(file=self.__full_path_cache, mode='a', encoding='utf-8') as file:
                for d in self.__dict_data:
                    json.dump(d, file)
                    file.write("\n")
            self.__dict_data.clear()
            print(f"...{self.__dict_data}")

    def __clear_cache(self):
        if self.__full_path_cache:
            print("limpiando api cache")
            with open(file=self.__full_path_cache, mode='w', encoding='utf-8') as file:
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

