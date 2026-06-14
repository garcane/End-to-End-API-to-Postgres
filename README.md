# MeteoFlow

**An end-to-end ETL pipeline that pulls UK weather forecasts from the Open-Meteo API, transforms them with pandas, and loads them into PostgreSQL — ready for SQL analysis.**

MeteoFlow fetches a seven-day hourly forecast for thirteen UK cities, tidies the raw JSON into a single clean table, and upserts it into a PostgreSQL database. A library of analytical SQL queries then sits on top, covering everything from daily aggregates to moving averages and city-to-city comparisons.

---

## How it works

The pipeline follows the classic three-stage ETL pattern. A useful analogy is a kitchen: **Extract** is the grocery run, **Transform** is the prep and chopping, and **Load** is plating up for the table.

**Extract.** For each location, MeteoFlow calls the Open-Meteo forecast endpoint and requests seven hourly variables: temperature, relative humidity, precipitation, wind speed, wind direction, weather code, and surface pressure. No API key is required (Open-Meteo is free for non-commercial use, up to 10,000 calls per day).

**Transform.** The raw JSON responses — one crumpled, nested structure per city — are flattened into a single tidy pandas DataFrame where each row is one hour, in one location, with one set of measurements. This stage standardises column names, casts data types, removes duplicates, and audits for nulls.

**Load.** The cleaned data is written to PostgreSQL using an upsert (`INSERT … ON CONFLICT DO UPDATE`). This makes the pipeline **idempotent** — you can re-run it as often as you like and existing rows are refreshed rather than duplicated.

---

## Project structure

```
MeteoFlow/
├── etl_pipeline.ipynb     # The ETL pipeline (extract → transform → load)
├── .env                   # Database credentials (not committed to git)
├── .gitignore
├── backups/               # Database backups
└── sql/
    ├── 01_create_database.sql
    ├── 02_create_user.sql              # Role + privileges (see note below)
    ├── 03_create_tables.sql
    ├── 04_update_tables.sql            # Upsert statement
    ├── 05_..._summary statistics per location.sql
    ├── 06_..._daily aggregate by location.sql
    ├── 07_..._top 5 windiest hours.sql
    ├── 08_..._rank locations by avg temperature.sql
    ├── 09_..._weather code interpretation.sql
    ├── 10_..._hourly temperature change.sql
    ├── 11_..._monthly precipitation comparison.sql
    ├── 12_..._extreme conditions.sql
    ├── 13_..._7-hour moving average.sql
    ├── 14_..._compare two cities.sql
    └── 15_..._View avg_city_temp location.sql
```

---

## Requirements

- Python 3.10 or later
- PostgreSQL 15 or later
- The following Python packages:

```bash
pip install requests numpy pandas psycopg2-binary python-dotenv
```

---

## Setup

### 1. Configure your credentials

Create a `.env` file in the project root (this file is git-ignored and must never be committed):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=weather_forecast
POSTGRES_USER=weather_user
POSTGRES_PASSWORD=your_password_here
```

### 2. Create the database and role

Run the SQL scripts in order. Scripts `01` and `02` must be executed by a **superuser** (typically the `postgres` login):

```bash
psql -U postgres -f sql/01_create_database.sql
psql -U postgres -d weather_forecast -f sql/02_create_user.sql
psql -U postgres -d weather_forecast -f sql/03_create_tables.sql
```

> **Important — PostgreSQL 15+ privileges.** From version 15 onwards, ordinary users no longer receive `CREATE` on the `public` schema by default. The `weather_user` role therefore needs an explicit `GRANT CREATE ON SCHEMA public`, which is included in `02_create_user.sql`. Without it, table creation fails with `ERROR: permission denied for schema public` (SQLSTATE 42501). The `GRANT CREATE` and `ALTER DEFAULT PRIVILEGES` statements in that script must be run by a superuser or the schema owner — a role cannot grant itself privileges it does not already hold.

### 3. Run the pipeline

Open `etl_pipeline.ipynb` and run all cells, or execute it headlessly:

```bash
jupyter nbconvert --to notebook --execute etl_pipeline.ipynb
```

The pipeline will fetch, transform, and load the data, logging its progress as it goes.

---

## Configuration

Both lists live near the top of the notebook and can be edited freely:

- **`LOCATIONS`** — the cities to fetch. Each entry needs a `name`, `latitude`, and `longitude`. The default set covers thirteen UK cities, including London, Manchester, Edinburgh, Cardiff, and Belfast.
- **`HOURLY_VARIABLES`** — the weather variables requested from the API. Any value supported by Open-Meteo's hourly endpoint can be added.

---

## The data

All data is loaded into a single table, `weather_forecast`. Each row represents one hour of forecast data for one location, uniquely identified by the combination of `location_name` and `time`.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Primary key |
| `location_name` | VARCHAR(100) | City name |
| `latitude`, `longitude` | FLOAT | Coordinates |
| `elevation_m` | FLOAT | Elevation in metres |
| `time` | TIMESTAMPTZ | Forecast timestamp |
| `temperature_2m` | FLOAT | Air temperature at 2 m (°C) |
| `relative_humidity_2m` | FLOAT | Relative humidity at 2 m (%) |
| `precipitation` | FLOAT | Precipitation (mm) |
| `wind_speed_10m` | FLOAT | Wind speed at 10 m (km/h) |
| `wind_direction_10m` | FLOAT | Wind direction at 10 m (°) |
| `weather_code` | INTEGER | WMO weather interpretation code |
| `surface_pressure` | FLOAT | Surface pressure (hPa) |
| `fetched_at` | TIMESTAMPTZ | When the row was retrieved |

---

## Analysis queries

The `sql/` directory contains a catalogue of ready-to-run analytical queries against the loaded data, including:

- Summary statistics and daily aggregates per location
- The windiest hours overall
- Ranking locations by average temperature using window functions
- Translating numeric weather codes into human-readable conditions
- Hour-on-hour temperature change and a seven-hour moving average for smoothing
- Monthly precipitation comparisons and a side-by-side comparison of two cities
- Reusable views (`24_views.sql`)

---

## Credits

Weather data provided by [Open-Meteo](https://open-meteo.com/), free for non-commercial use.
