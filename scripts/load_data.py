import csv
import os
from contextlib import contextmanager
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Generator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "data" / "cleaned" / "cleaned_tvet_data.csv"
REPORTING_PERIOD = date(2021, 1, 1)
REGION_COLUMNS = {"region"}
PROVINCE_COLUMNS = {
    "province",
    "assessed_female",
    "assessed_male",
    "assessed_total",
    "certified_female",
    "certified_male",
    "certified_total",
    "certification_rate",
}


def load_connection_string() -> str:
    for env_file in (PROJECT_ROOT / ".env", PROJECT_ROOT / ".env.local"):
        if not env_file.is_file():
            continue
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            key, separator, value = line.partition("=")
            if not separator:
                continue
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            os.environ.setdefault(key, value)

    connection_string = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_UNPOOLED")
    if not connection_string:
        raise RuntimeError(
            "Set DATABASE_URL or DATABASE_URL_UNPOOLED in the environment, .env, or .env.local."
        )
    return connection_string


def read_records() -> list[dict[str, Any]]:
    with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = set(reader.fieldnames or ())
        missing_columns = (REGION_COLUMNS | PROVINCE_COLUMNS) - headers
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing_columns))}")

        records = []
        for line_number, row in enumerate(reader, start=2):
            region_name = (row["region"] or "").strip()
            province_name = (row["province"] or "").strip()
            if not region_name or not province_name:
                raise ValueError(f"CSV row {line_number} has an empty region or province.")

            records.append(
                {
                    "region_name": region_name,
                    "province_name": province_name,
                    "reporting_period": REPORTING_PERIOD,
                    "assessed_female": int(row["assessed_female"]),
                    "assessed_male": int(row["assessed_male"]),
                    "assessed_total": int(row["assessed_total"]),
                    "certified_female": int(row["certified_female"]),
                    "certified_male": int(row["certified_male"]),
                    "certified_total": int(row["certified_total"]),
                    "certification_rate": Decimal(row["certification_rate"]),
                }
            )
    return records


def get_postgres_connect() -> Any:
    try:
        import psycopg

        return psycopg.connect
    except ImportError as error:
        raise RuntimeError(
            "A PostgreSQL driver is required. Install psycopg[binary] to run this loader."
        ) from error


@contextmanager
def managed_transaction(connect: Any, connection_string: str) -> Generator[Any, None, None]:
    connection = connect(connection_string)
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def load_records(records: list[dict[str, Any]], connection_string: str) -> None:
    if not records:
        print("CSV contains no province records; nothing to load.")
        return

    region_names = list(dict.fromkeys(record["region_name"] for record in records))
    connect = get_postgres_connect()

    with managed_transaction(connect, connection_string) as connection:
        with connection.cursor() as cursor:
            for region_name in region_names:
                cursor.execute(
                    "SELECT region_id FROM regions WHERE region_name = %s ORDER BY region_id",
                    (region_name,),
                )
                existing_ids = [row[0] for row in cursor.fetchall()]
                if len(existing_ids) > 1:
                    raise ValueError(
                        f"Multiple records exist for region {region_name!r}; "
                        "resolve them before loading."
                    )
                if not existing_ids:
                    cursor.execute(
                        "INSERT INTO regions (region_name) VALUES (%s)",
                        (region_name,),
                    )

            cursor.execute(
                "SELECT region_id, region_name FROM regions WHERE region_name = ANY(%s)",
                (region_names,),
            )
            region_ids = {region_name: region_id for region_id, region_name in cursor.fetchall()}
            missing_regions = set(region_names) - region_ids.keys()
            if missing_regions:
                raise RuntimeError(
                    f"Could not retrieve IDs for regions: {', '.join(sorted(missing_regions))}"
                )

            for record in records:
                region_id = region_ids[record["region_name"]]
                cursor.execute(
                    """
                    SELECT province_id
                    FROM province_stats
                    WHERE region_id = %s
                      AND province_name = %s
                      AND reporting_period = %s
                    ORDER BY province_id
                    FOR UPDATE
                    """,
                    (region_id, record["province_name"], record["reporting_period"]),
                )
                existing_ids = [row[0] for row in cursor.fetchall()]
                if len(existing_ids) > 1:
                    raise ValueError(
                        f"Multiple province records exist for "
                        f"{record['province_name']!r} in region "
                        f"{record['region_name']!r} for {record['reporting_period']}."
                    )

                values = (
                    record["assessed_female"],
                    record["assessed_male"],
                    record["assessed_total"],
                    record["certified_female"],
                    record["certified_male"],
                    record["certified_total"],
                    record["certification_rate"],
                )
                if existing_ids:
                    cursor.execute(
                        """
                        UPDATE province_stats
                        SET assessed_female = %s,
                            assessed_male = %s,
                            assessed_total = %s,
                            certified_female = %s,
                            certified_male = %s,
                            certified_total = %s,
                            certification_rate = %s
                        WHERE province_id = %s
                        """,
                        (*values, existing_ids[0]),
                    )
                else:
                    cursor.execute(
                        """
                        INSERT INTO province_stats (
                            region_id,
                            province_name,
                            reporting_period,
                            assessed_female,
                            assessed_male,
                            assessed_total,
                            certified_female,
                            certified_male,
                            certified_total,
                            certification_rate
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            region_id,
                            record["province_name"],
                            record["reporting_period"],
                            *values,
                        ),
                    )

    print(f"Loaded {len(region_names)} regions and {len(records)} province records.")


def main() -> None:
    records = read_records()
    connection_string = load_connection_string()
    load_records(records, connection_string)


if __name__ == "__main__":
    main()
