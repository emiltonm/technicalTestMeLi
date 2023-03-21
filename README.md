# Desafío Técnico Mercado Libre
# Descripción del desafío
La prueba esta dividida en dos partes una técnica y otra teórica:
### Parte técnica
Consiste en ejecutar un servicio web dentro de un docker container, el servicio debe:
- **Leer un archivo** en formato streameable (csv,txt,jsonlines)  
  - La forma de lectura de este archivo debe poder configurarse en el programa, sin que estos cambios afecten el código.
  - Tener en cuenta que este archivo puede ser mas grande que la memoria disponible.
  - _detalles:_
    - el archivo consta de 2 columnas (site,id)

- Con los datos obtenidos de el archivo **consultar el API publica de mercado libre**
  - La consulta a la API se debe hacer de la manera mas rapida posible.
  - La consulta a la API debe ser eficiente en cuanto al consumo de recursos del sistema
  - Permitir que se puedan agregar nuevas consultas de APIs. 
  - _detalles:_
    - el código de los items es site + id
    - del api items obtener price y start_time
    - con el category_id obtener el nombre de la categoria (name)
    - con el currency_id obtener description de la api currencies
    - con seller_id obtener nickname de user

- **Guardar en una base de datos** la respuesta de el API, los campos a guardar son:
  - **site** (obtenido del file)
  - **id** (obtenido del file)
  - **price** (obtenido de la api de ítems)
  - **start_time** (obtenido de la api de ítems)
  - **name** (obtenido de la api de categorías)
  - **description** (obtenido de la api de monedas)
  - **nickname** (obtenido de la api de users)
  - _detalles:_
    - La base de datos se debe levantar en un container
    - el motor puede ser no relacional
    - se puede utilizar una imagen existente
- Brindar una forma de poder **acceder a esos datos**

### Parte Teórica
consiste en sustentar una serie de preguntas, esta parte del desafío es resuelta en el archivo readme.md que sen encuentra en la carpeta _Desafio Teórico_ 

# Descripción general de la solución
para dar solución a este desafio se dividio en 4 modulos:
- **data**: se encarga de leer el archivo base y de generar los datos para la consulta a la api
- **api**: con los datos procesados del modulo data genera las URL de consultas para la API y realiza la peticion a la API
- **database**: se encarga de guardar los datos entregados por el modulo api en la base de datos
- **app**: se encarga de levantar el servicio web,este servicio web permite procesar los datos y consultar los datos guardados en la base de datos

para simplificar la lectura de descripcion se utilizara la siguiente notacion para las propiedades de las clases: ([-,+][-,G][-,S]) _<tipo_de_dato>_ **nombre_propiedad**: funcion de la propiedad; donde el primer caracter indica si es *publica o privada* el segundo si tiene un *metodo get* para acceder a ella y el tercero si existe un *metodo set* para modificar su valor ejemplo:

(-GS) _< string >_ **file_path**: ruta relativa donde se encuentra el archivo de datos a partir de app.py

(+--) _< int >_ **size**: numero de registros que contiene el archivo de datos

en el primero de los ejemplos indica que la propiedad es privada y tiene un metodo get y set, y es de tipo string; en el segundo de los ejemplos indica que la propiedad es publica y no tiene metodos get ni set, y es de tipo int


# Detalle de modulo Data
_configurar el modulo data a traves del archivo .env.data_

Se encarga de leer el archivo base y de generar un diccionario de datos para la consulta a la api.

**False** se asume que en cada registro el orden de los datos (los fields) no es correspondiente al de las columnas y que no todas las columnas deben tener todos los datos. ejemplo de un registro no tabulado dentro del mismo archivo podria tener la siguiente estructura:
```  
{"nombre":"Emilton","apellido":"Mendoza ojeda", "sexo":"M"}

y esta otra...

{"apellido":"Garcia Marquez","nombre":"Gabriel"} 
```
si es **False** no se tendran en cuenta las siguientes propiedades del archivo de configuracion... (listar propiedades) 

