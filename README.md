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
Nota: _configurar el modulo data a traves del archivo .env.data_

Este modulo se encarga de leer el archivo base y de generar un diccionario de datos para la consulta a la api.

Flujo de ejecución:
- apertura y lectura de archivo de configuracion
  - en caso de no ser posible finaliza la ejecucion del proceso 
- inicializacion de variables
- apertura de archivo de datos
  - en caso de no ser posible finaliza la ejecucion del proceso
- definir si el archivo es tabulado (formato CSV y parecidos) o no (formato JSONLINES y parecidos)
    - tabulado:
      - se resuelven las cabeceras (nombres de las columnas, claves del diccionario)
      - lectura de registro como cadena de texto
      - aplicar scripts sobre el registro (si esta activado)
      - convierto el registro en una lista de strings
      - comprobar si el numero de strings del registro es igual al numero de cabeceras
        - en caso de ser diferente se reporta el error, se ignora el registro y se continua con el siguiente
      - aplicar la conversion de tipos de datos a los valores (si esta activado)
      - convertir el registro en un diccionario juntando las cabeceras con los valores
      - agrego el registro a la lista data (lista de diccionarios procesados)
    - no tabulado:
      - convertir la plantilla HV (explicado en la carga del archivo de configuracion) en una expresion regular
      - lectura de registro como cadena de texto
      - recortar caracteres de inicio y fin del registro (indicado en el archivo de configuracion)
      - eliminar las comillas dobles del registro (facilita la extraccion de los valores)
      - aplicar scripts sobre el registro (si esta activado)
      - aplicar la expresion regular sobre el registro y convertir el resultado en una diccionario
      - agregar el registro a la lista data (lista de diccionarios procesados)
- cierra el archivo de datos

Detalle de ejecución:
- **carga archivo de configuracion**: carga el archivo de configuracion .env.data en caso de no encontrarse detiene la ejecución del proceso, este archivo esta ubicado en la raiz del proyecto y contiene las propiedades necesarias para la ejecución del modulo data estas propiedades son:
  - **SEPARATOR**: _(character)_ caracter separador para las listas DENTRO de este mismo documento (.env.data) no confundir con DATA_SEPARATOR
  - **FILE_PATH**: _(string)_ ruta relativa donde se encuentra el archivo de datos a partir de app.py
  - **FILE_NAME**: _(string)_ nombre del archivo de datos a procesar
  - **FILE_ENCODING**: _(string)_ tipo de codificacion del archivo de datos
  - **DATA_SEPARATOR**: _(character or tag)_ caracter que sirve como separador del valor de cada uno de los campos, utilizar las palabras TAB, SPACE para indicar que el separador es un tabulador o espacio en blanco respectivamente
  - **FILE_TABULATED**: _(boolean)_ **True** si el archivo conserva el mismo orden de datos en cada registro ejemplo un CSV y el numero de datos por registro coincide con el numero de columnas 
  - **AFFECT_RAW_RECORD**: _(boolean)_ habilita la ejecucion de scripts que modifica al registro cuando aun es una linea de texto
  - **SCRIPTS_PATH**: _(string)_ ruta relativa desde el directorio del proyecto en la cual se encuentran los scripts que se ejecutaran en cada registro
  - **SCRIPTS**: _(string,string,...)_ lista de scripts separados por SEPARATOR que se ejecutaran en cada registro, todos los scripts deben recibir un unico argumento de tipo string y retornar un string
  - **HEADERS_IN_FIRST_LINE**:_(boolean)_ **True** si el archivo contiene en su primera linea los nombres de los campos/claves del diccionario que se generara
  - **USE_CUSTOM_HEADER**: _(boolean)_ **True** si se desea utilizar nombres de columnas/claves personalizados 
  - **CUSTOM_HEADER**: _(string,string,...)_ lista de nombres personalizados para las columnas/claves separados por SEPARATOR se tiene encuenta el orden y que el archivo sea tabulado  
  - **APPLY_TYPES**: por defecto todos los campos son leidos como tipo string, si se desea que se apliquen tipos de datos personalizados se debe colocar en **True** esta propiedad
  - **HEADERS_TYPE**: _(tag,tag,...)_ lista de tipos de datos separados por SEPARATOR, se tiene encuenta el orden y que el archivo sea tabulado. los tipos de datos validos son int,str,float,bool. para futuras versiones se podria agregar mas tipos de datos como el date
  - **USE_LONG_CHAR_SEPARATOR**: _(boolean)_ **True** si los campos vienen separados por su cantidad de caracteres, ejemplo:
    ```
    emilton1983colM
    eduardo1986argM
    carlos 1000ecuM
    ana    2000venF
    ```
    en el ejemplo anterior cada registros tiene 4 campos, el primer campo (nombre) tiene reservado siempre 7 caracteres, el segundo campo (año) tiene reservado siempre 4 caracteres, el codigo del pais 3 y el sexo 1. el dato del campo no debe sobre pasar la cantidad de caracteres reservados para no generar inconsistencias y si no utiliza la totalidad de caracteres reservados se debe completar con espacios en blanco
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

