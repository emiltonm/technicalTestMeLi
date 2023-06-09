import sys
import os
import re
import json
import importlib
from decouple import Config, RepositoryEnv
from pathlib import Path


class Data:
    __file_name: str = ''
    __file_path: str = ''
    __full_path: str = ''
    __file_encoding: str = ''
    __raw_file: list = [str]

    __memory_block: int = 1
    __first_block: bool = True
    __data_cache: bool = True
    __full_path_cache: str = ''
    __cache_file_name: str = ''

    __is_tabulated: bool = False
    __headers_in_first_line: bool = True
    __use_custom_header: bool = False
    __custom_header: list = [str]
    __data_separator: str = ','
    __apply_types: bool = True
    __use_long_char: bool = False
    __size_field: list = [int]
    __headers: list = [str]
    __headers_type: list = [str]

    __ignore_errors: bool = True
    __data_errors_lines: list = [int]
    __data_errors_messages: list = [int]

    __field_template: str = ''
    __clip_start: int = 0
    __clip_end: int = 0

    __affect_raw_record: bool = False
    __scripts_path: str = ''
    __scripts_raw_record: list = []

    __data_frame: list = [dict]
    __n_line: int = 0

    def __init__(self):
        # valida que el archivo de configuracion exista
        config_file = Path(__file__).resolve().parent.parent/'.env.data'

        if not self.__file_exist(config_file, "Archivo de configuracion .env.data no encontrado"):
            return None
        else:
            print("Estableciendo variables de entorno desde .env.data ")
            config = Config(RepositoryEnv(config_file))

        # configuracion de ruta del archivo de datos
        self.__file_name = config('FILE_NAME')
        self.__file_path = Path(__file__).resolve(
        ).parent.parent/config('FILE_PATH')
        self.__full_path = self.__file_path/self.__file_name
        # configuracion de los datos del archivo
        self.__file_encoding = config('FILE_ENCODING')
        self.__memory_block = self.__conversion_type(
            config('MB_BLOCKS_SIZE'), "int")
        self.__first_block = True
        self.__raw_file.clear()
        self.__data_cache = self.__conversion_type(
            config('DATA_CACHE'), "bool")
        self.__cache_file_name = config('CACHE_FILE_NAME')

        self.__full_path_cache = self.__file_path/'cache'
        # si la carpeta cache no existe la crea
        if not self.__full_path_cache.exists():
            self.__full_path_cache.mkdir()
        self.__full_path_cache = self.__file_path/'cache'/self.__cache_file_name
        # si estoy iniciando y ya existe el archivo de cache lo limpio
        if self.__full_path_cache.exists():
             self.__clear_cache()

        self.__is_tabulated = self.__conversion_type(
            config('FILE_TABULATED'), "bool")

        self.__headers_in_first_line = self.__conversion_type(
            config('HEADERS_IN_FIRST_LINE'), "bool")
        self.__use_custom_header = self.__conversion_type(
            config('USE_CUSTOM_HEADER'), "bool")
        self.__custom_header = config(
            'CUSTOM_HEADER').split(config('SEPARATOR'))

        self.__data_separator = config('DATA_SEPARATOR')
        # convierte las etiquetas TAB o SPACE en los caracteres correspondientes
        self.__format_data_separator()

        self.__headers_type = config('HEADERS_TYPE').split(config('SEPARATOR'))
        self.__apply_types = self.__conversion_type(
            config('APPLY_TYPES'), "bool")
        self.__ignore_errors = self.__conversion_type(
            config('IGNORE_ERRORS_DATA'), "bool")
        self.__use_long_char = self.__conversion_type(
            config('USE_LONG_CHAR_SEPARATOR'), "bool")

        self.__size_field = config(
            'LONG_CHAR_SEPARATOR').split(config('SEPARATOR'))
        for i in range(len(self.__size_field)):
            if self.__size_field[i].isnumeric():
                self.__size_field[i] = int(self.__size_field[i])
            else:
                self.__size_field[i] = 0

        self.__n_line = 0

        self.__field_template = config('FIELD_TEMPLATE')
        self.__clip_start = int(config('CLIP_START'))
        self.__clip_end = int(config('CLIP_END'))

        #  configuracion de los scripts
        self.__affect_raw_record = self.__conversion_type(
            config('AFFECT_RAW_RECORD'), "bool")
        self.__scripts_raw_record = config(
            'SCRIPTS').split(config('SEPARATOR'))
        self.__scripts_path = config('SCRIPTS_PATH')

        # configuracion del manejo de errores
        self.__data_errors_messages.clear()
        self.__data_errors_lines.clear()

    def process_file(self):
        '''
        Procesa el archivo de datos, el resultado de este proceso
        se puede obtener llamando al metodo get_data() -> list[dict]
        '''
        self.__data_frame.clear()
        if not self.__file_exist(self.__full_path, "Archivo de datos no encontrado verifica la ruta y el nombre del archivo"):
            self.__raw_file.clear()
        else: 
            print(f"Procesando archivo de datos {self.__file_name}...")
            with open(self.__full_path, 'r', encoding=self.__file_encoding) as file:
                while True:
                    # Lee el archivo en bloques de tamaño definido por size_block
                    block = file.read(
                        self.__memory_block * 1024 * 1024)
                    # Si no hay más bloques, finaliza el ciclo
                    if not block:
                        break

                    self.__raw_file = block.splitlines()
                    print("="*80)
                    print("PROCESANDO ARCHIVO DE DATOS")
                    print("="*80)
                    if self.__is_tabulated:
                        self.__process_tabulated_file()
                    else:
                        self.__process_not_tabulated_file()

    def __process_tabulated_file(self):
        print("El archivo sera procesado como tabulado")
        raw_record: str = ''
        raw_fields: list = [str]
        format_fields: list = [any]
        format_record: dict = {str: any}

        format_fields.clear()
        format_record.clear()

        self.__resolve_headers()

        for raw_record in self.__raw_file:
            if self.__first_block and self.__headers_in_first_line:
                self.__first_block = False
                continue
            self.__n_line += 1
            print(f"raw_record es:\n{raw_record}")
            # ejecutos los scripts que afectan al registro
            # cuando aun es una linea de texto
            if self.__affect_raw_record:
                raw_record = self.__execute_scripts(raw_record)
                print(f"raw_record despues de ejecutar la lista de scripts :\n{raw_record}")
            raw_fields = self.__process_raw_record(raw_record)
            print(f"los valores del registro son:\n{raw_fields}")

            if len(self.__headers) != len(raw_fields):
                self.__report_error(
                    self.__n_line, f"El registro de la linea {self.__n_line} no tiene la misma cantidad de campos que la cabecera")
                if self.__ignore_errors:
                    continue
                else:
                    self.__report_error(
                        -1, "Se encontraron errores en el archivo y se ha configurado para que no se ignoren se detuvo la lectura del archivo en la linea {self.__n_line}")
                    break

            format_fields = self.__process_tabulated_fields(raw_fields)
            # vinculo cada valor con su cabecera
            format_record = dict(
                zip(self.__headers.copy(), format_fields.copy()))
            print(f"el registro convertido es: {format_record}")
            # agrego el registro al data frame
            self.__data_frame.append(format_record.copy())
            print("-"*80)
        self.__save_cache()

    def __process_raw_record(self, raw_record: str) -> list[str]:
        raw_fields: list = [str]
        raw_fields.clear()
        raw_record = raw_record.strip()
        #  divido los valores de los campos por su cantidad de caracteres
        #  en caso de que los campos vengan dados por cantidad de caracteres
        if self.__use_long_char:
            inferior_limit = 0
            superior_limit = 0
            for i in range(len(self.__size_field)):
                superior_limit = self.__size_field[i]
                raw_fields.append(
                    raw_record[inferior_limit:inferior_limit+superior_limit])
                inferior_limit = inferior_limit + superior_limit
        else:
            raw_fields = raw_record.split(self.__data_separator)
        return raw_fields.copy()

    def __process_tabulated_fields(self, raw_fields: list[str]):
        format_fields: list = [any]
        format_fields.clear()
        for index, fr in enumerate(raw_fields):
            field = fr
            # realizo la conversion de tipos y lo almaceno format fields
            if self.__apply_types:
                field = self.__conversion_type(
                    fr, self.__headers_type[index])
            if field is None:
                self.__report_error(
                    self.__n_line, f"El campo con el valor {fr} de la linea {self.__n_line} no se pudo convertir al tipo {self.__headers_type[index]}")
                if self.__ignore_errors:
                    continue
                else:
                    self.__report_error(
                        -1, "Se encontraron errores en el archivo y se ha configurado para que no se ignoren se detuvo la lectura del archivo en la linea {self.__n_line}")
                    break
            format_fields.append(field)
        print(f"los valores del registro con su conversion de tipo aplicada son:\n{format_fields}")
        return format_fields.copy()

    def __process_not_tabulated_file(self):
        print("Archivo no tabulado")
        raw_record: str = ''
        format_record: dict = {str: any}

        format_record.clear()
        # caracteres que seran escapados (se le agrega \ antes de ellos) en la planrilla
        special_chars = ['[', ']', '(', ')', '{', '}']
        expression = self.__field_template
        # escapamos los caracteres especiales
        for char in special_chars:
            expression = expression.replace(char, '\\'+char)
        # en las siguientes 3 lineas armamos la expresion regular a partir de la plantilla de campos
        # reemplazamos el primer H (header) por la expresion(\w+)
        # que signifca cualquier caracter alfanumerico
        expression = expression.replace('H', '(\w+)', 1)
        # reemplazamos el primer y unico V (value) por la expresion([\w\s.]+)
        # que significa cualquier caracter alfanumerico espacio o punto
        expression = expression.replace('V', '([\w\s.]+)', 1)
        # si existe mas de un H comunmente usado en etiquetas de cierre como xml se reemplaza por '\1'
        # que significa que se toma el primer grupo de la expresion regular (por eso el numero 1)
        # es decir si existe otra etiqueta H su valor debe ser igual al de la primera etiqueta H
        expression = expression.replace('H', '\\1', 1)

        print(
            f"la expresion regular con la que se evaluara RAW RECORD es: {expression}")
        # compilamos la expresion regular para mejoras en el rendimiento
        pattern = re.compile(expression)
        for raw_record in self.__raw_file:
            if self.__first_block and self.__headers_in_first_line:
                self.__first_block = False
                continue
            print("="*80)
            self.__n_line += 1
            print(f"el raw record es: \'{raw_record}\'")
            #  Elimino los caracteres de inicio y fin de raw record que no necesito
            if self.__clip_start > 0:
                raw_record = raw_record[self.__clip_start:]
            if self.__clip_end > 0:
                raw_record = raw_record[:-self.__clip_end]
            # Elimino comillas dentro de raw record
            raw_record = raw_record.replace('"', '')
            #  ejecuto los scripts
            raw_record = self.__execute_scripts(raw_record)
            #  en matches quedan almacenados en una lista de tuplas con formato:
            #  [(header, value), (header, value), (header, value), ...]
            matches = pattern.findall(raw_record)
            #  convierto la tupla en listas para poder modificarla
            fields = [list(t) for t in matches]
            print(f"los fields son: {fields}")
            for field in fields:
                #  borro caracteres de espacio en blanco al inicio y al final de cada campo
                field[1] = field[1].strip()
            print(f"los valores de los fields formateados son: {fields}")
            #  convierto a diccionario
            format_records = dict(fields)
            print(f"el registro terminado el proceso es:\n{format_records}")
            # agrego el registro al data frame
            self.__data_frame.append(format_records.copy())

    def show_errors(self):
        for index, error in enumerate(self.__data_errors_messages):
            print(f"Error Linea {self.__data_errors_lines[index]}: {error}")

    def __format_data_separator(self):
        key_words = ['tab', 'space']
        special_chars = ['\t', ' ']
        for i, word in enumerate(key_words):
            if self.__data_separator.lower() == word:
                self.__data_separator = special_chars[i]
                break

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

    def __resolve_headers(self):
        # si la cabecera esta en la primera linea del archivo y
        # es el primer bloque de datos
        if self.__headers_in_first_line and self.__first_block:
            first_line_file = self.__raw_file[0]
            self.__n_line += 1
            if self.__use_custom_header:
                print("Usando cabecera personalizada")
                self.__headers = self.__custom_header.copy()
            else:
                self.__headers = first_line_file.split(self.__data_separator)
        else:
            if self.__use_custom_header:
                print("Cabecera no in data - Usando cabecera personalizada")
                self.__headers = self.__custom_header.copy()

        print(f"los nombres de las cabeceras son:\n{self.__headers}")
        print("-"*80)

    def __conversion_type(self, str_value: str, convert_type: str) -> any:
        ''' 
        convierte una variable de tipo string al tipo indicado
        los tipos soportados son str, int, float, bool;
        en caso de no ser posible la conversion retorna None
        '''
        if (convert_type == "str"):
            return (str_value)

        if (convert_type == "int"):
            try:
                format_value = int(str_value)
            except:
                format_value = None
            return format_value

        if (convert_type == "float"):
            try:
                format_value = float(str_value)
            except:
                format_value = None
            return format_value

        if (convert_type == "bool"):
            if str_value.lower() == "true":
                return True
            if str_value.lower() == "false":
                return False
            return None

        return None

    def __execute_scripts(self, raw_record: str) -> str:
        #  obtengo la ruta del archivo de scripts al path del sistema para que puedan ser importados
        s_path = Path(__file__).resolve().parent.parent/self.__scripts_path
        dir_path = os.path.abspath(s_path)
        sys.path.append(dir_path)

        if self.__affect_raw_record:
            # recorro la lista de scripts y les paso el raw record
            # para que puedan modificarlo
            for name_script in self.__scripts_raw_record:
                name_script = name_script.strip()
                full_path_script = s_path/(name_script+".py")
                if not self.__file_exist(full_path_script, f"El script {name_script} no fue encontrado en la ruta indicada"):
                    continue
                else:
                    print(
                        f"**El script [{name_script}] modificara el raw record actual")
                    scripts = self.__get_script_from_module(name_script)
                    for script in scripts:
                        raw_record = script(raw_record)
        return raw_record

    def __get_script_from_module(self, module_name: str) -> list[any]:
        #  carga el modulo (archivo.py)
        #  no tiene problemas con la ruta puesto que se agrego al path del sistema
        #  asi que solo basta con su nombre
        module = importlib.import_module(module_name)
        #  recorre todos los objetos que hay dentro del modulo (archivo.py)
        #  estos objetos pueden ser funciones, clases, variables, etc.
        #  si el objeto en callable (es decir una funcion) lo agrega a la lista
        #  de functions
        functions = [getattr(module, f) for f in dir(
            module) if callable(getattr(module, f))]
        return functions

    def __save_cache(self):
        if self.__data_cache: 
            print(f"guardando datos en la cache de data [{self.__cache_file_name}]")
            with open(self.__full_path_cache, 'a') as file:
                for d in self.__data_frame:
                    json.dump(d, file)
                    file.write("\n")
            self.__data_frame.clear()

    def __clear_cache(self):
        if self.__data_cache:
            print("limpiando memoria cache de data")
            with open(self.__full_path_cache, 'w') as file:
                file.write("")

    '''
    get functions
    '''

    def get_data(self) -> any:
        '''
        retorna una copia de los datos cargados del archivo de datos en formato diccionario
        '''
        if not self.__data_cache:
            print(f"Data enviada desde memoria")
            return self.__data_frame.copy()
        else:
            print(f"Data enviada como archivo cache [{self.__cache_file_name}]")
            return self.__full_path_cache

    def get_file_name(self) -> str:
        return self.__file_name

    def get_extension_file(self) -> str:
        return self.__file_name.split('.')[-1]

    def get_file_path(self) -> str:
        return self.__file_path

    def get_full_path(self) -> str:
        return self.__full_path

    def get_headers_in_data(self) -> bool:
        return self.__headers_in_first_line

    def get_custom_header(self) -> list:
        return self.__custom_header.copy()

    def get_data_separator(self) -> str:
        return self.__data_separator

    def get_is_tabulated(self) -> bool:
        return self.__is_tabulated

    '''
    set functions
    '''

    def set_file_name(self, file_name: str):
        self.__file_name = file_name

    def set_file_path(self, file_path: str):
        self.__file_path = file_path

    def set_full_path(self, full_path: str):
        self.__full_path = full_path

    def set_headers_in_data(self, in_data: bool):
        self.__headers_in_first_line = in_data

    def set_use_custom_header(self, use_custom_header: bool):
        self.__use_custom_header = use_custom_header

    def set_custom_header(self, custom_header: list[str]):
        self.__custom_header = custom_header.copy()

    def set_data_separator(self, data_separator: str):
        self.__data_separator = data_separator

    def set_is_tabulated(self, is_tabulated: bool):
        self.__is_tabulated = is_tabulated
