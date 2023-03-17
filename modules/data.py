from flask import Flask
from decouple import config
from pathlib import Path


class Data:
    __file_name: str = '<unknown>'
    __file_path: str = '<unknown>'
    __full_path: str = '<unknown>'
    __raw_file = None

    __is_tabulated: bool = False
    __headers_in_first_line: bool = True
    __use_custom_header: bool = False
    __custom_header: list = [str]
    __data_separator: str = ','
    __ignore_errors: bool = True
    __apply_types: bool = True
    __use_long_char: bool = False
    __size_field: list = [int]
    __headers: list = [str]
    __headers_type: list = [str]
    __data_errors_lines: list = [int]
    __data_errors_messages: list = [int]

    __data_frame: list = [dict]

    def __init__(self):
        # validar que el archivo de configuracion exista

        # configuracion de ruta del archivo
        self.__file_name = config('FILE_NAME')
        self.__file_path = Path(__file__).resolve(
        ).parent.parent/config('FILE_PATH')
        self.__full_path = self.__file_path/self.__file_name

        # configuracion de los datos del archivo
        self.__is_tabulated = self.__conversion_type(
            config('FILE_TABULATED'), "bool")

        self.__headers_in_first_line = self.__conversion_type(
            config('HEADERS_IN_FIRST_LINE'), "bool")
        self.__use_custom_header = self.__conversion_type(
            config('USE_CUSTOM_HEADER'), "bool")
        self.__custom_header = config(
            'CUSTOM_HEADER').split(config('SEPARATOR'))

        self.__data_separator = config('DATA_SEPARATOR')
        self.__format_data_separator()

        self.__headers_type = config('HEADERS_TYPE').split(config('SEPARATOR'))
        print(f"los tipos de datos de la cabecera son: {self.__headers_type}")
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
        # configuracion del manejo de errores
        self.__data_errors_messages.clear()
        self.__data_errors_lines.clear()

    def load_file(self):
        raw_record: str = '<unknown>'
        raw_fields: list = [str]
        format_fields: list = [any]
        format_record: dict = {str: any}
        n_line: int = 0
        if self.__file_exist():
            print("Archivo encontrado")
            self.__raw_file = open(self.__full_path, 'r')
            # si el archivo tiene cabecera le sumo a n_line
            if self.__headers_in_first_line:
                n_line += 1

            if self.__is_tabulated:
                print("Archivo tabulado")
                self.__resolve_headers()

                print("="*80)
                format_record.clear()
                for raw_record in self.__raw_file:
                    raw_record = raw_record.strip()
                    n_line += 1
                    print(f"el raw record es: {raw_record}")
                    raw_fields = self.__proccess_raw_record(raw_record)
                    print(f"los campos divididos son: {raw_fields}")

                    if len(self.__headers) != len(raw_fields):
                        self.__report_error(
                            n_line, f"El registro de la linea {n_line} no tiene la misma cantidad de campos que la cabecera")
                        if self.__ignore_errors:
                            continue
                        else:
                            self.__report_error(
                                -1, "Se encontraron errores en el archivo y se ha configurado para que no se ignoren se detuvo la lectura del archivo en la linea {n_line}")
                            break

                    format_fields.clear()
                    for index, fr in enumerate(raw_fields):
                        field = fr
                        # realizo la conversion de tipos y lo almaceno format fields
                        if self.__apply_types:
                            field = self.__conversion_type(
                                fr, self.__headers_type[index])
                        if field is None:
                            self.__report_error(
                                n_line, f"El campo {fr} de la linea {n_line} no se pudo convertir al tipo {self.__headers_type[index]}")
                            if self.__ignore_errors:
                                continue
                            else:
                                self.__report_error(
                                    -1, "Se encontraron errores en el archivo y se ha configurado para que no se ignoren se detuvo la lectura del archivo en la linea {n_line}")
                                break
                        format_fields.append(field)

                    print(f"los campos convertido son: {format_fields}")

                    # vinculo cada valor con su cabecera
                    format_record = dict(
                        zip(self.__headers.copy(), format_fields.copy()))
                    print(f"el registro convertido es: {format_record}")
                    # agrego el registro al data frame
                    self.__data_frame.append(format_record.copy())
                    print("*"*80)
                # print(self.__data_frame)
            else:
                print("Archivo no tabulado")
            self.__raw_file.close()
        else:
            print("Archivo no encontrado")
            self.__raw_file = None

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

    def __proccess_raw_record(self, raw_record: str) -> list[str]:
        raw_fields: list = [str]
        raw_fields.clear()
        raw_record = raw_record.strip()
        if self.__is_tabulated:
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
        else:
            pass
        return raw_fields.copy()

    def __report_error(self, line: int, error_message: str):
        self.__data_errors_lines.append(line)
        self.__data_errors_messages.append(error_message)

    def __file_exist(self) -> bool:
        if self.__full_path.is_file():
            return True
        else:
            # -1 indica que es un error del archivo en general y no en una linea en particular
            self.__report_error(
                -1, "Archivo no encontrado Verifica la ruta y el nombre del archivo")
            return False

    def __resolve_headers(self):
        if self.__headers_in_first_line:
            # capturo la primera linea y obligo a avanzar al "cursor"
            # para que se posicione en el inicio de los datos
            first_line_file = self.__raw_file.readline().strip()
            if self.__use_custom_header:
                print("Usando cabecera personalizada")
                self.__headers = self.__custom_header.copy()
            else:
                self.__headers = first_line_file.split(self.__data_separator)
        else:
            if self.__use_custom_header:
                print("Cabecera no in data - Usando cabecera personalizada")
                self.__headers = self.__custom_header.copy()

        print(f"los nombres de las cabeceras son: {self.__headers}")

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

    '''
    get functions
    '''

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