habilita la ejecucion de scripts que modifica al registro cuando aun es una linea de texto, esto permite un amplio rango de posibilidades para la manipulacion de los datos. por ejemplo se puede utilizar para eliminar caracteres especiales, ejemplo las llaves de inicio y de cierre {} de los jsonlines; modificar valores de campos, (ejemplo pasara de formato largo del sexo a corto MASCULINO -> M), etc.

Secuencia de ejecución:
- **carga archivo de configuracion**: carga el archivo de configuracion .env.data en caso de no encontrarse detiene la ejecución del proceso, este archivo esta ubicado en la raiz del proyecto y contiene las propiedades necesarias para la ejecución del modulo data estas propiedades son:
  - **SEPARATOR**: _(character)_ caracter separador para las listas DENTRO de este mismo documento (.env.data) no confundir con DATA_SEPARATOR
  - **FILE_PATH**: _(string)_ ruta relativa donde se encuentra el archivo de datos a partir de app.py
  - **FILE_NAME**: _(string)_ nombre del archivo de datos a procesar
  - **FILE_ENCODING**: _(string)_ tipo de codificacion del archivo de datos
  - **DATA_SEPARATOR**: _(character or tag)_ caracter que sirve como separador del valor de cada uno de los campos, utilizar la palabra TAB,SPACE para indicar que el separador es un tabulador o espacio en blanco respectivamente
  - **FILE_TABULATED**:_(boolean)_ **True** si el archivo conserva el mismo orden de datos en cada registro ejemplo un CSV y el numero de datos por registro coincide con el numero de columnas 
  - **AFFECT_RAW_RECORD**:_(boolean)_ habilita la ejecucion de scripts que modifica al registro cuando aun es una linea de texto
  - **SCRIPTS_PATH**: _(string)_ ruta relativa desde el directorio del proyecto en la cual se encuentran los scripts que se ejecutaran en cada registro
  - **SCRIPTS**: _(string,string,...)_ lista de scripts separados por SEPARATOR que se ejecutaran en cada registro, todos los scripts deben recibir un unico argumento de tipo string y retornar un string
  - **HEADERS_IN_FIRST_LINE**:_(boolean)_ **True** si el archivo contiene en su primera linea los nombres de los campos/claves del diccionario que se generara
  - **USE_CUSTOM_HEADER**: _(boolean)_ **True** si se desea utilizar nombres de columnas/claves personalizados 
  - **CUSTOM_HEADER**: _(string,string,...)_ lista de nombres personalizados para las columnas/claves separados por SEPARATOR se tiene encuenta el orden y que el archivo sea tabulado  
  - **APPLY_TYPES**: por defecto todos los campos son leidos como tipo string, si se desea que se apliquen tipos de datos personalizados se debe colocar en **True** esta propiedad
  - **HEADERS_TYPE**: _(tag,tag,...)_ lista de tipos de datos separados por SEPARATOR, se tiene encuenta el orden y que el archivo sea tabulado. los tipos de datos validos son int,str,float,bool. para futuras versiones se podria agregar mas tipos de datos como el date
  - **USE_LONG_CHAR_SEPARATOR**: _(boolean)_ **True** si los campos vienen separados por su cantidad de caracteres, ejemplo:
    ```
    emilton1983col1
    eduardo1986arg1
    carlos 1000ecu0
    ana    2000ven0
    ```
    
  - **LONG_CHAR_SEPARATOR**:_(int,int,...)_ lista de cantidad de caracteres los campos
  - **IGNORE_ERRORS_DATA**: _(boolean)_ **True** para ignorar el registro actual si tiene alguna inconsistencia y continuar con el siguiente **False** para detener la ejecucion del proceso (ignora todo el registro no solamente el campo inconsistente)
  
  - **FIELD_TEMPLATE**: _(string)_ cadena que contiene el formato en que vienen almacenados los campos en cada registro de un archivo no tabulado el formarto es H (header,key) V (value) ejemplos:
    ```
    H:V separa los campos de registros con el siguiente formato:

    nombre:Emilton,apellido:Mendoza ojeda,sexo:M

    <H>V</H> separa los campos de registros con el siguiente formato:

    <nombre>Emilton</nombre><apellido>Mendoza ojeda</apellido><sexo>M</sexo>

    H=V separa los campos de registros con el siguiente formato:

    nombre=Emilton,apellido=Mendoza ojeda,sexo=M
    ```
     
  - **CLIP_START**:  _(int)_ numero de caracteres a ignorar desde el inicio de cada registro
  - **CLIP_END**: _(int)_ numero de caracteres a ignorar desde el final de cada registro


