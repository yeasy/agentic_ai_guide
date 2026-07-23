from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
FULL_ACTION_SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
EXPECTED_WORKFLOWS = (
    "ci.yaml",
    "preview-pdf.yml",
    "auto-release.yml",
    "dependabot-automerge.yml",
)
TEST_REPOSITORY = "owner/repo"
TEST_SHA = "a" * 40
GET_REF_COMMAND = [
    "api",
    "--include",
    "--method",
    "GET",
    f"repos/{TEST_REPOSITORY}/git/ref/tags/preview-pdf",
]
PATCH_REF_COMMAND = [
    "api",
    "--silent",
    "--method",
    "PATCH",
    f"repos/{TEST_REPOSITORY}/git/refs/tags/preview-pdf",
    "--raw-field",
    f"sha={TEST_SHA}",
    "--field",
    "force=true",
]
POST_REF_COMMAND = [
    "api",
    "--silent",
    "--method",
    "POST",
    f"repos/{TEST_REPOSITORY}/git/refs",
    "--raw-field",
    "ref=refs/tags/preview-pdf",
    "--raw-field",
    f"sha={TEST_SHA}",
]
VIEW_RELEASE_COMMAND = ["release", "view", "preview-pdf"]
EDIT_RELEASE_COMMAND = [
    "release",
    "edit",
    "preview-pdf",
    "--title",
    "Latest Preview Publications",
    "--notes-file",
    "dist/release-notes.md",
    "--prerelease",
]
CREATE_RELEASE_COMMAND = [
    "release",
    "create",
    "preview-pdf",
    "--title",
    "Latest Preview Publications",
    "--notes-file",
    "dist/release-notes.md",
    "--prerelease",
    "--latest=false",
    "--verify-tag",
]
UPLOAD_RELEASE_COMMAND = [
    "release",
    "upload",
    "preview-pdf",
    "dist/agentic_ai_guide.pdf",
    "dist/agentic_ai_guide.html",
    "dist/SHA256SUMS",
    "--clobber",
]
PREVIEW_MUTATION_STEPS = (
    "Synchronize mutable preview tag",
    "Create or update preview release",
    "Replace preview assets",
)


FAKE_GH = r'''#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["GH_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(args) + "\n")

scenario = os.environ["GH_SCENARIO"]
repository = "owner/repo"
sha = "a" * 40
reasons = {
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "429": "Too Many Requests",
    "503": "Service Unavailable",
}

def fail_http(code):
    print(f"HTTP/2.0 {code} {reasons[code]}")
    print(f"fake gh HTTP {code}", file=sys.stderr)
    raise SystemExit(1)

get_ref = ["api", "--include", "--method", "GET", f"repos/{repository}/git/ref/tags/preview-pdf"]
patch_ref = [
    "api", "--silent", "--method", "PATCH",
    f"repos/{repository}/git/refs/tags/preview-pdf",
    "--raw-field", f"sha={sha}", "--field", "force=true",
]
post_ref = [
    "api", "--silent", "--method", "POST", f"repos/{repository}/git/refs",
    "--raw-field", "ref=refs/tags/preview-pdf", "--raw-field", f"sha={sha}",
]
view_release = ["release", "view", "preview-pdf"]
edit_release = [
    "release", "edit", "preview-pdf", "--title", "Latest Preview Publications",
    "--notes-file", "dist/release-notes.md", "--prerelease",
]
create_release = [
    "release", "create", "preview-pdf", "--title", "Latest Preview Publications",
    "--notes-file", "dist/release-notes.md", "--prerelease",
    "--latest=false", "--verify-tag",
]
upload_release = [
    "release", "upload", "preview-pdf", "dist/agentic_ai_guide.pdf",
    "dist/agentic_ai_guide.html", "dist/SHA256SUMS", "--clobber",
]

if os.environ.get("GH_REPO") != repository:
    print("fake gh requires explicit GH_REPO", file=sys.stderr)
    raise SystemExit(2)

if args == get_ref:
    if scenario == "ref_404_exit2":
        print("HTTP/2.0 404 Not Found")
        print("fake gh HTTP 404 with unexpected exit", file=sys.stderr)
        raise SystemExit(2)
    if scenario == "ref_404_exit0":
        print("HTTP/2.0 404 Not Found")
        raise SystemExit(0)
    if scenario.startswith("ref_network"):
        print("fake gh network failure", file=sys.stderr)
        raise SystemExit(1)
    for code in reasons:
        if scenario.startswith(f"ref_{code}"):
            fail_http(code)
    print("HTTP/2.0 200 OK")
    print('Content-Type: application/json\n\n{"ref":"refs/tags/preview-pdf"}')
    raise SystemExit(0)

if args in (patch_ref, post_ref, edit_release, create_release, upload_release):
    raise SystemExit(0)

if args == view_release:
    if "release_missing_exit2" in scenario:
        print("release not found", file=sys.stderr)
        raise SystemExit(2)
    if "release_missing" in scenario:
        print("release not found", file=sys.stderr)
        raise SystemExit(1)
    if "release_network" in scenario:
        print("fake release network failure", file=sys.stderr)
        raise SystemExit(1)
    for code in reasons:
        if f"release_{code}" in scenario:
            print(f"fake release HTTP {code}", file=sys.stderr)
            raise SystemExit(1)
    raise SystemExit(0)

print(f"unexpected gh argv: {args!r}", file=sys.stderr)
raise SystemExit(2)
'''


