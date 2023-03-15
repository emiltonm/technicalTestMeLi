from flask import Flask
from decouple import config
from pathlib import Path

app = Flask(__name__)
keys = []
header_type = []
data_error_lines = []


def conversion_type(str_value, convert_type):
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


def get_data():
    source_data = []
    path_script = Path(__file__).resolve().parent
    path_data = path_script.parent/'data'/config('DATA_FILE')
    index_error = 0
    valid_row = True
    data_error_lines.clear()

    if not path_data.is_file():
        # Archivo no encontrado
        return [None, "Archivo no encontrado Verifica la ruta y el nombre del archivo"]

    file = open(path_data, 'r')

    # resolviendo cabeceras/nombres de columnas de los datos
    if (config('HEADERS_IN_DATA').lower() == "true"):
        first_line = file.readline().strip()
        if (config('USE_CUSTOM_HEADER').lower() == "true"):
            keys = config('CUSTOM_HEADER').split(',')
        else:
            keys = first_line.split(config('DATA_SEPARATOR'))
    else:
        keys = config('CUSTOM_HEADER').split(config('DATA_SEPARATOR'))

    # paso de datos de archivo a lista
    if (config('APPLY_TYPES').lower() == "true"):
        header_type = config('TYPES_HEADER').lower().split(',')
        format_row = []
        for row in file:
            valid_row = True
            index_error = index_error+1
            temp_row = row.strip().split(config('DATA_SEPARATOR'))
            # si el numero de campos del registro no coincide con el numero de columnas
            # existe una inconsistencia en los datos
            if len(temp_row) != len(keys):
                print(
                    f"Inconsistencia entre la cantidad columnas y el numero de campos en el registro {index_error}")
                if (config('IGNORE_ERROR_DATA').lower() == "true"):
                    data_error_lines.append(index_error)
                    valid_row = False
                    continue
                else:
                    return [None, f"Inconsistencia entre la cantidad columnas y el numero de campos en el registro {index_error}"]
            for index, field in enumerate(temp_row):
                field_value = conversion_type(field, header_type[index])
                # sin errores en la conversion
                if field_value != None:
                    format_row.append(field_value)
                # errores en la conversion
                else:
                    print(
                        f"Inconsistencia en el tipo de dato esperado  {index_error}")
                    if (config('IGNORE_ERROR_DATA').lower() == "true"):
                        data_error_lines.append(index_error)
                        valid_row = False
                        continue
                    else:
                        return [None, f"Inconsistencia en el tipo de dato esperado linea # {index_error}"]
            if (valid_row == True):
                source_data.append(format_row.copy())
            format_row.clear()
    else:
        # todos los datos son almacenados como string
        for row in file:
            source_data.append(row.strip().split(config('DATA_SEPARATOR')))

    file.close

    return source_data


if __name__ == '__main__':
    data = get_data()
    for index,record in enumerate(data):
        if record[0]=="":
            print(f"el sitio en la linea {index} es nulo")
            continue
        if record[0] not in ["MLA","MLB"]:
            print(f"el sitio en la linea {index} no existe")
    # app.run(debug=config('SERVER_DEBUG_MODE'), port=config('SERVER_PORT'))


# verificar que el archivo exista
# que si la variable headers in data es falsa debe existir obligatoriamente un custom header
# que el numero de headers coincida con el de las columnas
# incluir tipo fecha en la data
