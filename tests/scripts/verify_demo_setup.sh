#!/bin/bash
# Test script to verify the demo database setup

echo "======================================================================="
echo "MATILDA Demo Database - Verification Script"
echo "======================================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if database exists
echo -n "1. Checking database existence... "
if [ -f "data/university.db" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Missing!${NC}"
    echo "   Run: python scripts/generate_fake_university_db.py"
    exit 1
fi

# Check database size
echo -n "2. Checking database size... "
SIZE=$(ls -lh data/university.db | awk '{print $5}')
echo -e "${GREEN}✓${NC} ($SIZE)"

# Count tables
echo -n "3. Counting tables... "
TABLES=$(sqlite3 data/university.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
if [ "$TABLES" -eq 7 ]; then
    echo -e "${GREEN}✓${NC} (7 tables)"
else
    echo -e "${RED}✗ Expected 7, found $TABLES${NC}"
    exit 1
fi

# Count total tuples
echo -n "4. Counting total tuples... "
TOTAL=0
for table in department professor student course enrollment teaches advisor; do
    COUNT=$(sqlite3 data/university.db "SELECT COUNT(*) FROM $table;")
    TOTAL=$((TOTAL + COUNT))
done
if [ "$TOTAL" -eq 113 ]; then
    echo -e "${GREEN}✓${NC} (113 tuples)"
else
    echo -e "${YELLOW}⚠${NC} Expected 113, found $TOTAL"
fi

# Check scripts exist
echo -n "5. Checking generator script... "
if [ -f "scripts/generate_fake_university_db.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Missing!${NC}"
    exit 1
fi

echo -n "6. Checking inspector script... "
if [ -f "scripts/inspect_university_db.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Missing!${NC}"
    exit 1
fi

echo -n "7. Checking demo CLI... "
if [ -f "ai_doc/demo_cli.py" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Missing!${NC}"
    exit 1
fi

# Check documentation
echo -n "8. Checking data README... "
if [ -f "data/README.md" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Missing!${NC}"
    exit 1
fi

# Check Rich is installed
echo -n "9. Checking Rich library... "
if python -c "import rich" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Not installed!${NC}"
    echo "   Run: pip install rich"
    exit 1
fi

# Sample query
echo -n "10. Testing sample query... "
RESULT=$(sqlite3 data/university.db "SELECT name FROM student WHERE student_id=1;")
if [ -n "$RESULT" ]; then
    echo -e "${GREEN}✓${NC} (Found: $RESULT)"
else
    echo -e "${RED}✗ Query failed!${NC}"
    exit 1
fi

echo ""
echo "======================================================================="
echo -e "${GREEN}All checks passed! ✓${NC}"
echo "======================================================================="
echo ""
echo "You can now run:"
echo "  • python ai_doc/demo_cli.py              - Beautiful CLI demo"
echo "  • python scripts/inspect_university_db.py - Database inspector"
echo "  • python -m matilda_cli --database data/university.db - Full MATILDA"
echo ""
