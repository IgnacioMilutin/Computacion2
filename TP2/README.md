# TP2 - Sistema de Scraping y Análisis Web Distribuido

##### Ignacio Milutin - Computación 2
---
A continuacion se dara una explicacion de la como ejecutar el sistema y como funciona de cada una de sus partes.

## Guia de Ejecución
---

Para el funcionamiento del sistema se debe primero instalar las dependencias necesarias. Luego poner en marcha 2 ambos servidores. Una vez en marcha los servidores, ejecutar el cliente con los parametros correspondientes.

Instalar dependencias:

```
pip install -r requirements.txt
```

Ejecutar servidor de scrapping "A":
```
python server_scraping.py -h #ver argumentos posibles
```
```
python server_scraping.py -i localhost -p 8000 --processor-host localhost --processor-port 9001 
```

Ejecutar servidor de processing "B":
```
python server_processing.py -h #ver argumentos posibles
```
```
python server_processing.py -i localhost -p 9001
```

Ejecutar cliente:

```
python client.py -h #ver argumentos posibles
```
```
python client.py -s http://localhost:8000 -u <https://example.com> -o </directorio/nombre_archivo>
```

## Desarrollo y Funcionamiento
----
El proyecto esta dividido en 3: un servidor A de scrapping, un servirdor B de processing y los clientes. Cada uno tiene su propia tarea y funcionamiento.

#### Servidor de Scrapping "A":

El server de Scrapping es un servidor http asíncrono que utiliza aiohttp. Este recibe peticiones del cliente y ordena la tareas de scrapping web, tanto sus tareas como enviar las tareas al servidor de procesamiento. Para atender, recibir request y coordinar las tareas utiliza un event loop. Luego para ejecutar las tareas utliza un process pool y se comunica con el servidor de procesamientoi via TCP sockets. Cuando un cliente se comunica este envia un POST con al url a analizar. Este recibe esta petición, crea un tarea (task) y comienza el scrapping web sobre la url dada por el cliente. Luego obtiene los resultado de sus tareas y del servidor de procesamiento y le envia la respuesta al cliente. Mientras Este realiza sus tareas, el cliente puede enviar otras peticiones para consultar el estado de su tarea.

Este servidor tiene 3 Tareas, extrae informacion del html de la pagina, extrae metadatos de la pagina y se comunica con el servidor de procesamiento. 

- HTML_PARSER: Esta tarea anailiza el html y obtiene el titulo de la pagina, sus links, su estructura y la cantidad de imagenes que contiene. En cuanto a la estructura, este mira los header (h1,h2,h3,etc.) de la pagina y da la cantidad de cada uno.
- METADATA_EXTRACTOR: Esta tarea se encarga de analizar el html en busca de metadatos. Esta obtiene las descripciones y 'keywords' de esta y los Oen Graphs de difrrentes tipos.
- COMUNICACION CON SERVER_PROCESSING: La otra tarea que tiene este servidor es comunicarse con el servidor de procesamiento. Este se comuncia con un TCP socket y le envia la url que debe utilizar y sobre la que debe realizar sus tareas. Luego recibe la respuesta del servidor de procesamiento para agregarsela al resultado que se le entrega al cliente.

Ademas, este servidor tiene integrado un sistema de cache. este almacena durante 1 hora las respuestas de los clientes. De esta forma si se pide scrapper a un dominio que ya fue analizado antes (en un periodo de 1 hora), este no tiene que realizar toda la tarea de nuevo. tambien tiene integrado un sistema para limitar la cantidad de peticiones a un dominio y que esto cause un posible bloqueo al mismo. La cantidad de peticiones a un dominio se establece en 15, asi se contemplan los reintentos de la peticiones fallidas. 

#### Servidor de Processing "B":

El server de processing es un sevidor multiprocessing el cual escucha peticiones de server A, toma esas peticiones y ejecuta las tareas que le corresponde. Este utiliza socketserver para conectarse al cliente via socket, y  por cada conexion TCP crea un hilo, lo que le permite atender a varios clientes a la vez. Especificamente, cliente le envia url de la pagina a la cual se le realiza el analisis. Cada coneccion se mantiene durante 95 segundos, asi evitamos el bloqueo de un server por un cliente zombie y una conexión mal cerrada. Ademas este es una cantidad de tiempo considerable si este cliente esta en la cola para ejcutar las tareas. Vale la pena aclarar que en el caso de este server B, el cliente es el server A de scrapping.

Este realiza 3 tareas sobre esta url: toma un screenshot, procesa las imagenes de la pagina y realiza un analisis de rendimiento. Para estas tareas, se tiene un ProcessPool con 3 procesos por default. De esta forma se asigna un una tarea a cada proceso. Cada tarea se ejecuta con un timeout de 30 segundos. A continuacion deja una explicacion de como ejecuta cada una sus tareas:

- SCREENSHOT: La tarea de screenshot utiliza la biblioteca de 'Playwright' para tomar una captura de la pagina. Para esto, este realiza un GET de la pagina y le toma la captura en formato 'png'. Si este GET falla se reintenta un maximo de 3 veces. Se toma la captura con ciertos parametros fijos para adaptarlo en tamaño. Luego se verifica el tamaño de esta. Si la captura pesa mas de 5MB, esta se considera grande y se envia una version recortada al cliente. El screenshot enviado al cliente esta en base64. 
- PERFORMANCE: La tarea de analisis de rendimiento devuelve el tiempo de carga de la pagina, su tamaño en kb y la cantidad de request que realiza. Este primero realiza un GET de la apgina donde empiesa midiendo cuanto tarde esta petición. Si este GET falla se reintenta un maximo de 3 veces. Luego verifica si el html no excede el tamaño de 5MB. Luego este analiza los recursos del html(imagenes, css, fuentes, etc.) y busca su tamaño en el header con al etiquete de 'content_length'. Si el recurso no tiene esa etiquete realiza un GET de este para conocer su tamaño. Si es muy grande los obtiene en partes. Este analisis por partes tambien es hasata 5MB.

- IMAGES_PROCESSOR: El procesamiento de imagenes realiza un GET de la pagina y obtiene su html. Si esta peticion falla lo reintenta máximo 3 veces. Luego analiza el html en busca de imagenes, se busca las url de estas y las envia a procesar. El procesamiento de imagenes convierte las imagenes en thumbnails. A estas se les coloca un tamaño y una calidad fija. Ademas, realiza un cambio de RGBA a RGB, que le agrega fondo a las imagenes sin fondo para que puedan se procesadas correctamente. Estas se guardan en JPG, luego se convierten a base64 y se envian.

Una vez se obtienen los resultados de estos 3 procesos, se envian en conjunto al cliente y se cierra la conexión. 


#### Cliente:

El cliente interactua con el servidor de scrapping 'A'. Se comunica mediante peticione HTTP. Este le envia la url de la página la cual se quiere scrappear y espera a que el servidor le devuelva la informacion scrappeada de la página. Al ejecutarse, mediante el parámetro '-o' o '-output' se puede dar el directorio y nombre a donde se quiere descargar el archivo json con los resultados. 

Mientras espera, realiza una verificación del estado la tarea cad 2 segundos. Una vez la tarea se completa y el servidor le responde con el resultado, se imprime un resumen de estos resultados. En caso de no haberse especificado un output para descargar los resultados, se le pregunta al cliente si quiere descargarlos.