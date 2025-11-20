# MATILDA CLI - Quick Start

## Installation

```bash
pip install -e .
```

## Basic Usage

```bash
matilda --config config.yaml
```

## Configuration

Create `config.yaml`:

```yaml
database:
  path: "data/db/"
  name: "mydb.db"

results:
  output_dir: "results"

logging:
  log_dir: "logs"
```

## Example Workflow

```bash
# 1. Create config
cat > config.yaml << EOF
database:
  path: "data/db/"
  name: "database.db"
results:
  output_dir: "results"
logging:
  log_dir: "logs"
mlflow:
  use: false
EOF

# 2. Run MATILDA
matilda --config config.yaml

# 3. Check results
ls results/
cat results/MATILDA_*_results.json
```

## Help

```bash
matilda --help
```

## More Information

- [INSTALL.md](INSTALL.md) - Detailed installation
- [README.md](README.md) - Full documentation
