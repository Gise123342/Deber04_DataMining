# Deber04_DataMining
Giselle Cevallos 00325549)

### Informacion Importante

La Carpeta Data Con archivos de los datos en formato parquet fue generada para la carga de datos dentro de el proyecto localmente. A causa de el peso y el limite de espacio para los repositorios en github. No se subieron estos archivos. Pero en el proyecto subido con el link de github se pueden encontrar facilmente:

<img width="409" height="298" alt="image" src="https://github.com/user-attachments/assets/b912ddc2-3cf6-4546-83c3-fd942b721722" />
<img width="653" height="639" alt="image" src="https://github.com/user-attachments/assets/9eb342b8-3a41-4ce8-9498-dc3a669ac25e" />


### Cómo levantar Compose, ingestar RAW, construir OBT

**Construir e iniciar todos los servicios**

docker-compose up -d

Esto levantará:
- postgres → Base de datos
- spark-notebook → Entorno Jupyter/Spark
- obt-builder → Script CLI para generar la OBT

Verifica que los tres contenedores estén activos con:

docker ps

<img width="1545" height="212" alt="image" src="https://github.com/user-attachments/assets/aedaad0a-1fde-449d-829e-006c28e51ccb" />

**Estructura**

<img width="461" height="667" alt="image" src="https://github.com/user-attachments/assets/efb04706-e6f6-4920-8f4b-afd729a1992a" />

**Ingestar datos RAW:**

En el notebook 01_ingesta_parquet_raw.ipynb:
- Ejecuta todos los bloques secuencialmente.
- Descargará los datasets (yellow, green, lookup).
- Cargará los archivos en PostgreSQL dentro del esquema raw.
- Verifica la tabla raw.ingestion_log.

**Construir la OBT (Base Operacional de Viajes)**

Opción A: Modo completo
- Reconstruye toda la tabla analytics.obt_trips desde cero.

docker-compose run obt-builder python build_obt.py --mode full

Opción B: Modo por partición
- Solo actualiza un año/mes específico (por ejemplo, enero 2019):

docker-compose run obt-builder python build_obt.py --mode by-partition --year 2019 --month 1

Se usa el codigo:

<img width="1182" height="709" alt="image" src="https://github.com/user-attachments/assets/69d00af0-c2a4-4018-992b-2019ca31a53c" />

### Variables de ambiente requeridas

Tenemos un env.exaple y un .env (Local)

En el env.example podemos observar el ejemplo estructural de las variables y el .env es el que se utilizo localmente para credenciales de acceso tanto en jupyter y en postgres

<img width="694" height="660" alt="image" src="https://github.com/user-attachments/assets/7a128886-2270-4646-a86e-e632bd3a336d" />

<img width="661" height="588" alt="image" src="https://github.com/user-attachments/assets/999af431-35ff-4ab2-b98c-5c6c5e2e472d" />

Clave de Jupyter : data123

<img width="927" height="397" alt="image" src="https://github.com/user-attachments/assets/76ec7eb8-0bbc-4b48-9965-e442b60a2b11" />

### Modo full y by-partition de build_obt.py. 

**Modo full**
<img width="941" height="902" alt="image" src="https://github.com/user-attachments/assets/8f2f01f8-6b86-4ae3-a97a-570e5165b595" />

- Elimina la tabla analytics.obt_trips si ya existe.
- Recrea toda la tabla desde cero uniendo los datasets yellow y green.
- Es ideal cuando quieres reconstruir el OBT completo desde las tablas raw.*.

**by-partition**
<img width="1171" height="916" alt="image" src="https://github.com/user-attachments/assets/3eb05cc1-06b4-41a1-8005-18577deb3c51" />

- Verifica que se hayan pasado --year y --month.
- Borra solo los registros de ese año/mes en analytics.obt_trips.
- Inserta nuevamente los datos correspondientes a ese año/mes desde raw.*.
- Esto es más rápido que recalcular toda la OBT.
