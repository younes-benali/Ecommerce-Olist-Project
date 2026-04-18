from pathlib import Path

# Project root (two levels up from this file: src/ → project root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Database connection 
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "olist_db"
DB_USER = "postgres"
DB_PASSWORD = "0000"  

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Raw data source (your original CSV files)
OLIST_DB = BASE_DIR / "olist_db"

# Data pipeline folders
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_INTERIM = BASE_DIR / "data" / "interim"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

# Models & reports
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_FIGURES = REPORTS_DIR / "figures"
REPORTS_METRICS = REPORTS_DIR / "metrics"

# Create all directories if they don't exist
for dir_path in [DATA_RAW, DATA_INTERIM, DATA_PROCESSED, MODELS_DIR,
                 REPORTS_FIGURES, REPORTS_METRICS]:
    dir_path.mkdir(parents=True, exist_ok=True)