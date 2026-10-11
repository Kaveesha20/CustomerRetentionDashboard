# src/load_db.py
# Job: take the cleaned tables and write them into SQL Server as real
# database tables, so SQL (Level 1) and Power BI (Level 4) can use them.

from sqlalchemy import create_engine
from config import CONNECTION_STRING


def get_engine():
    """
    Creates a SQLAlchemy 'engine' - this is the object that knows how
    to talk to SQL Server using the connection string from config.py.
    We create it once here and reuse it, rather than reconnecting
    every time we write a table.
    """
    return create_engine(CONNECTION_STRING)


def load_all(cleaned_tables: dict):
    """
    Writes every cleaned DataFrame into SQL Server as its own table.
    to_sql() is pandas' built-in function for this - it converts the
    DataFrame's columns into SQL columns automatically.
    """
    engine = get_engine()

    for name, df in cleaned_tables.items():
        df.to_sql(
            name=name,           # table name in SQL Server, e.g. "customers"
            con=engine,
            if_exists="replace", # overwrite the table if it already exists -
                                 # useful while developing, so re-running this
                                 # script doesn't create duplicate data
            index=False,         # don't write pandas' row-number index as a column -
                                 # we don't need it, SQL tables don't use it
        )
        print(f"Loaded {name} into SQL Server ({df.shape[0]} rows)")


if __name__ == "__main__":
    from ingest import load_raw_data
    from clean import clean_all

    tables = load_raw_data()
    cleaned = clean_all(tables)
    load_all(cleaned)
    print("\nAll tables loaded into SQL Server successfully.")