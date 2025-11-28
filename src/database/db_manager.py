import duckdb
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for IP reputation checking"""
    
    def __init__(self, db_path: str = "ip_reputation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        with duckdb.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS ip_reputation (
                ip TEXT PRIMARY KEY,
                reputation TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            conn.execute("""
            CREATE TABLE IF NOT EXISTS ip_analysis (
                ip TEXT,
                quality_score INTEGER,
                is_valid BOOLEAN,
                is_private BOOLEAN,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ip, analyzed_at)
            )
            """)

            logger.info(f"Database initialized at {self.db_path}")
    
    def get_reputation(self, ip: str) -> Optional[str]:
        """Get stored reputation for an IP address"""
        with duckdb.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT reputation FROM ip_reputation WHERE ip = ?", [ip]
            ).fetchone()
            
            return result[0] if result else None
    
    def store_reputation(self, ip: str, reputation: str):
        """Store or update IP reputation in database"""
        with duckdb.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO ip_reputation (ip, reputation, checked_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                [ip, reputation]
            )
            conn.commit()
            
            logger.info(f"Stored reputation for IP {ip}: {reputation}")
    
    def is_bad_ip(self, ip: str) -> bool:
        """Check if IP has BAD reputation in database"""
        reputation = self.get_reputation(ip)
        return reputation == "BAD"
    
    def store_analysis(self, ip: str, quality_score: int, is_valid: bool, is_private: bool):
        """Store IP analysis results in database"""
        with duckdb.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO ip_analysis (ip, quality_score, is_valid, is_private, analyzed_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                [ip, quality_score, is_valid, is_private]
            )
            conn.commit()
            
            logger.info(f"Stored analysis for IP {ip}")
    
    def get_analysis_history(self, ip: str) -> list:
        """Get analysis history for an IP address"""
        with duckdb.connect(self.db_path) as conn:
            results = conn.execute(
                """
                SELECT quality_score, is_valid, is_private, analyzed_at
                FROM ip_analysis
                WHERE ip = ?
                ORDER BY analyzed_at DESC
                """,
                [ip]
            ).fetchall()
            
            return results