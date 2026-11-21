import csv
from contextlib import closing
from getpass import getpass
from pathlib import Path

import psycopg2
from psycopg2 import sql


# =========================================================
# CONFIGURACIÓN
# =========================================================
ARCHIVO = Path(r"C:\Users\user\Documents\Inteligencia de negocios\Proyecto_IN\Proy_Analysis_Airbnb_Business_Model\data\raw\listings.csv")
#ARCHIVO = Path(r"C:\Users\user\Documents\Inteligencia de negocios\Proyecto_IN\Proy_Analysis_Airbnb_Business_Model\data\raw\neighbourhoods.csv")


HOST = "localhost"
PORT = 5432
DATABASE = "proy_airbnb_rio"
USER = "postgres"
ESQUEMA = "staging"
TABLA = "listings"


def importar_csv():
    # 1. Comprobar que exista el archivo.
    if not ARCHIVO.is_file():
        raise FileNotFoundError(
            f"No se encontró el archivo:\n{ARCHIVO}\n"
            "Corrige la ruta en la variable ARCHIVO."
        )

    # 2. Leer y validar los encabezados.
    with ARCHIVO.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as entrada:
        columnas = next(csv.reader(entrada), None)

    if not columnas:
        raise ValueError("El archivo está vacío o no tiene encabezados.")

    if any(not columna.strip() for columna in columnas):
        raise ValueError("Existen columnas con nombres vacíos.")

    if len(columnas) != len(set(columnas)):
        raise ValueError("Existen nombres de columnas repetidos.")

    # PostgreSQL limita normalmente los identificadores a 63 bytes.
    if any(len(columna.encode("utf-8")) > 63 for columna in columnas):
        raise ValueError(
            "Hay encabezados que superan los 63 bytes. "
            "Deben ajustarse antes de crear la tabla."
        )

    print(f"Archivo: {ARCHIVO}")
    print(f"Columnas detectadas: {len(columnas)}")
    print(f"Base de datos: {DATABASE}")
    print(f"Tabla de destino: {ESQUEMA}.{TABLA}")

    password = getpass(f"Contraseña del usuario {USER}: ")

    # closing garantiza el cierre de la conexión.
    with closing(
        psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            user=USER,
            password=password,
            connect_timeout=10,
            application_name="importacion_airbnb_rio",
        )
    ) as conexion:
        conexion.set_client_encoding("UTF8")

        # Confirma los cambios si todo termina correctamente.
        # Si ocurre un error, revierte esta transacción.
        with conexion:
            with conexion.cursor() as cursor:
                # 3. Crear el esquema.
                cursor.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        sql.Identifier(ESQUEMA)
                    )
                )

                # 4. Evitar sobrescrituras y cargas duplicadas.
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = %s
                          AND table_name = %s
                    )
                    """,
                    (ESQUEMA, TABLA),
                )

                if cursor.fetchone()[0]:
                    raise RuntimeError(
                        f"La tabla {ESQUEMA}.{TABLA} ya existe. "
                        "Revisa su contenido en pgAdmin. "
                        "El script no borrará ni duplicará sus datos."
                    )

                # 5. Crear las columnas como TEXT para conservar
                # los valores originales antes de la limpieza.
                definiciones = sql.SQL(", ").join(
                    sql.SQL("{} TEXT").format(
                        sql.Identifier(columna)
                    )
                    for columna in columnas
                )

                cursor.execute(
                    sql.SQL("CREATE TABLE {}.{} ({})").format(
                        sql.Identifier(ESQUEMA),
                        sql.Identifier(TABLA),
                        definiciones,
                    )
                )

                print("Tabla creada. Importando registros...")

                # 6. Importar el CSV mediante COPY.
                consulta_copy = sql.SQL(
                    """
                    COPY {}.{}
                    FROM STDIN
                    WITH (
                        FORMAT CSV,
                        HEADER TRUE,
                        DELIMITER ',',
                        ENCODING 'UTF8'
                    )
                    """
                ).format(
                    sql.Identifier(ESQUEMA),
                    sql.Identifier(TABLA),
                )

                with ARCHIVO.open(
                    "r",
                    encoding="utf-8-sig",
                    newline="",
                ) as entrada:
                    cursor.copy_expert(
                        consulta_copy.as_string(conexion),
                        entrada,
                    )

                # 7. Contar los registros cargados.
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                        sql.Identifier(ESQUEMA),
                        sql.Identifier(TABLA),
                    )
                )
                total = cursor.fetchone()[0]

        # Este mensaje aparece después de confirmar la transacción.
        print(f"\nImportación completada: {total:,} registros.")
        print(f"Destino: {DATABASE} → {ESQUEMA}.{TABLA}")


if __name__ == "__main__":
    try:
        importar_csv()

    except psycopg2.Error as error:
        print("\nError de PostgreSQL:")
        print(error)

    except (OSError, ValueError, RuntimeError, csv.Error) as error:
        print("\nNo se completó la importación:")
        print(error)