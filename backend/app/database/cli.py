"""CLI commands for database operations"""

import click
import logging
from ..database import     init_db,
    check_db_connection,
    get_db_tables,
    drop_all_tables,
    DatabaseService,
    SessionLocal,
)
from ..database.migrations import     get_schema_info,
    verify_schema,
    get_table_statistics,
    health_check,
    backup_table,
    cleanup_old_audit_logs,
    create_indexes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def db_cli():
    """Database management commands"""
    pass


@db_cli.command()
def init():
    """Initialize the database and create all tables"""
    click.echo("Initializing database...")
    try:
        init_db()
        create_indexes()
        click.echo(click.style("✓ Database initialized successfully", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Failed to initialize database: {str(e)}", fg="red"))
        raise


@db_cli.command()
def test_connection():
    """Test database connection"""
    click.echo("Testing database connection...")
    if check_db_connection():
        click.echo(click.style("✓ Database connection successful", fg="green"))
    else:
        click.echo(click.style("✗ Database connection failed", fg="red"))


@db_cli.command()
def status():
    """Check database health status"""
    click.echo("Checking database health...")
    result = health_check()
    click.echo(f"Status: {click.style(result['status'], fg='green' if result['status'] == 'healthy' else 'red')}")
    click.echo(f"Timestamp: {result['timestamp']}")
    click.echo("\nChecks:")
    for check, value in result["checks"].items():
        if isinstance(value, str):
            color = "green" if value == "ok" else "red"
            click.echo(f"  {check}: {click.style(value, fg=color)}")
        else:
            click.echo(f"  {check}: {value}")


@db_cli.command()
def schema_info():
    """Display database schema information"""
    click.echo("Database Schema Information:\n")
    info = get_schema_info()
    for table, details in info.items():
        click.echo(f"Table: {table}")
        for key, value in details.items():
            if isinstance(value, list):
                click.echo(f"  {key}: {', '.join(value)}")
            else:
                click.echo(f"  {key}: {value}")
        click.echo()


@db_cli.command()
def verify():
    """Verify database schema"""
    click.echo("Verifying database schema...")
    if verify_schema():
        click.echo(click.style("✓ Schema verification passed", fg="green"))
    else:
        click.echo(click.style("✗ Schema verification failed", fg="red"))


@db_cli.command()
def stats():
    """Display table statistics"""
    click.echo("Table Statistics:\n")
    stats = get_table_statistics()
    for table, data in stats.items():
        click.echo(f"Table: {table}")
        if "error" in data:
            click.echo(f"  Error: {data['error']}")
        else:
            click.echo(f"  Rows: {data['row_count']}")
            click.echo(f"  Size: {data['size_mb']} MB")
        click.echo()


@db_cli.command()
def tables():
    """List all database tables"""
    click.echo("Database Tables:")
    tables = get_db_tables()
    for i, table in enumerate(tables, 1):
        click.echo(f"  {i}. {table}")


@db_cli.command()
@click.option("--table", required=True, help="Table name to backup")
def backup(table):
    """Backup a table"""
    click.echo(f"Backing up table: {table}...")
    try:
        backup_name = backup_table(table)
        click.echo(click.style(f"✓ Backup created: {backup_name}", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Backup failed: {str(e)}", fg="red"))


@db_cli.command()
@click.option("--days", default=90, help="Delete logs older than N days")
def cleanup_audit_logs(days):
    """Clean up old audit logs"""
    click.echo(f"Cleaning up audit logs older than {days} days...")
    try:
        deleted = cleanup_old_audit_logs(days)
        click.echo(click.style(f"✓ Deleted {deleted} audit logs", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Cleanup failed: {str(e)}", fg="red"))


@db_cli.command()
def create_indexes_cmd():
    """Create all recommended indexes"""
    click.echo("Creating indexes...")
    try:
        create_indexes()
        click.echo(click.style("✓ Indexes created successfully", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Index creation failed: {str(e)}", fg="red"))


@db_cli.command()
@click.confirmation_option(prompt="Are you sure? This will drop all tables!")
def drop_all():
    """Drop all tables from the database"""
    click.echo("Dropping all tables...")
    try:
        drop_all_tables()
        click.echo(click.style("✓ All tables dropped", fg="green"))
    except Exception as e:
        click.echo(click.style(f"✗ Drop failed: {str(e)}", fg="red"))


@db_cli.command()
def reset():
    """Reset database (drop all tables and recreate)"""
    if click.confirm("This will drop all tables and recreate them. Continue?"):
        click.echo("Resetting database...")
        try:
            drop_all_tables()
            click.echo("Dropping complete. Recreating tables...")
            init_db()
            create_indexes()
            click.echo(click.style("✓ Database reset successfully", fg="green"))
        except Exception as e:
            click.echo(click.style(f"✗ Reset failed: {str(e)}", fg="red"))


if __name__ == "__main__":
    db_cli()
