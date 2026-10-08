"""SmartFin Agri: small, reliable agricultural management console.

The application uses SQLite so data survives restarts.  The business layer is
kept independent from input/output to make it reusable by a future web UI.
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


DEFAULT_DATABASE = Path("smartfin.db")
VALID_TRANSACTION_TYPES = {"income", "expense"}


@dataclass(frozen=True)
class Report:
    inventory: dict[str, float]
    income: float
    expenses: float

    @property
    def net_profit(self) -> float:
        return self.income - self.expenses

    @property
    def credit_score(self) -> int:
        """Return a transparent 0-100 score based on recorded activity."""
        total_activity = self.income + self.expenses
        if total_activity <= 0:
            return 0
        profitability = max(0.0, min(1.0, self.net_profit / total_activity))
        activity_points = min(40.0, total_activity / 100_000 * 40)
        return round(profitability * 60 + activity_points)


class SmartFinStore:
    """SQLite-backed store for harvests and financial transactions."""

    def __init__(self, database_path: str | Path = DEFAULT_DATABASE) -> None:
        self.database_path = Path(database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                crop TEXT PRIMARY KEY COLLATE NOCASE,
                quantity_kg REAL NOT NULL CHECK (quantity_kg >= 0)
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL CHECK (
                    transaction_type IN ('income', 'expense')
                ),
                amount_fcfa REAL NOT NULL CHECK (amount_fcfa > 0),
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def add_harvest(self, crop: str, quantity_kg: float) -> None:
        crop = crop.strip().title()
        if not crop:
            raise ValueError("Le nom de la culture est obligatoire.")
        if quantity_kg <= 0:
            raise ValueError("La quantité doit être supérieure à zéro.")
        self.connection.execute(
            """
            INSERT INTO inventory (crop, quantity_kg) VALUES (?, ?)
            ON CONFLICT(crop) DO UPDATE SET quantity_kg = quantity_kg + excluded.quantity_kg
            """,
            (crop, quantity_kg),
        )
        self.connection.commit()

    def add_transaction(
        self, transaction_type: str, amount_fcfa: float, description: str = ""
    ) -> None:
        transaction_type = transaction_type.strip().lower()
        if transaction_type not in VALID_TRANSACTION_TYPES:
            raise ValueError("Le type doit être 'income' ou 'expense'.")
        if amount_fcfa <= 0:
            raise ValueError("Le montant doit être supérieur à zéro.")
        self.connection.execute(
            """
            INSERT INTO transactions
                (transaction_type, amount_fcfa, description, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                transaction_type,
                amount_fcfa,
                description.strip(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        self.connection.commit()

    def report(self) -> Report:
        inventory_rows = self.connection.execute(
            "SELECT crop, quantity_kg FROM inventory ORDER BY crop"
        ).fetchall()
        totals = self.connection.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN transaction_type = 'income'
                    THEN amount_fcfa ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE WHEN transaction_type = 'expense'
                    THEN amount_fcfa ELSE 0 END), 0) AS expenses
            FROM transactions
            """
        ).fetchone()
        return Report(
            inventory={row["crop"]: row["quantity_kg"] for row in inventory_rows},
            income=float(totals["income"]),
            expenses=float(totals["expenses"]),
        )

    def transactions(self, limit: int = 50) -> list[dict[str, object]]:
        """Return the most recent transactions for dashboards and exports."""
        if limit <= 0:
            raise ValueError("La limite doit être supérieure à zéro.")
        rows = self.connection.execute(
            """
            SELECT transaction_type, amount_fcfa, description, created_at
            FROM transactions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def format_report(report: Report) -> str:
    lines = ["\n" + "=" * 48, "📊 RAPPORT SMARTFIN", "=" * 48, "\n📦 STOCK"]
    if report.inventory:
        lines.extend(
            f"- {crop}: {quantity:g} kg"
            for crop, quantity in report.inventory.items()
        )
    else:
        lines.append("- Aucun stock enregistré.")
    lines.extend(
        [
            "\n💰 FINANCES",
            f"- Revenus : {report.income:,.0f} FCFA",
            f"- Dépenses : {report.expenses:,.0f} FCFA",
            f"- Résultat net : {report.net_profit:,.0f} FCFA",
            f"- Score de crédibilité : {report.credit_score}/100",
            "=" * 48,
        ]
    )
    return "\n".join(lines)


def read_positive_number(prompt: str, input_fn: Callable[[str], str] = input) -> float:
    raw_value = input_fn(prompt).strip().replace(",", ".")
    try:
        value = float(raw_value)
    except ValueError as error:
        raise ValueError("Veuillez saisir un nombre valide.") from error
    if value <= 0:
        raise ValueError("La valeur doit être supérieure à zéro.")
    return value


def display_menu() -> None:
    print(
        "\n" + "=" * 48 + "\n"
        "🌾 SMARTFIN AGRI - GESTION D'EXPLOITATION\n"
        + "=" * 48
        + "\n1. Ajouter une récolte\n"
        "2. Enregistrer une transaction\n"
        "3. Afficher le rapport\n"
        "4. Quitter\n"
        + "=" * 48
    )


def run_console(store: SmartFinStore, input_fn: Callable[[str], str] = input) -> None:
    while True:
        display_menu()
        try:
            choice = input_fn("Votre choix (1-4) : ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFermeture de SmartFin.")
            return
        try:
            if choice == "1":
                crop = input_fn("Nom de la culture : ")
                quantity = read_positive_number("Quantité récoltée (kg) : ", input_fn)
                store.add_harvest(crop, quantity)
                print("✅ Récolte enregistrée.")
            elif choice == "2":
                kind = input_fn("Type (A = revenu, B = dépense) : ").strip().upper()
                transaction_type = {"A": "income", "B": "expense"}.get(kind)
                if transaction_type is None:
                    raise ValueError("Choix invalide : utilisez A ou B.")
                amount = read_positive_number("Montant (FCFA) : ", input_fn)
                description = input_fn("Description (optionnelle) : ")
                store.add_transaction(transaction_type, amount, description)
                print("✅ Transaction enregistrée.")
            elif choice == "3":
                print(format_report(store.report()))
            elif choice == "4":
                print("Merci d'avoir utilisé SmartFin. À bientôt !")
                return
            else:
                print("❌ Choix invalide. Utilisez 1, 2, 3 ou 4.")
        except ValueError as error:
            print(f"❌ {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gestion agricole SmartFin")
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help="Chemin de la base SQLite (défaut: smartfin.db)",
    )
    args = parser.parse_args()
    store = SmartFinStore(args.database)
    try:
        run_console(store)
    finally:
        store.close()


if __name__ == "__main__":
    main()