### Propiedades de la clase Data

(-GS) _< string >_ **file_name**: nombre del archivo de datos a procesar

(-GS) _< string >_ **file_path**: ruta relativa donde se encuentra el archivo de datos

(-GS) _< string >_ **full_path**: ruta completa del archivo de datos

(---) _< string >_ **file_encoding**: formato de codificacion del archivo

(---) _< File >_ **raw_file**:cursor del archivo de datos

(-GS) _< bool >_ **is_tabulated**:True si el archivo es tabulado

(-GS) _< bool >_ **headers_in_first_line**: True si la primera linea del archivo son los nombres de las columnas/clave en este caso el metodo set se de esta propiedad se llama _set_headers_in_data_

(-GS) _< bool >_ **use_custom_header**: True si se desea utilizar nombres de columnas/claves personalizados

(-GS) _< list[str] >_ **custom_header**: lista de nombres personalizados para las columnas/claves

(-GS) _< string >_ **data_separator**: caracter que sirve como separador del valor de cada uno de los campos

(---) _< bool >_ **ignore_errors**: True para ignorar el registro actual si tiene alguna inconsistencia y continuar con el siguiente False para detener la ejecucion del proceso (ignora todo el registro no solamente el campo inconsistente)

(---) _< bool >_ **apply_types**: por defecto todos los campos son leidos como tipo string, si se desea que se apliquen tipos de datos personalizados se debe colocar en True esta propiedad

(---) _< bool >_ **use_long_char**: True si los campos vienen separados por su cantidad de caracteres

(---) _< list[int] >_ **size_field**: lista de cantidad de caracteres que corresponden a cada campo

(---) _< bool >_ **affect_raw_record**: habilita la ejecucion de scripts que modifica al registro cuando aun es una linea de texto

(---) _< string >_ **scripts_path**: ruta relativa desde el directorio del proyecto en la cual se encuentran los scripts que se ejecutaran en cada registro

(---) _< list[str] >_ **scripts**: lista de scripts separados por SEPARATOR que se ejecutaran en cada registro, todos los scripts deben recibir un unico argumento de tipo string y retornar un string

(---) _< list[str] >_ **headers_type**: lista de los tipos de datos de cada columna/clave, se tiene encuenta el orden y que el archivo sea tabulado. los tipos de datos validos son int,str,float,bool. para futuras versiones se podria agregar mas tipos de datos como el date

(---) _< string >_ **field_template**: cadena que contiene el formato en que vienen almacenados los campos en cada registro de un archivo no tabulado el formarto es H (header,key) V (value)

(---) _< int >_ **clip_start**: numero de caracteres a ignorar desde el inicio de cada registro

(---) _< int >_ **clip_end**: numero de caracteres a ignorar desde el final de cada registro

(---) _< list[str] >_ **headers**: lista de nombres de columnas/claves

(-G-) _< list[dict] >_ **data_frame**: datos extraidos del archivo de datos, el metodo get de esta propiedad es llamado _get_data_

(---) _< list[int] >_ **data_errors_lines**: lista de numeros de lineas que contienen errores

(---) _< list[str] >_ **data_errors_messages**: lista de mensajes de error

NOTA: algunas propiedades deberian tener metodos get y set establecidos pero por cuestiones de tiempo no fueron implementadas (pero deberian)

###  Metodos
descripcion de metodos relevantes

get_data()
get_extension_file()

# Descripción de modulo api
Descripcion de la clase
### Propiedades
descripcion de las propiedades importantes
###  Metodos
descripcion de metodos relevantes

# Descripción de modulo database
Descripcion de la clase
### Propiedades
descripcion de las propiedades importantes
###  Metodos
descripcion de metodos relevantes

