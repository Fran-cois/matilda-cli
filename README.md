# MATILDA: Tuple-Generating Dependencies Discovery

[![PyPI version](https://badge.fury.io/py/matilda-cli.svg)](https://badge.fury.io/py/matilda-cli)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/badge/tests-61%20passed-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-45%25-orange)](tests/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17644035.svg)](https://doi.org/10.5281/zenodo.17644035)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Modern CLI](https://img.shields.io/badge/CLI-Rich-ff69b4)](https://github.com/Textualize/rich)

> **MATILDA** (Mining Approximate Tuple-Generating Dependencies in Large Databases) is a research-grade command-line tool for automatically discovering **Tuple-Generating Dependencies (TGDs)** in relational databases with a **modern, beautiful CLI interface**.

## ✨ New: Modern CLI Interface

MATILDA now features a **gorgeous, colorful interface** powered by [Rich](https://github.com/Textualize/rich):

- 🎨 **Beautiful ASCII art banner** with MATILDA branding
- 📊 **Live progress bars** with spinners and time tracking
- 📋 **Elegant tables** for displaying discovered rules
- 🎯 **Color-coded panels** for configuration and results
- ✨ **Status indicators** with emojis for better UX

Try it: `python demo_cli.py` for a quick preview!

See [CLI_MODERNIZATION.md](CLI_MODERNIZATION.md) for full details.

## 🎓 Academic Context

This tool was developed as part of post-doctoral research in database theory and knowledge discovery. It implements novel algorithms for mining logical rules from relational data, with applications in:

- **Data Quality**: Detecting inconsistencies and integrity violations
- **Schema Design**: Understanding implicit constraints and relationships
- **Knowledge Extraction**: Discovering hidden patterns in enterprise databases
- **Database Reverse Engineering**: Reconstructing business logic from legacy systems

## ✨ Key Features

- 🔍 **Automated TGD Discovery**: Extracts logical rules without manual specification
- 📊 **Confidence Metrics**: Ranks discovered rules by support and accuracy
- 🗄️ **Multi-Database Support**: Works with SQLite, MySQL, PostgreSQL via SQLAlchemy
- ⚡ **Efficient Pruning**: Uses constraint graphs and heuristics to scale to large schemas
- 📈 **MLflow Integration**: Optional experiment tracking for research workflows
- 🛡️ **Resource Management**: Built-in memory limits and timeout controls
- 📝 **Comprehensive Reporting**: Generates JSON and Markdown outputs

## 📦 Installation

### Quick Install

```bash
pip install -e .
```

### From Source

```bash
git clone https://github.com/Fran-cois/MATILDA.git
cd matilda_cli
pip install -e .
```

### With MLflow Support

```bash
pip install -e ".[mlflow]"
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## 🎯 Quick Start

### Demo Mode (Quickest Way to Try MATILDA)

```bash
# Run with pre-configured university demo database
matilda --demo imperfect_database
```

This will:
- ✅ Auto-create a demo SQLite database with 50 students, 81 enrollments
- 🔍 Run TGD discovery on realistic data with built-in violations
- 📊 Generate reports in `results/`

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for details.

### Basic Usage

```bash
# Run with default config.yaml
matilda

# Run with specific config
matilda --config /path/to/config.yaml
```

### Configuration

Create a `config.yaml` file:

```yaml
monitor:
  memory_threshold: 16106127360  # 15GB
  timeout: 3600  # 1 hour

database:
  path: "data/db/"
  name: "database.db"

logging:
  log_dir: "logs"

results:
  output_dir: "results"

mlflow:
  use: false
```

## 📖 Usage Examples

### Quick Demo with Fake Database

Try MATILDA instantly with our pre-built university database:

```bash
# Generate the demo database
python scripts/generate_fake_university_db.py

# Run the beautiful CLI demo
python ai_doc/demo_cli.py

# Inspect the database
python scripts/inspect_university_db.py

# Run MATILDA on the demo database
python -m matilda_cli --database data/university.db
```

The fake database contains:

- 5 departments (CS, Math, Physics, Business, Engineering)
- 10 professors
- 15 students
- 13 courses
- 42 enrollments + teaching assignments + advisor relationships
- **113 total tuples** across 7 tables

See [data/README.md](data/README.md) for more details.

### Example 1: Basic Discovery

```bash
# Run with default configuration
matilda --config config.yaml
```

**Sample Output:**

```
INFO - Discovered 47 rules
INFO - Top rule: student(X, Y) ∧ enrollment(Y, Z) → course(Z, W) [support: 156, confidence: 0.94]
```

### Example 2: Custom Parameters

```yaml
# config.yaml
monitor:
  memory_threshold: 16106127360  # 15GB
  timeout: 3600  # 1 hour

database:
  path: "data/databases/"
  name: "university.db"

algorithm:
  nb_occurrence: 5      # Minimum support
  max_table: 4          # Max tables per rule
  max_vars: 8           # Max variables per rule

logging:
  log_dir: "logs"

results:
  output_dir: "results"
```

### Example 3: With MLflow Experiment Tracking

```bash
# Install with MLflow support
pip install -e ".[mlflow]"

# Configure MLflow in config.yaml
cat > config.yaml << EOF
mlflow:
  use: true
  tracking_uri: "http://localhost:5000"
  experiment_name: "MATILDA_University_DB"
  
database:
  path: "data/"
  name: "university.db"
EOF

# Start MLflow server (separate terminal)
mlflow server --host 127.0.0.1 --port 5000

# Run MATILDA with tracking
matilda --config config.yaml
```

### Example 4: Programmatic Usage

```python
from pathlib import Path
from matilda_cli.database.alchemy_utility import AlchemyUtility
from matilda_cli.algorithms.matilda import MATILDA

# Connect to database
db_path = Path("data/university.db")
db = AlchemyUtility(db_path)

# Configure algorithm
settings = {
    "nb_occurrence": 3,
    "max_table": 3,
    "max_vars": 6
}

# Discover rules
matilda = MATILDA(db, settings)
for rule in matilda.discover_rules():
    print(f"{rule} [support: {rule.support}, confidence: {rule.confidence:.2f}]")

# Cleanup
db.close()
```

## 🔧 Configuration Options

### Complete Configuration Reference

```yaml
# Monitor Settings
monitor:
  memory_threshold: 16106127360  # Maximum memory usage (bytes, default: 15GB)
  timeout: 3600                   # Maximum execution time (seconds, default: 1h)

# Database Settings  
database:
  path: "data/databases/"         # Directory containing database files
  name: "database.db"             # Database filename

# Algorithm Settings
algorithm:
  nb_occurrence: 3                # Minimum rule support (default: 3)
  max_table: 3                    # Maximum tables per rule (default: 3)
  max_vars: 6                     # Maximum variables per rule (default: 6)

# Logging Settings
logging:
  log_dir: "logs"                 # Directory for log files
  level: "INFO"                   # Log level: DEBUG, INFO, WARNING, ERROR

# Results Settings
results:
  output_dir: "results"           # Directory for output files
  
# MLflow Settings (optional)
mlflow:
  use: false                      # Enable/disable MLflow tracking
  tracking_uri: "http://localhost:5000"  # MLflow server URL
  experiment_name: "MATILDA Discovery"   # Experiment name
```

### Algorithm Parameters Tuning Guide

| Parameter         | Effect                                              | Recommendation                               |
| ----------------- | --------------------------------------------------- | -------------------------------------------- |
| `nb_occurrence` | Higher = more general rules, fewer results          | Start with 3-5 for exploration               |
| `max_table`     | Higher = more complex rules, slower execution       | 3 for most cases, 4-5 for complex schemas    |
| `max_vars`      | Higher = more expressive rules, larger search space | 6 is balanced, increase to 8-10 for research |

## 📊 Output Format

MATILDA generates three types of output:

### 1. JSON Rules File

```json
{
  "rules": [
    {
      "body": ["student(X, Y)", "enrollment(Y, Z)"],
      "head": ["course(Z, W)"],
      "support": 156,
      "confidence": 0.94,
      "accuracy": 0.94,
      "tgd_string": "student(X, Y) ∧ enrollment(Y, Z) → course(Z, W)"
    }
  ],
  "metadata": {
    "database": "university.db",
    "total_rules": 47,
    "execution_time": "12.3s"
  }
}
```

### 2. Markdown Report

Auto-generated summary with:

- Execution statistics
- Top 5 rules by confidence
- Database schema overview
- Timestamps and configuration

### 3. Detailed Logs

```
2025-11-18 10:15:23 - INFO - Starting MATILDA discovery
2025-11-18 10:15:24 - INFO - Loaded database: university.db (3 tables, 12 attributes)
2025-11-18 10:15:25 - INFO - Generated 45 candidate rules
2025-11-18 10:15:26 - INFO - Pruned 12 rules (support threshold)
2025-11-18 10:15:27 - INFO - Discovered 47 valid TGDs
```

## 🛠️ Development

### Project Architecture

```
matilda_cli/
├── matilda_cli/              # Main package
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── algorithms/           # MATILDA algorithm implementation
│   │   ├── matilda.py        # Main algorithm class
│   │   └── MATILDA/          # Core discovery logic
│   │       ├── tgd_discovery.py       # TGD mining algorithms
│   │       ├── constraint_graph.py    # Graph-based representation
│   │       └── candidate_rule_chains.py  # Rule generation
│   ├── database/             # Database utilities
│   │   ├── alchemy_utility.py         # SQLAlchemy interface
│   │   ├── query_utility.py           # Query optimization
│   │   └── data_exporter.py           # Export utilities
│   └── utils/                # Shared utilities
│       ├── config_loader.py           # YAML configuration
│       ├── rules.py                   # Rule data structures
│       └── monitor.py                 # Resource monitoring
├── tests/                    # Comprehensive test suite
│   ├── algorithms/           # Algorithm tests (61 tests passing)
│   ├── database/             # Database utilities tests
│   ├── fixtures/             # Test databases and fixtures
│   └── benchmarks/           # Performance benchmarks
├── scripts/                  # Development utilities
│   ├── check_tests.py        # Test integrity verification
│   ├── run_benchmarks.py     # Performance benchmarking
│   └── generate_test_report.py  # Test coverage reports
├── docs/                     # Documentation (auto-generated)
├── setup.py                  # Package configuration
├── pyproject.toml            # Modern Python packaging
└── pytest.ini                # Test configuration
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=matilda_cli tests/

# Run specific test categories
pytest tests/algorithms/         # Algorithm tests
pytest tests/database/           # Database tests
pytest -m benchmark tests/       # Performance benchmarks only

# Run tests with detailed output
pytest -v --tb=short tests/
```

### Test Suite Status

- **Total Tests**: 61 ✅
- **Coverage**: 45%
- **Test Categories**:
  - Unit Tests: 35 tests
  - Integration Tests: 20 tests
  - Benchmarks: 6 tests
- **Databases**: 3 test schemas (university, employee, retail)

### Code Quality Tools

```bash
# Type checking
mypy matilda_cli/

# Code formatting
black matilda_cli/ tests/

# Linting
ruff check matilda_cli/

# Run all checks
./scripts/check_tests.py
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Core Dependencies**:
  - SQLAlchemy >= 2.0
  - PyYAML >= 6.0
  - psutil >= 5.9
  - tqdm >= 4.66
- **Optional**:
  - mlflow >= 2.0 (for experiment tracking)
  - pytest >= 7.0 (for development)

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [Testing Guide](TESTING.md) - Comprehensive testing documentation
- [Test Status](TEST_STATUS.md) - Current test suite status
- [API Documentation](docs/) - Full API reference (auto-generated)

## 🤝 Contributing

Contributions are welcome! This is an academic research project, so please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality
4. **Ensure** all tests pass (`pytest tests/`)
5. **Document** your changes
6. **Commit** with clear messages (`git commit -m 'Add amazing feature'`)
7. **Push** to your branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Development Setup

```bash
# Clone repository
git clone https://github.com/Fran-cois/MATILDA.git
cd matilda_cli

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode with all extras
pip install -e ".[dev,mlflow]"

# Verify installation
matilda --help
pytest tests/
```

## Related Datasets

Test databases are based on schemas from:

- Zenodo Repository: [DOI 10.5281/zenodo.17644035](https://doi.org/10.5281/zenodo.17644035)

## 🙏 Acknowledgments

- **Database Theory Community**: For foundational work on TGDs and dependencies
- **SQLAlchemy Project**: For the excellent database abstraction layer
- **Open Source Contributors**: For tools and libraries that made this possible
- **Academic Reviewers**: For feedback on algorithm design and implementation

## 🗺️ Roadmap

### Current Version (0.1.0)

- ✅ Core TGD discovery algorithm
- ✅ SQLite, MySQL, PostgreSQL support
- ✅ MLflow integration
- ✅ Comprehensive test suite

### Planned Features (0.2.0)

- 🔄 Parallel rule discovery
- 🔄 Interactive rule refinement
- 🔄 Web-based visualization
- 🔄 Incremental discovery for large databases

### Future Research Directions

- 🔮 Probabilistic TGDs
- 🔮 Temporal dependency discovery
- 🔮 Multi-database federation
- 🔮 Machine learning-guided pruning

## 🏆 Academic Impact

This tool is designed to support:

- **PhD Students**: As a baseline for dependency discovery research
- **Database Researchers**: For experimental evaluation and comparison
- **Industry Practitioners**: For data quality assessment and schema understanding
- **Educators**: As a teaching tool for database theory concepts
