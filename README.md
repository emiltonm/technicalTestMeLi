# Desafío Técnico Mercado Libre
# Descripción del desafío
La prueba esta dividida en dos partes una técnica y otra teórica:
### Parte técnica
Consiste en ejecutar un servicio web dentro de un docker container, el servicio debe:
- **Leer un archivo** en formato streameable (csv,txt,jsonlines)
-- La forma de lectura de este archivo debe poder configurarse en el programa, sin que estos cambios afecten el código.
-- Tener en cuenta que este archivo puede ser mas grande que la memoria disponible.
- Con los datos obtenidos de el archivo **consultar el API publica de mercado libre**
-- La consulta a la API se debe hacer de la manera mas rapida posible.
-- La consulta a la API debe ser eficiente en cuanto al consumo de recursos del sistema
-- Permitir que se puedan agregar nuevas consultas de APIs.
- **Guardar en una base de datos** la respuesta de el API 
- Brindar una forma de poder **acceder a esos datos**

**Parte Teórica.** consiste en sustentar una serie de preguntas, esta parte del desafío es resuelta en el archivo readme.md que sen encuentra en la carpeta _Desafio Teórico_