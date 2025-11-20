# MATILDA Demo Mode

MATILDA CLI includes a demo mode that allows you to quickly test the TGD rule discovery algorithm on a pre-configured university database.

## Quick Start

Run MATILDA with one of the demo databases:

```bash
# Run with the demo database (contains violations for rule discovery)
python3 -m matilda_cli --demo imperfect_database

# Or using the alias (both use the same underlying database)
python3 -m matilda_cli --demo perfect_database
```

## Demo Database

Both demo options use the same test database (`tests/data/university.db`) which is specifically designed to demonstrate MATILDA's TGD discovery capabilities. The database contains:

- **50 students** across 2 departments
- **10 professors**
- **10 courses**
- **81 enrollments** (with 5 violations: fake students enrolled in courses)
- **48 advisor relationships** (with 3 violations: fake students assigned to advisors)

### Database Schema

```
department (dept_id, dept_name)
professor (prof_id, name, dept_id)
student (student_id, name, year, dept_id)
course (course_id, title, dept_id)
enrollment (enrollment_id, student_id, course_id)
advisor (advisor_id, prof_id, student_id)
teaches (teaches_id, prof_id, course_id, semester)
```

### Expected Rules

The demo database is designed to help MATILDA discover rules such as:

- `enrollment(X, Y) → student(X, ...)` - Enrolled students should exist in the student table
- `advisor(X, Y) → student(Y, ...)` - Advised students should exist in the student table

**Note:** Rule discovery depends on the configuration parameters (`nb_occurrence`, `max_table`, `max_vars`). With small databases, MATILDA may discover 0 rules if the parameters are too restrictive. This is expected behavior.

## Configuration

The demo mode uses the configuration from `config.yaml`. To adjust rule discovery parameters, edit this file:

```yaml
database:
  # Demo databases are created in data/db/
  path: "data/db/"
  
algorithm:
  nb_occurrence: 3      # Minimum number of times a pattern must occur
  max_table: 3          # Maximum number of tables in a rule
  max_vars: 6           # Maximum number of variables in a rule
```

### Adjusting for Small Databases

For small demo databases, you may want to lower `nb_occurrence`:

```yaml
algorithm:
  nb_occurrence: 2      # Lower threshold for small databases
```

## Output Files

After running the demo, MATILDA creates:

- `results/report_MATILDA_university_{demo_type}.md` - Detailed markdown report
- `results/MATILDA_university_{demo_type}_results.json` - JSON results with metrics
- `data/db/university_{demo_type}.db` - The demo SQLite database

## Creating Custom Demo Databases

If you want to modify the demo database, edit `tests/scripts/create_db_with_violations.py` and then:

```bash
# Recreate the test database
python3 tests/scripts/create_db_with_violations.py

# Remove existing demo databases to force recreation
rm -f data/db/university_*.db

# Run demo mode (will copy the new test database)
python3 -m matilda_cli --demo imperfect_database
```

## Troubleshooting

### No Rules Discovered

This is normal for small databases with restrictive configuration parameters. Try:

1. Lowering `nb_occurrence` in `config.yaml`
2. Checking that the database has enough violations
3. Reviewing the report in `results/` for detailed statistics

### Database Not Found Errors

The demo mode automatically creates the test database if it doesn't exist. If you see errors:

```bash
# Manually create the test database
python3 tests/scripts/create_db_with_violations.py

# Verify it was created
ls -lh tests/data/university.db
```

## Example Session

```bash
# Run demo
$ python3 -m matilda_cli --demo imperfect_database

╔═══════════════════════════════════════════╗
║                                           ║
║   MATILDA - Mining Approximate TGDs       ║
║                                           ║
╚═══════════════════════════════════════════╝

✓ Demo database created: data/db/university_imperfect_database.db
ℹ Database contains: 50 students, 81 enrollments, 48 advisors

⚙️  Configuration
  🗄️  Database    university_imperfect_database.db
  🎯 Min Occurrence    3
  📊 Max Tables        3

Starting MATILDA Discovery Process...
[... discovery output ...]

✓ Process completed successfully!
Total rules discovered: 0

📄 Report saved to: results/report_MATILDA_university_imperfect_database.md
```

## Next Steps

After trying the demo, you can:

1. Modify `tests/scripts/create_db_with_violations.py` to create custom violations
2. Adjust `config.yaml` parameters to tune rule discovery
3. Run MATILDA on your own databases using the standard mode
4. Review the generated reports in `results/`

For more information, see:
- [README.md](README.md) - Main documentation
- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [CLI_DEMO_GUIDE.md](ai_doc/CLI_DEMO_GUIDE.md) - Detailed CLI reference
