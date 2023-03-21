# Desafío Técnico Mercado Libre
---
# Descripción del desafío
La prueba esta dividida en dos partes una técnica y otra teórica:
### Parte técnica
Consiste en ejecutar un servicio web dentro de un docker container, el servicio debe:
- **Leer un archivo** en formato streameable (csv,txt,jsonlines) 
-- La forma de lectura de este archivo debe poder configurarse en el programa, sin que estos cambios afecten el código.
-- Tener en cuenta que este archivo puede ser mas grande que la memoria disponible.
_detalles: el archivo consta de 2 columnas (site,id)_

- Con los datos obtenidos de el archivo **consultar el API publica de mercado libre**
-- La consulta a la API se debe hacer de la manera mas rapida posible.
-- La consulta a la API debe ser eficiente en cuanto al consumo de recursos del sistema
-- Permitir que se puedan agregar nuevas consultas de APIs. 
_detalles: el código de los items es site + id, del api items obtener price y start_time, con el category_id obtener el nombre de la categoria (name), con el currency_id obtener description de la api currencies con seller_id obtener nickname de user_

- **Guardar en una base de datos** la respuesta de el API, los campos a guardar son:
-- **site** (obtenido del file)
-- **id** (obtenido del file)
-- **price** (obtenido de la api de ítems)
-- **start_time** (obtenido de la api de ítems)
-- **name** (obtenido de la api de categorías)
-- **description** (obtenido de la api de monedas)
-- **nickname** (obtenido de la api de users)
_detalles: La base de datos se debe levantar en un container, el motor puede ser no relacional, se puede utilizar una imagen existente._
- Brindar una forma de poder **acceder a esos datos**

**Parte Teórica.** consiste en sustentar una serie de preguntas, esta parte del desafío es resuelta en el archivo readme.md que sen encuentra en la carpeta _Desafio Teórico_ 

# Descripción general de la solución