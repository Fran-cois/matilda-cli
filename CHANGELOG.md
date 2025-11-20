# Changelog

All notable changes to MATILDA CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-20

### Added
- Initial release of MATILDA CLI
- TGD (Tuple-Generating Dependencies) discovery algorithm
- Beautiful CLI interface with Rich console
- Demo mode with `--demo` flag (perfect_database and imperfect_database)
- YAML-based configuration system
- Support for SQLite, MySQL databases
- CSV/TSV export capabilities
- MLflow integration for experiment tracking
- Comprehensive test suite
- Database connection management
- Index optimization for performance
- Rule accuracy and confidence metrics
- JSON and Markdown report generation

### Fixed
- Fixed `max_nb_occurrence_per_table_and_column` None check bug
- Removed networkx dependency (unused)
- Disabled CSV/TSV generation by default for performance
- Fixed database path configuration

### Changed
- Database output path changed from `data/db/` to `data/`
- Algorithm settings moved to dedicated `algorithm` section in config
- Improved logging and error messages

### Documentation
- Added comprehensive README with installation and usage examples
- Added QUICKSTART guide
- Added DEMO_GUIDE with demo database information
- Added SETUP_AND_TESTING guide
- Added PUBLISHING guide for PyPI deployment

## [0.0.1] - 2024-xx-xx (Internal Development)

### Added
- Initial development version
- Core MATILDA algorithm implementation
- Basic CLI functionality

---

[Unreleased]: https://github.com/Fran-cois/MATILDA/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Fran-cois/MATILDA/releases/tag/v0.1.0
