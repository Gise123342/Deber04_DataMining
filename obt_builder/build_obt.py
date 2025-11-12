
import os
import time
import argparse
import psycopg2
from datetime import datetime

# --- Leer variables de entorno ---
pg_host = os.getenv("PG_HOST")
pg_db = os.getenv("PG_DB")
pg_user = os.getenv("PG_USER")
pg_password = os.getenv("PG_PASSWORD")

# --- CLI Arguments ---
parser = argparse.ArgumentParser(description="Construye o actualiza la tabla analytics.obt_trips")
parser.add_argument("--mode", choices=["full", "by-partition"], default="full", help="Modo de ejecución")
parser.add_argument("--year", type=int, help="Año a procesar (solo para modo by-partition)")
parser.add_argument("--month", type=int, help="Mes a procesar (solo para modo by-partition)")
args = parser.parse_args()

print(f"🔹 Iniciando obt-builder en modo '{args.mode}'...")
print(f"🔹 Conectando a Postgres {pg_host}:{pg_db} con usuario {pg_user}")

# --- Conexión a la base ---
conn = psycopg2.connect(
    host=pg_host, database=pg_db, user=pg_user, password=pg_password
)
cur = conn.cursor()

# --- Crear esquema destino ---
cur.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
conn.commit()

start_time = time.time()

if args.mode == "full":
    print("Ejecutando carga completa del OBT...")
    cur.execute("DROP TABLE IF EXISTS analytics.obt_trips;")
    cur.execute("""
        CREATE TABLE analytics.obt_trips AS
        SELECT
            'yellow' AS service_type,
            "VendorID",
            tpep_pickup_datetime AS pickup_datetime,
            tpep_dropoff_datetime AS dropoff_datetime,
            passenger_count,
            trip_distance,
            "PULocationID",
            "DOLocationID",
            payment_type,
            fare_amount,
            total_amount
        FROM raw.yellow_taxi_trip
        UNION ALL
        SELECT
            'green' AS service_type,
            "VendorID",
            lpep_pickup_datetime AS pickup_datetime,
            lpep_dropoff_datetime AS dropoff_datetime,
            passenger_count,
            trip_distance,
            "PULocationID",
            "DOLocationID",
            payment_type,
            fare_amount,
            total_amount
        FROM raw.green_taxi_trip;
    """)
    conn.commit()
    print("Carga completa finalizada.")

elif args.mode == "by-partition":
    if not args.year or not args.month:
        raise ValueError("Debe especificar --year y --month para modo by-partition")
    print(f"Actualizando partición {args.year}-{args.month:02d}...")
    cur.execute(f"""
        DELETE FROM analytics.obt_trips
        WHERE EXTRACT(YEAR FROM pickup_datetime) = {args.year}
          AND EXTRACT(MONTH FROM pickup_datetime) = {args.month};
        INSERT INTO analytics.obt_trips
        SELECT
            'yellow' AS service_type, "VendorID", tpep_pickup_datetime, tpep_dropoff_datetime,
            passenger_count, trip_distance, "PULocationID", "DOLocationID",
            payment_type, fare_amount, total_amount
        FROM raw.yellow_taxi_trip
        WHERE EXTRACT(YEAR FROM tpep_pickup_datetime) = {args.year}
          AND EXTRACT(MONTH FROM tpep_pickup_datetime) = {args.month}
        UNION ALL
        SELECT
            'green' AS service_type, "VendorID", lpep_pickup_datetime, lpep_dropoff_datetime,
            passenger_count, trip_distance, "PULocationID", "DOLocationID",
            payment_type, fare_amount, total_amount
        FROM raw.green_taxi_trip
        WHERE EXTRACT(YEAR FROM lpep_pickup_datetime) = {args.year}
          AND EXTRACT(MONTH FROM lpep_pickup_datetime) = {args.month};
    """)
    conn.commit()
    print(f"Partición {args.year}-{args.month:02d} actualizada.")

# --- Métricas ---
elapsed = time.time() - start_time
cur.execute("SELECT COUNT(*) FROM analytics.obt_trips;")
total_rows = cur.fetchone()[0]

print(f"Total filas en analytics.obt_trips: {total_rows:,}")
print(f"Tiempo total de ejecución: {elapsed:.2f} segundos.")

cur.close()
conn.close()
print("Proceso OBT finalizado correctamente.")