def workflow_step_script(workflow_text: str, step_name: str) -> str:
    marker = f"      - name: {step_name}\n"
    start = workflow_text.index(marker) + len(marker)
    run_marker = "        run: |\n"
    script_start = workflow_text.index(run_marker, start) + len(run_marker)
    script_end = workflow_text.find("\n      - name:", script_start)
    if script_end < 0:
        script_end = len(workflow_text)
    return textwrap.dedent(workflow_text[script_start:script_end])


def workflow_job_step_names(workflow_text: str, job_name: str) -> list[str]:
    lines = workflow_text.splitlines()
    job_marker = f"  {job_name}:"
    try:
        job_start = lines.index(job_marker)
    except ValueError:
        return []
    names: list[str] = []
    in_steps = False
    for line in lines[job_start + 1 :]:
        if re.match(r"^  [A-Za-z0-9_-]+:\s*$", line):
            break
        if line == "    steps:":
            in_steps = True
            continue
        if in_steps:
            match = re.match(r"^      - name:\s*(.+?)\s*$", line)
            if match:
                names.append(match.group(1))
    return names


def preview_mutation_step_names(workflow_text: str) -> list[str]:
    return [
        name
        for name in workflow_job_step_names(workflow_text, "publish")
        if name in PREVIEW_MUTATION_STEPS
    ]


