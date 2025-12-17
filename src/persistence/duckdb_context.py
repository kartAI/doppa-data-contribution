import duckdb


def create_duckdb_context() -> duckdb.DuckDBPyConnection:
    db_context: duckdb.DuckDBPyConnection = duckdb.connect()
    db_context.install_extension("spatial")
    db_context.load_extension("spatial")
    db_context.install_extension("delta")
    db_context.load_extension("delta")
    db_context.install_extension("azure")
    db_context.load_extension("azure")
    db_context.install_extension("httpfs")
    db_context.load_extension("httpfs")

    db_context.execute("""
        CREATE OR REPLACE SECRET azure_secret(
            TYPE azure,
            PROVIDER config,
            ACCOUNT_NAME 'doppablobstorage'
        );
        """)

    db_context.execute("SET azure_transport_option_type = curl")

    return db_context
