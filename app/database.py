from __future__ import annotations

import sqlite3
from pathlib import Path


class SettingsRepository:
    """
    Handles the SQLite database used to store clock customization settings.
    """

    def __init__(self, database_path: str = "data/clock_settings.db") -> None:
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)

        self._create_settings_table()
        self._insert_default_settings()
        self._migrate_legacy_settings()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    def _create_settings_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def _insert_default_settings(self) -> None:
        default_settings = {
            "user_name": "Estudiante",
            "accent_color": "#EC4899",
            "show_seconds": "1",
            "reminder_enabled": "1",
            "reminder_time": "07:00",
            "reminder_message": "Hora de estudiar estructuras de datos"
        }

        with self._connect() as connection:
            for key, value in default_settings.items():
                connection.execute(
                    """
                    INSERT OR IGNORE INTO app_settings (setting_key, setting_value)
                    VALUES (?, ?)
                    """,
                    (key, value)
                )

            connection.commit()

    def _migrate_legacy_settings(self) -> None:
        """
        Updates the old professional blue default to the new girly pink default.
        This helps if the database was already created before the visual redesign.
        """
        current_color = self.get_setting("accent_color", "#EC4899")

        if current_color == "#2563EB":
            self.save_setting("accent_color", "#EC4899")

    def get_setting(self, key: str, default_value: str = "") -> str:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT setting_value
                FROM app_settings
                WHERE setting_key = ?
                """,
                (key,)
            )

            row = cursor.fetchone()

            if row is None:
                return default_value

            return str(row[0])

    def save_setting(self, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO app_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_key)
                DO UPDATE SET setting_value = excluded.setting_value
                """,
                (key, value)
            )
            connection.commit()

    def load_all_settings(self) -> dict[str, str]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT setting_key, setting_value
                FROM app_settings
                """
            )

            return {key: value for key, value in cursor.fetchall()}