# This module's name (double __) makes python unittest runner to execute this BEFORE db module (or any other modules depending on 'db') otherwise db module
# will NOT connect properly to Postgres instance initialized here
import os

from pathlib import Path
from testcontainers.postgres import PostgresContainer

db_migration_scripts_location = Path(__file__).parent.parent.parent / "db" / "migrations"
postgres = PostgresContainer("postgres:16.3-alpine")
postgres.with_volume_mapping(host=str(db_migration_scripts_location), container=f"/docker-entrypoint-initdb.d/")
postgres.start()

os.environ["DB_HOST"] = postgres.get_container_host_ip()
os.environ["DB_PORT"] = postgres.get_exposed_port(5432)
os.environ["DB_NAME"] = postgres.dbname
os.environ["DB_USER"] = postgres.username
os.environ["DB_PW"] = postgres.password