class WorkflowSafetyTests(unittest.TestCase):
    def workflow_text(self, name: str) -> str:
        path = WORKFLOW_DIR / name
        self.assertTrue(path.is_file(), path)
        return path.read_text(encoding="utf-8")

    def test_actions_are_immutable_and_checkout_drops_credentials(self):
        failures = []
        for name in EXPECTED_WORKFLOWS:
            text = self.workflow_text(name)
            lines = text.splitlines()
            for number, line in enumerate(lines, 1):
                match = re.search(r"\buses:\s*([^\s#]+)(?:\s+#\s*(\S+))?", line)
                if match:
                    action, version = match.groups()
                    if (
                        not FULL_ACTION_SHA.fullmatch(action)
                        or not version
                        or not version.startswith("v")
                    ):
                        failures.append(f"{name}:{number}: {line.strip()}")
                if "uses: actions/checkout@" in line:
                    step = "\n".join(lines[number - 1 : number + 8])
                    if "persist-credentials: false" not in step:
                        failures.append(f"{name}:{number}: checkout credentials persist")
        self.assertEqual(failures, [])

    def test_permissions_are_default_deny_and_build_publish_are_separated(self):
        for name in EXPECTED_WORKFLOWS:
            self.assertIn("\npermissions: {}\n", self.workflow_text(name), name)

        ci = self.workflow_text("ci.yaml")
        auto = self.workflow_text("auto-release.yml")
        preview = self.workflow_text("preview-pdf.yml")
        self.assertRegex(ci, r"(?ms)^  build:\n    permissions:\n      contents: read\b")
        self.assertRegex(auto, r"(?ms)^  build:\n    permissions:\n      contents: read\b")
        self.assertRegex(
            auto,
            r"(?ms)^  release:.*?permissions:\n      contents: write\n"
            r"      id-token: write\n      attestations: write\b.*?needs: build",
        )
        self.assertRegex(preview, r"(?ms)^  build:\n    permissions:\n      contents: read\b")
        self.assertRegex(
            preview,
            r"(?ms)^  publish:.*?permissions:\n      contents: write\b.*?needs: build",
        )

    def test_downloads_and_artifacts_have_integrity_gates(self):
        for name in ("ci.yaml", "preview-pdf.yml", "auto-release.yml"):
            text = self.workflow_text(name)
            self.assertIn("checksums.txt", text, name)
            self.assertIn("PANDOC_SHA256", text, name)
            self.assertIn("sha256sum -c -", text, name)
            self.assertIn("tools/verify_artifacts.py", text, name)
            self.assertIn("SHA256SUMS", text, name)
            self.assertNotIn("continue-on-error: true", text, name)
        self.assertIn(
            "actions/attest-build-provenance@0f67c3f4856b2e3261c31976d6725780e5e4c373 # v4.1.1",
            self.workflow_text("auto-release.yml"),
        )

    def test_mermaid_dependency_is_exact_and_lockfile_backed(self):
        package_path = ROOT / "tools" / "mermaid" / "package.json"
        lock_path = ROOT / "tools" / "mermaid" / "package-lock.json"
        self.assertTrue(package_path.is_file(), package_path)
        self.assertTrue(lock_path.is_file(), lock_path)
        package = json.loads(package_path.read_text(encoding="utf-8"))
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertEqual(package["dependencies"]["@mermaid-js/mermaid-cli"], "11.16.0")
        self.assertGreaterEqual(lock["lockfileVersion"], 3)
        self.assertEqual(
            lock["packages"][""]["dependencies"]["@mermaid-js/mermaid-cli"],
            "11.16.0",
        )

    def test_publication_workflows_build_and_verify_pdf_html_and_checksums(self):
        for name in ("ci.yaml", "preview-pdf.yml", "auto-release.yml"):
            text = self.workflow_text(name)
            self.assertIn("npm ci --prefix tools/mermaid --ignore-scripts", text, name)
            self.assertIn("tools/mermaid/node_modules/.bin", text, name)
            self.assertIn("tools/render_mermaid.py", text, name)
            self.assertRegex(
                text,
                r"(?s)tools/render_mermaid\.py\s+.*?--book-dir\s+\.\s+"
                r".*?--svg-out\s+[^\n]+\s+--strict\b",
                name,
            )
            self.assertIn("tools/build_html_reader.py", text, name)
            self.assertIn("--pdf", text, name)
            self.assertIn("--html", text, name)
            self.assertIn("--source-root .", text, name)
            self.assertIn("if-no-files-found: error", text, name)

    def test_tagged_release_attests_and_publishes_every_artifact(self):
        auto = self.workflow_text("auto-release.yml")
        self.assertRegex(auto, r"(?s)subject-path:.*?\.pdf.*?\.html.*?SHA256SUMS")
        self.assertRegex(auto, r"(?s)files:.*?\.pdf.*?\.html.*?SHA256SUMS")
        self.assertIn("fail_on_unmatched_files: true", auto)

    def run_preview_scripts(
        self,
        scenario: str,
        *,
        repository: str = TEST_REPOSITORY,
        sha: str = TEST_SHA,
    ) -> tuple[subprocess.CompletedProcess[str], list[list[str]]]:
        preview = self.workflow_text("preview-pdf.yml")
        step_names = preview_mutation_step_names(preview)
        scripts = [workflow_step_script(preview, name) for name in step_names]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_gh = root / "gh"
            fake_gh.write_text(FAKE_GH, encoding="utf-8")
            fake_gh.chmod(0o755)
            log = root / "commands.jsonl"
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{root}{os.pathsep}{env.get('PATH', '')}",
                    "GH_LOG": str(log),
                    "GH_SCENARIO": scenario,
                    "GH_TOKEN": "test-token",
                    "GH_REPO": repository,
                    "GITHUB_SHA": sha,
                }
            )
            result = None
            for script in scripts:
                result = subprocess.run(
                    ["/bin/bash", "-c", script],
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    break
            self.assertIsNotNone(result)
            commands = (
                [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
                if log.exists()
                else []
            )
            return result, commands

    def test_preview_mutation_steps_are_declared_in_exact_yaml_order(self):
        preview = self.workflow_text("preview-pdf.yml")
        self.assertEqual(preview_mutation_step_names(preview), list(PREVIEW_MUTATION_STEPS))

    def test_preview_order_reader_detects_yaml_step_swaps(self):
        preview = self.workflow_text("preview-pdf.yml")
        first, second, third = PREVIEW_MUTATION_STEPS
        swapped = preview.replace(first, "__FIRST__", 1)
        swapped = swapped.replace(second, first, 1).replace("__FIRST__", second, 1)
        self.assertEqual(
            preview_mutation_step_names(swapped),
            [second, first, third],
        )
        self.assertNotEqual(
            preview_mutation_step_names(swapped), list(PREVIEW_MUTATION_STEPS)
        )

    def test_preview_updates_existing_tag_release_then_assets_in_exact_order(self):
        result, commands = self.run_preview_scripts("ref_200_release_exists")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            commands,
            [
                GET_REF_COMMAND,
                PATCH_REF_COMMAND,
                VIEW_RELEASE_COMMAND,
                EDIT_RELEASE_COMMAND,
                UPLOAD_RELEASE_COMMAND,
            ],
        )

    def test_preview_creates_only_after_explicit_404s(self):
        result, commands = self.run_preview_scripts("ref_404_release_missing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            commands,
            [
                GET_REF_COMMAND,
                POST_REF_COMMAND,
                VIEW_RELEASE_COMMAND,
                CREATE_RELEASE_COMMAND,
                UPLOAD_RELEASE_COMMAND,
            ],
        )

    def test_preview_rejects_invalid_repository_and_sha_before_gh(self):
        cases = (
            ("owner/repo/extra", TEST_SHA, "Invalid GH_REPO"),
            (TEST_REPOSITORY, "a" * 39, "Invalid GITHUB_SHA"),
        )
        for repository, sha, message in cases:
            with self.subTest(repository=repository, sha=sha):
                result, commands = self.run_preview_scripts(
                    "ref_200_release_exists", repository=repository, sha=sha
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(commands, [])
                self.assertIn(message, result.stderr)

    def test_preview_tag_lookup_fails_closed_on_non_404_errors(self):
        for scenario in ("ref_401", "ref_403", "ref_429", "ref_503", "ref_network"):
            with self.subTest(scenario=scenario):
                result, commands = self.run_preview_scripts(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(commands, [GET_REF_COMMAND])
                expected = "network failure" if scenario.endswith("network") else scenario[4:]
                self.assertIn(expected, result.stderr)

    def test_preview_tag_404_requires_the_exact_expected_exit_code(self):
        for scenario in ("ref_404_exit2", "ref_404_exit0"):
            with self.subTest(scenario=scenario):
                result, commands = self.run_preview_scripts(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(commands, [GET_REF_COMMAND])
                self.assertNotIn(POST_REF_COMMAND, commands)

    def test_preview_release_lookup_fails_closed_on_unknown_errors(self):
        for scenario in (
            "ref_200_release_401",
            "ref_200_release_403",
            "ref_200_release_429",
            "ref_200_release_503",
            "ref_200_release_network",
            "ref_200_release_missing_exit2",
        ):
            with self.subTest(scenario=scenario):
                result, commands = self.run_preview_scripts(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(commands, [GET_REF_COMMAND, PATCH_REF_COMMAND, VIEW_RELEASE_COMMAND])
                self.assertNotIn(UPLOAD_RELEASE_COMMAND, commands)


if __name__ == "__main__":
    unittest.main()
