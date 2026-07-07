"""
Database diagnostics and health checking utilities.

Provides tools for:
- Connection testing
- Health monitoring
- Performance diagnostics
- Connection pool status
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import text, inspect
from ..database.connection import import logging

logger = logging.getLogger(__name__)


class DatabaseDiagnostics:
    """Diagnostics utilities for database health and performance"""

    @staticmethod
    def test_connection() -> bool:
        """Test database connectivity.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                result.close()
            logger.info("✓ Database connection test passed")
            return True
        except Exception as e:
            logger.error(f"✗ Database connection test failed: {str(e)}")
            return False

    @staticmethod
    def get_server_info() -> Dict[str, Any]:
        """Get MySQL server information.

        Returns:
            dict: Server version and other info
        """
        try:
            with engine.connect() as connection:
                result = connection.execute(text("SELECT VERSION()"))
                version = result.scalar()

                result = connection.execute(
                    text("SHOW STATUS LIKE 'Threads%'")
                )
                threads = {row[0]: row[1] for row in result}

                return {
                    "version": version,
                    "threads": threads,
                    "connection_valid": True,
                }
        except Exception as e:
            logger.error(f"Failed to get server info: {str(e)}")
            return {"connection_valid": False, "error": str(e)}

    @staticmethod
    def get_connection_pool_status() -> Dict[str, Any]:
        """Get current connection pool status.

        Returns:
            dict: Pool statistics
        """
        try:
            pool = engine.pool

            return {
                "pool_size": pool.size(),
                "checked_in_connections": pool.checkedin(),
                "overflow": pool.overflow(),
                "total_connections": pool.size() + pool.overflow(),
                "pool_type": str(type(pool).__name__),
                "echo": engine.echo,
            }
        except Exception as e:
            logger.error(f"Failed to get pool status: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """Get database-level statistics.

        Returns:
            dict: Database statistics
        """
        stats = {"timestamp": datetime.utcnow().isoformat()}

        try:
            with engine.connect() as connection:
                # Get database size
                result = connection.execute(
                    text("""
                    SELECT
                        table_schema as 'Database',
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as 'Size (MB)'
                    FROM information_schema.tables
                    WHERE table_schema NOT IN ('mysql', 'performance_schema', 'information_schema')
                    GROUP BY table_schema
                    """)
                )

                db_sizes = {}
                for row in result:
                    db_sizes[row[0]] = row[1]

                stats["databases"] = db_sizes

                # Get connection count
                result = connection.execute(
                    text("SHOW STATUS LIKE 'Threads_connected'")
                )
                row = result.first()
                if row:
                    stats["active_connections"] = int(row[1])

        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            stats["error"] = str(e)

        return stats

    @staticmethod
    def get_table_stats() -> Dict[str, Dict[str, Any]]:
        """Get statistics for all tables.

        Returns:
            dict: Table row counts and sizes
        """
        stats = {}

        try:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            with engine.connect() as connection:
                for table_name in table_names:
                    try:
                        # Get row count
                        result = connection.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        )
                        row_count = result.scalar()

                        # Get table size
                        result = connection.execute(
                            text(f"""
                            SELECT
                                ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb,
                                data_length,
                                index_length
                            FROM information_schema.TABLES
                            WHERE table_schema = DATABASE() AND table_name = '{table_name}'
                            """)
                        )

                        size_row = result.first()
                        if size_row:
                            stats[table_name] = {
                                "row_count": row_count,
                                "size_mb": size_row[0],
                                "data_length": size_row[1],
                                "index_length": size_row[2],
                            }
                        else:
                            stats[table_name] = {"row_count": row_count, "error": "Size info unavailable"}

                    except Exception as e:
                        stats[table_name] = {"error": str(e)}

        except Exception as e:
            logger.error(f"Failed to get table stats: {str(e)}")

        return stats

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Perform comprehensive health check.

        Returns:
            dict: Health status and diagnostics
        """
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "checks": {},
        }

        # Connection test
        if DatabaseDiagnostics.test_connection():
            health["checks"]["connection"] = "✓ pass"
        else:
            health["checks"]["connection"] = "✗ fail"
            health["status"] = "unhealthy"

        # Server info
        try:
            server_info = DatabaseDiagnostics.get_server_info()
            if server_info.get("connection_valid"):
                health["checks"]["server_info"] = f"✓ {server_info['version']}"
            else:
                health["checks"]["server_info"] = "✗ unavailable"
                health["status"] = "degraded"
        except Exception as e:
            health["checks"]["server_info"] = f"✗ {str(e)}"

        # Pool status
        try:
            pool_status = DatabaseDiagnostics.get_connection_pool_status()
            health["pool"] = pool_status
            health["checks"]["pool"] = "✓ pass"
        except Exception as e:
            health["checks"]["pool"] = f"✗ {str(e)}"
            health["status"] = "degraded"

        # Table stats
        try:
            table_stats = DatabaseDiagnostics.get_table_stats()
            health["tables"] = table_stats
            health["checks"]["tables"] = f"✓ {len(table_stats)} tables"
        except Exception as e:
            health["checks"]["tables"] = f"✗ {str(e)}"

        return health

    @staticmethod
    def get_diagnostic_report() -> Dict[str, Any]:
        """Generate comprehensive diagnostic report.

        Returns:
            dict: Full diagnostic information
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "connection": DatabaseDiagnostics.test_connection(),
            "server_info": DatabaseDiagnostics.get_server_info(),
            "pool_status": DatabaseDiagnostics.get_connection_pool_status(),
            "database_stats": DatabaseDiagnostics.get_database_stats(),
            "table_stats": DatabaseDiagnostics.get_table_stats(),
            "health": DatabaseDiagnostics.health_check(),
        }


def print_health_report():
    """Print formatted health check report"""
    report = DatabaseDiagnostics.health_check()

    print("\n" + "="*50)
    print("DATABASE HEALTH CHECK")
    print("="*50)
    print(f"Status: {report['status'].upper()}")
    print(f"Timestamp: {report['timestamp']}")
    print("\nChecks:")
    for check_name, result in report['checks'].items():
        print(f"  {check_name}: {result}")

    if 'pool' in report:
        print(f"\nConnection Pool:")
        for key, value in report['pool'].items():
            print(f"  {key}: {value}")

    if 'tables' in report:
        print(f"\nTables ({len(report['tables'])}):")
        for table_name, stats in report['tables'].items():
            if 'error' not in stats:
                print(f"  {table_name}: {stats['row_count']} rows, {stats['size_mb']}MB")
            else:
                print(f"  {table_name}: {stats['error']}")

    print("="*50 + "\n")