- **aplicar scripts sobre el registro**: Ejecuta los ficheros.py que se encuentran en la lista **SCRIPTS** del archivo de configuracion enviando el registro actual (en este punto es un string) como unico argumento. Los scripts deben estar en el directorio indicado en la propiedad **SCRIPTS_PATH** del archivo de configuracion, deben tener una unica funcion que recibe un string y retornar un string, el nombre del fichero del script debe ser igual al de esta funcion, los scripts son ejecutados de forma secuencial en el orden en que se encuentran en la lista **SCRIPTS** del archivo de configuracion, esto quiere decir que las modificaciones que realice un script sobre el registro actual se tendran en cuenta para el siguiente script.

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
descripcion de metodos relevantes.

**process_file()**: inicia el proceso de obtencion de datos, los cuales se pueden obtener a traves de get_data()

**get_data() -> list[dict]**: retorna una lista de diccionarios con los datos extraidos del archivo de datos

**show_errors()**: muestra en pantalla los errores que se generaron durante la carga de los datos

**get_extension_file() -> str**: devuelve la extension del archivo de datos


# Descripción de modulo api
Nota: _configurar el modulo data a traves del archivo .env.api_

Este modulo se encarga tomar la lista de registros generados por el modulo Data y a partir de estos generar las url que consultaran el API el resultado de esas consultas (lista de diccionarios) sera obtenido a traves del metodo get_data

Flujo de ejecución:
- apertura y lectura de archivo de configuracion
  - en caso de no ser posible finaliza la ejecucion del proceso 
- inicializacion de variables
- paso de registros generados por el modulo Data (metodo set_api_data(registros))
- procesar el archivo donde se encuentran las instrucciones de consulta(fetch_url_file())
  - en caso de no encontrar el archivo de instrucciones a procesar termina el proceso
  - formatea las instrucciones convirtiendola en url de consulta a la API
  - ejecuta la peticion a la API con la url generada
  - agrega el resultado como una {clave:valor} mas al registro usado para consultar el API
    - en caso de fallar la consulta (error 404) agrega un resultado {"processing_error":True} para no seguir usando ese registro en las siguientes consultas a las API
- agregar el registro resultante de la peticion a la lista de registros de la api
- cierre de archivo de instrucciones

Detalle de ejecución:
- **carga archivo de configuracion**: carga el archivo de configuracion .env.api en caso de no encontrarse detiene la ejecución del proceso, este archivo esta ubicado en la raiz del proyecto y contiene las propiedades necesarias para la ejecución del modulo api estas propiedades son:
  - **PATH_TO_APIS**:(string) ruta relativa donde se encuentra el archivo de datos a partir de app.py
  - **URL_BASE**:(string) direccion url mediante el cual se accede al API ejemplo https://api.mercadolibre.com/
  - **FILE_API**: (string) nombre de el archivo donde se encuentran las instrucciones para generar las urls de consultas a las APIs, cada instruccion debe estar en una linea diferente el formato de instruccion es el siguiente:
  
    **texto_1<clave_1>texto_n<clave_n>->name_prop_1,name_prop_n**

    donde texto_1 y texto_n son strings "estaticos" que ayudan a construir la url
    
    **<clave_1>** y **<clave_n>** son nombres validos de las claves del diccionario de consulta encerrados entre llaves angulares, puesto que las consultas se hacen en forma secuencial y los resultados se guardan en el mismo diccionario se pueden usar claves generadas de consultas anteriores

    **name_prop_1** y **name_prop_n** son los nombres de las propiedades obtenidas de la consulta que quiero almacenar, estas propiedades deben ir despues de la secuencia de caracteres -> y separadas por comas sin espacios

    ejemplo:
    tomando como referencia el API publica de mercado libre, para obtener el nombre de la categoria de un producto la instruccion seria:

    categories/<category_id>->name

    - donde _categories/_ es un texto_n "estatico" que ayuda a formar la url
  
    - _<category_id>_ es una clave valida del diccionario donde estan guardados los datos que se quieren consultar en el api o es una clave valida generada por alguna peticion a la API ejecutada anteriormente
  
    - _->_ es el indicador de que el texto siguiente es la lista de propiedades que quiero extraer de la consulta a la API
  
    - _name_ es el nombre de la propiedad que quiero extraer puedoagregar mas propiedades separandolas por , sin espacios despues de esta

    otro ejemplo valido de instruccion utilizando el API de mercado libre seria:
    
    items?ids=<Key>&attributes=price,start_time,category_id,currency_id,seller_id->price,start_time,category_id,currency_id,seller_id

    donde _items?ids=_ es texto complementario
    
    _<Key>_ es la clave del producto

    _&attributes=price,start_time,category_id,currency_id,seller_id_ mas texto complementario

    _->_ indicador de que el texto que sigue son las propiedades que quiero almacenar
    
    _price,start_time,category_id,currency_id,seller_id_ lista de propiedades a almacenar separadas por ,

    no hay limite para agregar claves ni para agregar propiedades siempre que sean validas



