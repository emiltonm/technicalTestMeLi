# Desafio teorico

## Procesos, hilos y corrutinas

### Un caso en el que usarías procesos para resolver un problema y por qué.
- Es aconsejable utilizar procesos en los casos en que la aplicación necesita realizar tareas que no necesariamente deben ser concurrentes, pero si independientes entre si.
### Un caso en el que usarías threads para resolver un problema y por qué.
- Es aconsejable utilizar threads en los casos en que la aplicación necesita realizar tareas simultáneas y/o concurrentes. como puedan ser el procesamiento de datos, estos pueden ser divididos en partes y ejecutados en paralelo; comunicaciones en red para poder enviar y recibir datos de manera simultanea
### Un caso en el que usarías corrutinas para resolver un problema y por qué.
- Las corrutinas pueden ser útiles para gestionar la espera de las operaciones de E/S sin bloquear el hilo principal de la aplicación. En lugar de bloquear el hilo principal de la aplicación, se puede utilizar una corrutina para llevar a cabo la tarea de E/S mientras que el hilo principal de la aplicación se dedica a otras tareas. un caso sria cuando una aplicación necesita realizar tareas de larga duración, como el procesamiento de grandes conjuntos de datos.

## Si tuvieras 1.000.000 de elementos y tuvieras que consultar para cada uno de ellos información en una API HTTP. ¿Cómo lo harías? Explicar.
- examinar el API para saber si soporta peticiones por lotes (multiget)
- eliminaria la informacion redundante (registros repetidos) en la data de entrada, para evitar que se realicen consultas innecesarias.
- dividiria la informacion en bloques dependiendo de las limitaciones de la API y de los recursos disponibles en mi aplicación
- revisar el archivo de cache persistente para ver si hay elementos que ya se han consultado previamente
- enviar las solicitudes al API
- guardar la respuesta de la API en un archivo de cache persistente para aquellos elementos comunes a las solicitudes por ejemplo, categorias de un producto, tipo de usuario, etc.
- procesar la respuesta de la API para obtener la información requerida ejemplo guardar en una base de datos
- reintentar las solicitudes fallidas

# Análisis de complejidad

## Dados 4 algoritmos A, B, C y D que cumplen la misma funcionalidad, con complejidades O(n^2), O(n^3), O(2^n) y O(n log n), respectivamente, ¿Cuál de los algoritmos favorecerías y cuál descartarías en principio? Explicar por qué.

- En general, en la mayoría de los casos, el algoritmo D, con una complejidad de O(n log n), sería la mejor opción para procesar grandes cantidades de datos. Sin embargo, si se sabe que el número de elementos procesados será pequeño, el algoritmo A podría ser suficiente y más eficiente que el algoritmo D. Los algoritmos B y C, con complejidades O(n^3) y O(2^n), respectivamente, serían descartados en principio ya que son mucho menos eficientes que los otros dos.


## Asume que dispones de dos bases de datos para utilizar en diferentes problemas a resolver. La primera llamada AlfaDB tiene una complejidad de O(1) en consulta y O(n^2) en escritura. La segunda llamada BetaDB que tiene una complejidad de O(log n) tanto para consulta, como para escritura. ¿Describe en forma sucinta, qué casos de uso podrías atacar con cada una?

- AlfaDB es más adecuada para casos de uso en los que se realizan muchas consultas pero pocas escrituras, mientras que BetaDB es más adecuada para casos de uso en los que se realizan tanto consultas como escrituras con frecuencia.
