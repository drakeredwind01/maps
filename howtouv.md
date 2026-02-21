# HOW TO UV — Sanctuary Map

## First time setup (create the virtual environment)

```bash
# From the project folder D:\Documents\github\maps
cd D:\Documents\github\maps

# Create the venv and install all dependencies from pyproject.toml
./uv venv
./uv sync

# For dev tools (jupyterlab, ruff, black)
./uv sync --extra dev
```

## Running the script

```bash
# Full San Diego County (default — slow, big data)
./uv run sanctuary_map.py

# Specific bounding box (faster for testing)
# format: south,north,west,east
./uv run sanctuary_map.py --bbox "32.70,32.80,-117.20,-117.10"

# Skip saving GeoPackage (just show the map)
./uv run sanctuary_map.py --no-save
```

## Outputs

| File                          | What it is                              |
|-------------------------------|-----------------------------------------|
| `sanctuary_exclusion_map.png` | Static map image (always saved)         |
| `safe_zones.gpkg`             | GeoPackage with all layers for QGIS use |

## If you add new dependencies

```bash
./uv add some-package
./uv sync
```

## Previous script (archived reference)
```
./uv run analyze_sd_risks.py
```
