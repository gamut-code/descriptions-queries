import configparser
import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from tqdm import tqdm


class PostgresDatabase_GWS:

    def __init__(self, db="postgres"):
        assert isinstance(db, str)
        self.conn = self._connect2postgres_(db=db)
        pass

    def query(self, statement, parse_dates=None, chunksize=100000):
        assert isinstance(statement, str)
        assert isinstance(parse_dates, list) or parse_dates is None
        assert isinstance(chunksize, int)
        df = []
        for chunk_df in tqdm(pd.read_sql(sql=statement, con=self.conn, parse_dates=parse_dates, chunksize=chunksize)):
            df.append(chunk_df)
        if len(df) > 0:
            df = pd.concat(df)
        if len(df) == 0:
            df = pd.DataFrame()
        return df

    def get_tables(self):
        df = self.query(
            """
            SELECT *
            FROM pg_catalog.pg_tables;
            """
        )
        tables = df[["tablename"]].values.flatten()
        return tables

    def get_columns(self, tablename):
        assert isinstance(tablename, str)
        df = self.query(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_NAME = '{tablename}';
            """.format(tablename=tablename))
        columns = df["column_name"].values.flatten()
        return columns

    def get_table_head(self, tablename, columns=None, nrows=5):
        assert isinstance(tablename, str)
        assert isinstance(columns, list) or columns is None
        assert isinstance(nrows, int)
        if columns is None:
            columns = "*"
        if columns is not None:
            columns = ", ".join(columns)
        df = self.query(
            """
            SELECT {columns}
            FROM {tablename}
            LIMIT {nrows};
            """.format(columns=columns, tablename=tablename, nrows=nrows)
        )
        return df

    def _connect2postgres_(self, db):
        args = self._getcreds_()
        host = "gac-rds-internal-readonly.graingercloud.com"
        port = 5432
        engine = create_engine(
            "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db}".format(
                username=args[0], password=args[1], port=port, host=host, db=db
            )
        )
        conn = engine.connect()
        return conn

    def __del__(self):
        self.conn.close()
        pass

    @staticmethod
    def _getcreds_():
        parser = configparser.RawConfigParser()
        cred_path = os.path.expanduser("~/.Pyenviron")
        parser.read(cred_path)
        username = parser.get("POSTGRES_GWS", "USER")
        password = parser.get("POSTGRES_GWS", "PASS")
        return [username, password]
