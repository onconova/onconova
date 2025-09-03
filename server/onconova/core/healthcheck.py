"""
This module provides an API endpoint for health checking the server and its database. 
"""

import time
from typing import Literal, Optional, Union

from django.db import DEFAULT_DB_ALIAS, ProgrammingError, connections
from django.db.migrations.executor import MigrationExecutor
from django.db.utils import OperationalError
from ninja import Field, Schema
from ninja_extra import ControllerBase, api_controller, route


class HealthCheck(Schema):
    """
    Schema representing the health status of the server and its components.

    Attributes:
        server (Literal["ok"]): Indicates whether the server is online.
        database (Union[Literal["ok"], Literal["error"]]): Indicates the status of the database connection.
        database_connection_time_ms (Optional[float]): Time taken to connect to the database in milliseconds.
        migrations (Union[Literal["ok"], Literal["pending"], Literal["error"]]): Status of database migrations.
    """
    server: Literal["ok"] = Field(
        title="Server Status", description="Whether the server is online"
    )
    database: Union[Literal["ok"], Literal["error"]] = Field(
        title="Database Status", description="Whether the database is online"
    )
    database_connection_time_ms: Optional[float] = Field(
        default=None,
        title="Database Connection Time",
        description="Database connection time in milliseconds",
    )
    migrations: Union[Literal["ok"], Literal["pending"], Literal["error"]] = Field(
        title="Migration Status", description="Whether there are pending migrations"
    )


@api_controller(
    "/healthcheck",
    tags=["API Health"],
)
class HealthCheckController(ControllerBase):
    """
    API controller for performing health checks on the server and its database.
    """

    @route.get(
        path="",
        response={
            200: HealthCheck,
            401: None,
            400: None,
            403: None,
            500: None,
        },
        operation_id="healthcheck",
        openapi_extra=dict(security=[]),
    )
    def health_check(self):
        """
        Performs a health check of the server, database connection, and database migrations.
        """
        # Check server status (if this endpoint is hit, server is up)
        server_status = "ok"
        # Check database connection and measure connection speed
        db_connection_time_ms = None
        try:
            start = time.time()
            connections["default"].cursor()
            end = time.time()
            database_status = "ok"
            db_connection_time_ms = (end - start) * 1000  # milliseconds
        except OperationalError:
            database_status = "error"

        # Check for unapplied migrations
        try:
            connection = connections[DEFAULT_DB_ALIAS]
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            if plan:
                migrations_status = "pending"
            else:
                migrations_status = "ok"
        except (OperationalError, ProgrammingError):
            migrations_status = "error"

        return HealthCheck(
            server=server_status,
            database=database_status,
            database_connection_time_ms=(
                round(db_connection_time_ms, 2)
                if db_connection_time_ms is not None
                else None
            ),
            migrations=migrations_status,
        )
