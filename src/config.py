# src/config.py
# Central place for settings. Other files import from here instead of
# repeating connection details everywhere - if the server name changes,
# you only fix it in one place.

import os
from pathlib import Path
from dotenv import load_dotenv

# load_dotenv() reads the .env file in the project root and makes its
# values available via os.getenv(). This keeps settings out of the code.
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

# Path(__file__) = this file's location. .parent.parent goes up two
# folders (src -> project root), so this works no matter where you run
# the script from.
PROJECT_ROOT = Path(__file__).parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

# The connection string SQLAlchemy/pyodbc needs to reach SQL Server.
# - driver=ODBC+Driver+18+for+SQL+Server: the driver you installed
# - Trusted_Connection=yes: use Windows login, no password needed
# - TrustServerCertificate=yes: accept the local self-signed certificate
CONNECTION_STRING = (
    f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
    "?driver=ODBC+Driver+18+for+SQL+Server"
    "&Trusted_Connection=yes"
    "&TrustServerCertificate=yes"
)