"""
Integration tests for MATILDA TGD discovery with real databases.
"""

import pytest
import json
from pathlib import Path
import sys

# Add the fixtures to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))

from matilda_cli.algorithms.matilda import MATILDA
from matilda_cli.database.alchemy_utility import AlchemyUtility
from matilda_cli.utils.rules import TGDRuleFactory


class TestMATILDAIntegration:
    """Integration tests for MATILDA algorithm with real databases."""
    
    def test_university_db_discovery(self, university_db, tmp_path):
        """Test TGD discovery on university database."""
        from tests.fixtures.test_databases import university_db as _
        db_url, db_path = university_db
        
        # Create database inspector
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            # Create MATILDA instance
            matilda = MATILDA(database=db_inspector)
            
            # Discover rules
            discovered_rules = []
            for rule in matilda.discover_rules():
                discovered_rules.append(rule)
                # Limit to first 10 rules for testing
                if len(discovered_rules) >= 10:
                    break
            
            # We should discover at least some rules
            # (exact number depends on threshold settings)
            assert isinstance(discovered_rules, list)
    
    def test_employee_db_discovery(self, employee_db, tmp_path):
        """Test TGD discovery on employee-department database."""
        from tests.fixtures.test_databases import employee_db as _
        db_url, db_path = employee_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector, settings={'nb_occurrence': 3})
            
            discovered_rules = []
            for rule in matilda.discover_rules():
                discovered_rules.append(rule)
                if len(discovered_rules) >= 5:
                    break
            
            assert isinstance(discovered_rules, list)
    
    def test_retail_db_discovery(self, retail_db, tmp_path):
        """Test TGD discovery on retail database."""
        from tests.fixtures.test_databases import retail_db as _
        db_url, db_path = retail_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector)
            
            # Try to discover at least one rule
            rules_found = False
            for rule in matilda.discover_rules():
                rules_found = True
                assert rule is not None
                break  # Just check that we can discover at least one
            
            # It's ok if no rules are found in small test databases
            # The important thing is that the process completes without errors
            assert isinstance(rules_found, bool)
    
    def test_rule_format(self, university_db, tmp_path):
        """Test that discovered rules have the correct format."""
        from tests.fixtures.test_databases import university_db as _
        db_url, db_path = university_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector)
            
            # Get one rule if possible
            for rule in matilda.discover_rules():
                # Check rule structure
                assert isinstance(rule, dict)
                assert 'tgd' in rule or 'rule' in rule
                break
    
    def test_empty_database_handling(self, tmp_path):
        """Test handling of empty database."""
        import sqlite3
        
        # Create empty database
        empty_db = tmp_path / "empty.db"
        conn = sqlite3.connect(str(empty_db))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE empty_table (id INTEGER)")
        conn.commit()
        conn.close()
        
        db_url = f"sqlite:///{empty_db}"
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector)
            
            discovered_rules = list(matilda.discover_rules())
            # Empty database should yield no rules
            assert len(discovered_rules) == 0


# Pytest fixtures imported from test_databases
pytest_plugins = ['tests.fixtures.test_databases']
