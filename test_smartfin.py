import tempfile
import unittest
from pathlib import Path

from SmartFin_Console_Agricultural import SmartFinStore


class SmartFinStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "test.db"
        self.store = SmartFinStore(self.database)

    def tearDown(self) -> None:
        self.store.close()
        self.temp_dir.cleanup()

    def test_harvests_are_accumulated_and_persisted(self) -> None:
        self.store.add_harvest("oignons", 12)
        self.store.add_harvest("OIGNONS", 8.5)
        self.store.close()

        reopened = SmartFinStore(self.database)
        self.assertEqual(reopened.report().inventory, {"Oignons": 20.5})
        reopened.close()

    def test_report_calculates_profit_and_score(self) -> None:
        self.store.add_transaction("income", 100_000, "Vente")
        self.store.add_transaction("expense", 25_000, "Semences")

        report = self.store.report()

        self.assertEqual(report.net_profit, 75_000)
        self.assertEqual(report.credit_score, 76)

    def test_invalid_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.add_harvest("Maïs", 0)
        with self.assertRaises(ValueError):
            self.store.add_transaction("income", -1)
        with self.assertRaises(ValueError):
            self.store.add_transaction("loan", 100)


if __name__ == "__main__":
    unittest.main()
