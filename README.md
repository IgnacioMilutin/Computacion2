COMPUTACION 2 - Ingenieria en Informática - Universidad de Mendoza

Ignacio Milutin       DNI: 45529564


# TP1 - Analisis Biométrico

## Descripcion

El sistema de analisis biometrico genera 60 muestras, una por segundo, realiza calculo de media y desviación estandar da cada dato y lugo analiza si se encuntra dentro de un rango, depende del tipo de dato, a cumplir. Luego cada muestra se coloca en una cadena de bloques, de la cual se puede verificar su integridad. Luego tiene la opcion de dar un reporte acerca de estas muestras. El codigo tiene un main, donde estan las definiciones de cada proceso. Cada función del programa tiene un proceso diferente.

### Generador

El procesos generador se encarga de generar las muestras aleatoreamente. Estas muestras tienen 3 tipos de dato: Frecuencia, oxigeno y presion. Luego de generar la muestra, la coloca en 3 pipes diferentes que se encargaran de enviar la muestra a los diferentes procesos analizadores. Luego de generar y enviar las 60 muestras envia una muestra 'fin' a cada pipe y finalmente cierra su extremo de cada pipe.

### Analizadores

Hay 3 procesos analizadores, uno para cada tipo de dato. Cada proceso recibe la muestra por un pipe diferente. La función de los procesos analizadores es calcular la media y desviacion estandar del dato que le corresponde tomando en cuenta las ultimas 30 muestras recibidas. Luego de obtener la media y desviación estandar forma un diccionario con esos datos y los coloca en una queue por la cual el verificador recibira los diccionarios. Cada vez que un analizador coloca un diccionario en la queue, realiza un adquire del semaforo, por lo tanto hasta que el verificador no realiza un release los analizadores no envia otro dato. Finalmente cuando no tienen mas datos que enviar envian un fin cada uno.

### Verificador

El proceso verificador recibe los datos de la queue y junta los 3 diccionarios (uno para cada tipo de dato) que corresponden a la misma muestra y los junta en un mismo bloque.  Antes de juntarlos en un mismo bloque realiza un analisis para ver si cada dato esta dentro de un rango permitido. Si uno de los datos no lo esta se coloca una alerta en el bloque. Luego coloca el hash del bloque anterior en este y calcula el hash de este bloque utilizando SHA256 y se añade a la cadena de bloques a un archivo llamado `blockchain.json`. Finalmente muestra en pantalla el indice del bloque que se proceso,su hash y si tiene alerta o no. Para terminar realiza un semaforo release para que los analizadores le envien los siguientes diccionarios.

### Verificador de la Cadena de Bloques

Al terminar de armar la cadena de bloques se preguntara por la opcion de verificar la integridad de esta. En caso de que algun bloque rompa con la integridad se indicar cual la rompe.

### Reporte

Luego se preguntara si se quiere un reporte el cual contiene: 
- Cantidad de bloques
- Cantidad de bloques con alerta
- Los promedios de los datos en base a las 60 muestras.

Se creara un archivo `reporte.txt` donde se encontrara esta información

## Instruccion de Ejecución}

Para ejecutar este programa se debera primeron realizar una instalacion de las extenciones utilizadas las cuales estan en `requirements.txt` y luego ejecutar el archivo `main.py`

Instalar extenciones:

```
pip install -r requirements.txt

```

ejecutar archivo main:

```
pyton3 main.py
```

