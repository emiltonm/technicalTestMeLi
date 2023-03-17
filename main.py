from modules.data import Data


if __name__ == '__main__':
    source_data = Data()
    source_data.load_file()
    source_data.show_errors()
    # print(f"el nombre del archivo es: {source_data.get_file_name()}")
    # print(f"la ruta del archivo es: {source_data.get_file_path()}")
    # print(f"la extension del archivo es: {source_data.get_extension_file()}")
    # print(f"la ruta completa es: {source_data.get_full_path()}")
    # print(type(open(source_data.get_full_path(), 'r')))

    # before_load_process
    # after_load_process