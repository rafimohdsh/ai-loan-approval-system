"""Database schema utilities and helper functions"""

import logging
from datetime import datetime
from sqlalchemy import text
from ..database.connection import 
logger = logging.getLogger(__name__)


def get_schema_info() -> dict:
    """Get database schema information"""
    schema_info = {
        "customers": {
            "description": "Stores customer/applicant information",
            "primary_key": "id",
            "unique_fields": ["customer_id", "email", "ssn"],
            "indexes": ["customer_id", "email", "phone", "ssn"],
        },
        "loan_applications": {
            "description": "Loan application records with applicant financial data",
            "primary_key": "id",
            "unique_fields": ["application_id"],
            "indexes": ["application_id", "applicant_email", "status"],
        },
        "loan_decisions": {
            "description": "Loan approval/rejection decisions with risk analysis",
            "primary_key": "id",
            "unique_fields": ["decision_id"],
            "indexes": ["decision_id", "loan_application_id", "decision_status", "risk_score"],
        },
        "audit_logs": {
            "description": "Complete audit trail of all system actions",
            "primary_key": "id",
            "unique_fields": ["audit_id"],
            "indexes": ["audit_id", "entity_type", "entity_id", "user_id", "timestamp"],
        }
    }
    return schema_info


def verify_schema() -> bool:
    """Verify database schema matches expected structure"""
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(
                text("""
                SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                """)
            )
            existing_tables = {row[0] for row in result}

            required_tables = {"customers", "loan_applications", "loan_decisions", "audit_logs"}
            missing_tables = required_tables - existing_tables

            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                return False

            logger.info(f"Schema verification successful. Found tables: {existing_tables}")
            return True
    except Exception as e:
        logger.error(f"Schema verification failed: {str(e)}")
        return False


def get_table_statistics() -> dict:
    """Get row count and size information for all tables"""
    stats = {}
    tables = ["customers", "loan_applications", "loan_decisions", "audit_logs"]

    try:
        with engine.connect() as conn:
            for table in tables:
                try:
                    # Get row count
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    row_count = result.scalar()

                    # Get table size
                    size_result = conn.execute(
                        text(f"""
                        SELECT
                            ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
                        FROM information_schema.TABLES
                        WHERE table_schema = DATABASE() AND table_name = '{table}'
                        """)
                    )
                    size_row = size_result.fetchone()
                    size_mb = size_row[0] if size_row else 0

                    stats[table] = {
                        "row_count": row_count,
                        "size_mb": size_mb,
                    }
                except Exception as e:
                    logger.warning(f"Could not get stats for {table}: {str(e)}")
                    stats[table] = {"error": str(e)}

    except Exception as e:
        logger.error(f"Failed to get table statistics: {str(e)}")

    return stats


def backup_table(table_name: str) -> str:
    """Create a backup of a table"""
    backup_table_name = f"{table_name}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}"))
            conn.commit()
            logger.info(f"Backup created: {backup_table_name}")
            return backup_table_name
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        raise


def health_check() -> dict:
    """Perform database health check"""
    health = {
        "status": "healthy",
        "checks": {},
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        with engine.connect() as conn:
            # Test connection
            result = conn.execute(text("SELECT 1"))
            health["checks"]["connection"] = "ok"

            # Check schema
            health["checks"]["schema"] = "ok" if verify_schema() else "failed"

            # Get statistics
            stats = get_table_statistics()
            health["checks"]["statistics"] = stats

            # Overall status
            if any(check == "failed" for check in health["checks"].values() if isinstance(check, str)):
                health["status"] = "degraded"

    except Exception as e:
        health["status"] = "unhealthy"
        health["error"] = str(e)
        logger.error(f"Health check failed: {str(e)}")

    return health


def cleanup_old_audit_logs(days: int = 90) -> int:
    """Delete audit logs older than specified days. Returns count of deleted records."""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(f"""
                DELETE FROM audit_logs
                WHERE timestamp < DATE_SUB(NOW(), INTERVAL {days} DAY)
                """)
            )
            conn.commit()
            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} audit logs older than {days} days")
            return deleted_count
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise


def create_indexes() -> None:
    """Ensure all recommended indexes are created"""
    indexes = [
        ("customers", "idx_customer_email_phone", ["email", "phone"]),
        ("customers", "idx_customer_ssn_name", ["ssn", "first_name", "last_name"]),
        ("loan_applications", "idx_app_email_status", ["applicant_email", "status"]),
        ("loan_applications", "idx_app_created_at", ["created_at"]),
        ("loan_decisions", "idx_decision_app_id", ["loan_application_id"]),
        ("loan_decisions", "idx_decision_status", ["decision_status"]),
        ("loan_decisions", "idx_decision_risk_score", ["risk_score"]),
        ("audit_logs", "idx_audit_entity", ["entity_type", "entity_id"]),
        ("audit_logs", "idx_audit_user_timestamp", ["user_id", "timestamp"]),
        ("audit_logs", "idx_audit_action_timestamp", ["action_type", "timestamp"]),
        ("audit_logs", "idx_audit_timestamp", ["timestamp"]),
    ]

    try:
        with engine.connect() as conn:
            for table, index_name, columns in indexes:
                columns_str = ", ".join(columns)
                try:
                    conn.execute(
                        text(f"""
                        CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({columns_str})
                        """)
                    )
                    logger.debug(f"Index {index_name} created/verified on {table}")
                except Exception as e:
                    logger.warning(f"Could not create index {index_name}: {str(e)}")
            conn.commit()
    except Exception as e:
        logger.error(f"Index creation failed: {str(e)}")
        raise
