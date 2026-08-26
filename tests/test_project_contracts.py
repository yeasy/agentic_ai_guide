from __future__ import annotations

import re
import tempfile
import unittest
from datetime import date
from pathlib import Path

import check_project_rules as rules


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "12_appendix" / "12.5_volatile_facts.md"


def check_volatile(testcase: unittest.TestCase, path: Path, today: date) -> list[str]:
    testcase.assertTrue(
        hasattr(rules, "check_volatile_facts"),
        "check_project_rules.py must define check_volatile_facts()",
    )
    return rules.check_volatile_facts(path, today)


class VolatileFactsTests(unittest.TestCase):
    def write_ledger(
        self,
        directory: str,
        *,
        verified: str = "2026-07-10",
        expires: str = "2026-08-09",
        ttl: int = 30,
        status: str = "current",
    ) -> Path:
        path = Path(directory) / "facts.md"
        path.write_text(
            "# Facts\n\n"
            f"> `verified_at`: {verified} · `expires_at`: {expires} · `ttl_days`: {ttl}\n\n"
            f"<!-- volatile-status: id=models status={status} -->\n",
            encoding="utf-8",
        )
        return path

    def test_fresh_30_day_ledger_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_ledger(directory)
            self.assertEqual(check_volatile(self, path, date(2026, 7, 20)), [])

    def test_expired_ledger_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_ledger(directory)
            issues = check_volatile(self, path, date(2026, 8, 10))
            self.assertTrue(any("expired" in issue for issue in issues), issues)

    def test_verification_date_cannot_be_in_the_future(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_ledger(
                directory, verified="2026-07-11", expires="2026-08-10"
            )
            issues = check_volatile(self, path, date(2026, 7, 10))
            self.assertTrue(any("future" in issue for issue in issues), issues)

    def test_expiry_cannot_precede_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_ledger(
                directory, verified="2026-07-10", expires="2026-07-09"
            )
            issues = check_volatile(self, path, date(2026, 7, 10))
            self.assertTrue(any("after verified_at" in issue for issue in issues), issues)

    def test_verification_and_expiry_boundaries_are_inclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_ledger(directory)
            self.assertEqual(check_volatile(self, path, date(2026, 7, 10)), [])
            self.assertEqual(check_volatile(self, path, date(2026, 8, 9)), [])
            issues = check_volatile(self, path, date(2026, 8, 10))
            self.assertTrue(any("expired" in issue for issue in issues), issues)

    def test_ttl_metadata_must_describe_exactly_30_days(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_ledger(directory, expires="2026-09-08", ttl=60)
            issues = check_volatile(self, path, date(2026, 7, 10))
            self.assertTrue(any("30 days" in issue for issue in issues), issues)

    def test_open_conflict_fails_closed_but_resolved_conflict_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            open_path = self.write_ledger(directory, status="open-conflict")
            issues = check_volatile(self, open_path, date(2026, 7, 10))
            self.assertTrue(any("unresolved conflict" in issue for issue in issues), issues)

            resolved_path = self.write_ledger(directory, status="resolved-conflict")
            self.assertEqual(
                check_volatile(self, resolved_path, date(2026, 7, 10)), []
            )

    def test_repository_ledger_records_current_official_model_status(self):
        text = LEDGER.read_text(encoding="utf-8")
        # Assert the SHAPE of the header rather than the literal dates. Pinning
        # them here guarantees that every honest re-verification — the one thing
        # the 30-day TTL exists to force — also breaks this test. The date
        # arithmetic is enforced by check_volatile_facts() against the ledger's
        # own verified_at, so it does not need a second copy here.
        self.assertRegex(
            text,
            r"`verified_at`: \d{4}-\d{2}-\d{2} · "
            r"`expires_at`: \d{4}-\d{2}-\d{2} · `ttl_days`: 30",
        )
        required = (
            "status=resolved-conflict",
            "GPT-5.6",
            "GPT-5.3-Codex",
            "Fable 5 已于 2026-07-01 恢复全球访问",
            "Mythos 5 非普遍可用，仅限 Project Glasswing 获批客户",
            "2026-07-01 的恢复公告记录当时先恢复给一组美国机构",
            "Claude Sonnet 5",
            "`claude-sonnet-5`",
            "`claude-opus-5`",
            "Gemini 3.5 Flash",
            "https://www.anthropic.com/news/redeploying-fable-5",
            "https://www.anthropic.com/news/claude-sonnet-5",
            "https://developers.openai.com/api/docs/models/all",
            "https://ai.google.dev/gemini-api/docs/models",
        )
        for marker in required:
            self.assertIn(marker, text)
        # Check the real ledger as of its OWN verified_at, not a hardcoded date.
        # This line used to pin 2026-07-10, so every honest ledger refresh failed
        # here with "verified_at is in the future" — a third date pin hiding behind
        # the two in the marker list above. The synthetic fixtures below keep their
        # own fixed dates on purpose; those exercise the checker, not the ledger.
        stamped = re.search(r"`verified_at`:\s*(\d{4})-(\d{2})-(\d{2})", text)
        self.assertIsNotNone(stamped, "ledger header must carry verified_at")
        self.assertEqual(
            check_volatile(self, LEDGER, date(*(int(g) for g in stamped.groups()))), []
        )

    def test_main_checker_enforces_volatile_facts(self):
        source = (ROOT / "check_project_rules.py").read_text(encoding="utf-8")
        self.assertIn("issues.extend(check_volatile_facts())", source)


class ExecutiveRouteTests(unittest.TestCase):
    def test_readme_has_a_testable_five_stop_executive_route(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 高管决策路线", text)
        expected = (
            "09_agentops/9.9_autonomy_metrics.md",
            "09_agentops/9.4_optimization.md",
            "09_agentops/9.5_enterprise.md",
            "04_tools/4.7_agentic_ux.md",
            "11_future/11.2_alignment.md",
        )
        positions = []
        for path in expected:
            self.assertIn(path, text)
            positions.append(text.index(path))
        self.assertEqual(positions, sorted(positions))

    def test_readme_routes_fast_changing_claims_to_the_ledger(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("12_appendix/12.5_volatile_facts.md", text)
        self.assertIn("30 天", text)


if __name__ == "__main__":
    unittest.main()
