import logging
from typing import List, Tuple

import colorama  # Ajout de colorama
from sqlalchemy import MetaData, text
from tqdm import tqdm

colorama.init(autoreset=True)
# from matilda_cli.utils.log_setup import setup_loggers


class IndexManager:
    """
    Manages index creation (especially for SQLite).
    """

    def __init__(self, conn, metadata: MetaData):
        self.conn = conn
        self.metadata = metadata
        self.logger = logging.getLogger("query_time")

    def create_indexes(self):
        """Create indexes for all columns in all tables."""
        with self.conn.begin():
            for table in self.metadata.tables.values():
                for column in table.columns:
                    index_name = f"idx_{table.name}_{column.name}"
                    self.conn.execute(
                        text(
                            f"CREATE INDEX IF NOT EXISTS {index_name} ON {table.name} ({column.name});"
                        )
                    )

    def create_composed_indexes(self, cols_list: List[Tuple[str, str, str, str]]):
        """Create composed indexes for tuples of columns."""
        for t1, c1, t2, c2 in tqdm(cols_list, desc="Creating composed indexes", leave=False):
            if t1 == t2 and c1 != c2:
                index_name = f"idx_{t1}_{c1}_{c2}"
                self.conn.execute(
                    text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {t1} ({c1}, {c2});")
                )
                self.conn.commit()
