"""
SQLite Storage Engine for Tracking WorldQuant Brain Alphas, Backtests, and Daily Goals.
"""

import sqlite3
import datetime
import os
from typing import List, Dict, Any, Optional
from config import DB_PATH, MIN_SHARPE, MIN_FITNESS, MAX_TURNOVER, MIN_TURNOVER

class AlphaDatabase:
    """Manages persistent tracking of all candidate, simulated, and submitted alphas."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Alphas master table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alphas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                formula TEXT UNIQUE NOT NULL,
                category TEXT NOT NULL,
                region TEXT DEFAULT 'USA',
                universe TEXT DEFAULT 'TOP3000',
                decay INTEGER DEFAULT 5,
                neutralization TEXT DEFAULT 'SUBINDUSTRY',
                truncation REAL DEFAULT 0.08,
                status TEXT DEFAULT 'draft',
                sharpe REAL,
                turnover REAL,
                fitness REAL,
                returns REAL,
                margin_bps REAL,
                max_drawdown REAL,
                sub_universe_passed INTEGER DEFAULT 0,
                brain_sim_id TEXT,
                brain_alpha_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                simulated_at TIMESTAMP,
                submitted_at TIMESTAMP,
                notes TEXT
            );
            """)

            # Daily targets and quotas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_goals (
                date TEXT PRIMARY KEY,
                target_simulations INTEGER DEFAULT 15,
                target_submissions INTEGER DEFAULT 3,
                simulations_done INTEGER DEFAULT 0,
                submissions_done INTEGER DEFAULT 0
            );
            """)

            conn.commit()

    def save_alpha(self, data: Dict[str, Any]) -> int:
        """Insert or update an alpha record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO alphas (
                name, formula, category, region, universe, decay,
                neutralization, truncation, status, notes
            ) VALUES (
                :name, :formula, :category, :region, :universe, :decay,
                :neutralization, :truncation, :status, :notes
            )
            ON CONFLICT(formula) DO UPDATE SET
                name = excluded.name,
                category = excluded.category,
                notes = COALESCE(excluded.notes, alphas.notes)
            """, {
                "name": data.get("name", "Untitled Alpha"),
                "formula": data["formula"].strip(),
                "category": data.get("category", "Uncategorized"),
                "region": data.get("region", "USA"),
                "universe": data.get("universe", "TOP3000"),
                "decay": data.get("decay", 5),
                "neutralization": data.get("neutralization", "SUBINDUSTRY"),
                "truncation": data.get("truncation", 0.08),
                "status": data.get("status", "draft"),
                "notes": data.get("notes", "")
            })
            conn.commit()
            return cursor.lastrowid

    def update_simulation_result(self, alpha_id: int, sim_metrics: Dict[str, Any]):
        """Record backtest simulation results for an alpha."""
        sharpe = sim_metrics.get("sharpe")
        turnover = sim_metrics.get("turnover")
        fitness = sim_metrics.get("fitness")
        returns = sim_metrics.get("returns")
        margin = sim_metrics.get("margin_bps")
        dd = sim_metrics.get("max_drawdown")
        sub_pass = 1 if sim_metrics.get("sub_universe_passed") else 0
        brain_alpha_id = sim_metrics.get("brain_alpha_id")
        brain_sim_id = sim_metrics.get("brain_sim_id")

        # Determine automatic status check
        status = "simulated"
        if sharpe is not None and turnover is not None and fitness is not None:
            if (sharpe >= MIN_SHARPE and 
                fitness >= MIN_FITNESS and 
                MIN_TURNOVER <= turnover <= MAX_TURNOVER):
                status = "passed"
            else:
                status = "rejected"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE alphas SET
                sharpe = :sharpe,
                turnover = :turnover,
                fitness = :fitness,
                returns = :returns,
                margin_bps = :margin_bps,
                max_drawdown = :max_drawdown,
                sub_universe_passed = :sub_universe_passed,
                brain_sim_id = :brain_sim_id,
                brain_alpha_id = :brain_alpha_id,
                status = :status,
                simulated_at = CURRENT_TIMESTAMP
            WHERE id = :id
            """, {
                "id": alpha_id,
                "sharpe": sharpe,
                "turnover": turnover,
                "fitness": fitness,
                "returns": returns,
                "margin_bps": margin,
                "max_drawdown": dd,
                "sub_universe_passed": sub_pass,
                "brain_sim_id": brain_sim_id,
                "brain_alpha_id": brain_alpha_id,
                "status": status
            })
            
            # Increment daily simulation counter
            today = datetime.date.today().isoformat()
            cursor.execute("""
            INSERT INTO daily_goals (date, simulations_done)
            VALUES (:today, 1)
            ON CONFLICT(date) DO UPDATE SET
                simulations_done = simulations_done + 1
            """, {"today": today})

            conn.commit()

    def mark_submitted(self, alpha_id: int):
        """Mark an alpha as submitted to WorldQuant Brain."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE alphas SET
                status = 'submitted',
                submitted_at = CURRENT_TIMESTAMP
            WHERE id = :id
            """, {"id": alpha_id})

            today = datetime.date.today().isoformat()
            cursor.execute("""
            INSERT INTO daily_goals (date, submissions_done)
            VALUES (:today, 1)
            ON CONFLICT(date) DO UPDATE SET
                submissions_done = submissions_done + 1
            """, {"today": today})

            conn.commit()

    def get_alphas(self, status: Optional[str] = None, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Query alphas with optional filtering."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM alphas WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            if category:
                query += " AND category = ?"
                params.append(category)
                
            query += " ORDER BY id DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_alpha_by_id(self, alpha_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single alpha by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alphas WHERE id = ?", (alpha_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_daily_stats(self) -> Dict[str, Any]:
        """Get today's targets and progress."""
        today = datetime.date.today().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM daily_goals WHERE date = ?", (today,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                INSERT INTO daily_goals (date, target_simulations, target_submissions, simulations_done, submissions_done)
                VALUES (?, 15, 3, 0, 0)
                """, (today,))
                conn.commit()
                return {
                    "date": today,
                    "target_simulations": 15,
                    "target_submissions": 3,
                    "simulations_done": 0,
                    "submissions_done": 0
                }
            return dict(row)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get aggregate counts across all statuses."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, count(*) as count FROM alphas GROUP BY status")
            counts = {row["status"]: row["count"] for row in cursor.fetchall()}
            
            cursor.execute("SELECT count(*) as total, avg(sharpe) as avg_sharpe, avg(fitness) as avg_fitness FROM alphas WHERE status IN ('passed', 'submitted')")
            top_row = cursor.fetchone()
            
            return {
                "status_counts": counts,
                "total_passed_or_submitted": top_row["total"] if top_row else 0,
                "avg_sharpe_passed": round(top_row["avg_sharpe"], 2) if top_row and top_row["avg_sharpe"] else 0.0,
                "avg_fitness_passed": round(top_row["avg_fitness"], 2) if top_row and top_row["avg_fitness"] else 0.0
            }