### Propiedades de la clase API
(-GS) _< string >_ **file_name**: nombre de el archivo de datos a procesar

(---) _< string >_ **url_base**: url base para consulta a la API 

(---) _< string >_ **path**: ruta donde se encuentra el archivo de instrucciones de la API

(---) _< string >_ **file_name**: nombre del archivo de instrucciones 

(---) _< string >_ **full_path**: ruta + nombre del arhivo de instrucciones

(---) _< File >_ **list_file**: apuntador del archivo

(---) _< list[dict] >_ **dict_data**: lista de datos que se van a procesar

(-G-) _< list[dict] >_ **api_data**: diccionario de datos utilizado para las peticiones + los datos obtenidos por las consultas de la API. el metodo get de esta propiedad es llamado get_data()

(---) _< list[int] >_ **data_errors_lines**: lista de numeros de lineas que contienen errores

(---) _< list[str] >_ **data_errors_messages**: lista de mensajes de error

NOTA: algunas propiedades deberian tener metodos get y set establecidos pero por cuestiones de tiempo no fueron implementadas (pero deberian)

###  Metodos
descripcion de metodos relevantes.

**set_api_data(list[dict])**: pasa a la clase API los datos que se usaran para las consultas

**fetch_url_file()**: se encarga de ejecutar todos los procesos necesarios para la obtencion de los datos de la API desde la lectura del archivo de instrucciones hasta la obtencion de los datos

**get_data()**: retorna una lista de registros procesados que es la lista registro ingresados (con el metodo set_api_data) cada registro actualizados con los campos traidos de la consulta de la API. ejemplo: 

la lista de diccionarios pasada por medio de set_api_data() es:
``` 
[{"site":"MLA","id":828617220,"Key":"MLA412445"},{"site":"MLB","id":456,"Key":"MLA456"}]
```
la instruccion de consulta a la API es _categories/<Key>->name_

la url de consulta generada para el primer registro es https://api.mercadolibre.com/categories/MLA412445

y de esa consulta tomara la propiedad name

una vez ejecutada la consulta el primer registro quedaria de la forma:
``` 
[{"site":"MLA","id":828617220,"Key":"MLA412445","name":"Libros Físicos"},{"site":"MLB","id":456,"Key":"MLA456"}]
```

# Descripción de modulo database
Nota: _configurar el modulo data a traves del archivo .env.database_

Este modulo se encarga tomar la lista de registros generados por el modulo API y almacenarlos o consultarlos dado el caso.

Flujo de ejecución:
- apertura y lectura de archivo de configuracion
  - en caso de no ser posible finaliza la ejecucion del proceso 
- inicializacion de variables
- conexion con la base de datos
- guardar registros de la consulta de la API
- consultar registros de la consulta de la API
### Propiedades
(---) _< string >_ **mongo_uri**: string de conexion a la base de datos

(---) _< mongoClient >_ **mongo_client**: cliente cursor a la base de datos de mongoDB

(---) _< string >_ **mongo_db**: nombre de la base de datos con la cual se conectara

(---) _< string >_ **mongo_collection**: nombre de la coleccion de mongoDB

(---) _< list[int] >_ **data_errors_lines**: lista de indice de registro que contienen errores

(---) _< list[str] >_ **data_errors_messages**: lista de mensajes de error

###  Metodos
descripcion de metodos relevantes.

**insert_many(list[dict])**: inserta en la base de datos la lista de diccionarios pasada como argumentos

**paginate(n:int,x:int)** muestra los registros de la pagina n donde las paginas tienen x cantidad de elementos 

**count()** devuelve la cantidad de registros almacenados en la base de datos

# Futuras implementaciones

###  General
- terminar la implementacion de los metodos get y set  de las propiedades que lo necesitan en todos los modulos
- aplicar concurrencia en los procesos donde sea posible
- implementar el registro de errores en un archivo de texto que funcione como log
- correcciones ortograficas de el archivo readme.md
###  Modulo data
- agregar un metodo data_info que retorne la cantidad de registros procesados, la cantidad de registros ignorados
  
- agregar una propiedad en el archivo de configuracion llamada IGNORE_N_LINES que serviria para saltar los n primeros renglones del archivo de datos, esto para facilitar ignorar informacion de metadatos o comentarios que se encuentran generalmente en el inicio de los archivos

- agregar un metodo fill_with junto a una variable de entorno tipo cabecera:valor_a_cambiar:nuevo_valor,cabecera:valor_a_cambiar:nuevo_valor... que en caso de encontrar cierto valor (puede ser null 0 o cualquier otro) reemplace ese valor por otro actualmente esos registros son ignorados por no poseer informacion suficiente

###  Modulo api
- agregar un metodo que permita cambiar el nombre de las claves de los registros en lo posible durante la ejecucion de las consultaspara evitar nombres de claves duplicada que generen errores o inconsistencias

###  Modulo database
- separar la conexion del init de la clase para poder reintentar conexiones en caso de de errores