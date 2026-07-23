from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".paradigma" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load_tool(script: str):
    module_name = "failure_baseline_" + script.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, TOOLS / script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_tool(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


class LintAndLinkFailureBaselines(unittest.TestCase):
    def test_strict_lint_rejects_schema_and_checksum_drift(self) -> None:
        lint = load_tool("pd-lint-okf.py")
        schema = {
            "required_frontmatter": ["type", "title", "timestamp"],
            "required_paradigma_fields": ["temperature"],
            "types.test-concept.required_sections": ["Purpose"],
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = root / "concept.md"
            document.write_text(
                """---
type: test-concept
title: Test
timestamp: yesterday
---

# Wrong Section
""",
                encoding="utf-8",
            )
            messages = [
                issue.message
                for issue in lint.validate_document(document, schema, "strict")
            ]
            self.assertTrue(any("not ISO 8601" in message for message in messages))
            self.assertIn(
                "missing required paradigma field `temperature`", messages
            )
            self.assertIn("missing required section `# Purpose`", messages)

            index_path = root / "index.md"
            index_path.write_text(
                f"""# Index

{lint.BEGIN_MARKER}
<!-- checksum: 0000000000000000 -->
generated content
{lint.END_MARKER}
""",
                encoding="utf-8",
            )
            index_issues = lint.validate_index(index_path, "strict")
            self.assertTrue(
                any("checksum is stale" in issue.message for issue in index_issues)
            )

    def test_link_checker_distinguishes_errors_from_planned_warnings(self) -> None:
        links = load_tool("pd-check-links.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            document = root / "concept.md"
            document.write_text(
                """---
type: test-concept
paradigma:
  relations:
    planned:
      - /future.md
---

[Missing](missing.md)
""",
                encoding="utf-8",
            )
            issues = links.check_file(document, [root])
            self.assertEqual(
                [("ERROR", "markdown"), ("WARN", "planned")],
                [(issue.level, issue.message.split()[1]) for issue in issues],
            )


class HotSizeAndVersionFailureBaselines(unittest.TestCase):
    def test_hot_size_threshold_and_fail_on_warn_contract(self) -> None:
        hot_size = load_tool("pd-check-hot-size.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            progress = root / "progress" / "index.md"
            progress.parent.mkdir(parents=True)
            progress.write_text("line\n" * 161, encoding="utf-8")
            with mock.patch.multiple(
                hot_size,
                ROOT=root,
                ACTIVE_TASK=root / "missing-active-task.md",
                KNOWLEDGE_ROOT=root / "missing-knowledge",
                PROGRESS_INDEX=progress,
            ):
                with mock.patch.object(sys, "argv", ["pd-check-hot-size.py"]):
                    with redirect_stdout(StringIO()):
                        self.assertEqual(0, hot_size.main())
                with mock.patch.object(
                    sys, "argv", ["pd-check-hot-size.py", "--fail-on-warn"]
                ):
                    with redirect_stdout(StringIO()):
                        self.assertEqual(1, hot_size.main())

            error = hot_size.SizeCheck(progress, 261, 160, 260, "test")
            self.assertEqual("ERROR", error.level)

    def test_version_cli_rejects_invalid_semver(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / ".paradigma" / "tools"
            schemas = root / ".paradigma" / "schemas"
            tools.mkdir(parents=True)
            schemas.mkdir(parents=True)
            for name in ("_paradigma_yaml.py", "_version.py", "pd-version.py"):
                shutil.copy2(TOOLS / name, tools / name)
            (root / "VERSION").write_text("release-next\n", encoding="utf-8")
            (root / ".paradigma" / "config.yaml").write_text(
                """config_schema_version: "0.3"
okf_version: "0.1"
installed_distribution_version: release-next
""",
                encoding="utf-8",
            )
            (schemas / "paradigma-types.schema.yaml").write_text(
                'document_schema_version: "0.2"\n', encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, str(tools / "pd-version.py"), "--check"],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("distribution_version is not SemVer", result.stdout)


class DiagnoseAndCheckAllFailureBaselines(unittest.TestCase):
    def test_diagnose_unknown_workspace_has_machine_readable_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_tool(
                "pd-diagnose.py",
                "--project",
                temporary,
                "--upstream",
                str(ROOT),
                "--json",
            )
            self.assertEqual(2, result.returncode)
            report = json.loads(result.stdout)
            self.assertEqual("unknown", report["detected_version"])
            self.assertEqual(1, report["summary"]["errors"])
            self.assertEqual("missing", report["gaps"][0]["kind"])

    def test_check_all_stops_on_first_failure_by_default(self) -> None:
        check_all = load_tool("pd-check-all.py")
        failure = subprocess.CompletedProcess([], 1)
        with mock.patch.object(check_all.subprocess, "run", return_value=failure) as run:
            with mock.patch.object(sys, "argv", ["pd-check-all.py"]):
                with redirect_stdout(StringIO()):
                    self.assertEqual(1, check_all.main())
        self.assertEqual(1, run.call_count)

    def test_check_all_keep_going_aggregates_failures(self) -> None:
        check_all = load_tool("pd-check-all.py")
        results = [
            subprocess.CompletedProcess([], 1),
            subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 1),
            subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 0),
        ]
        output = StringIO()
        with mock.patch.object(check_all.subprocess, "run", side_effect=results) as run:
            with mock.patch.object(check_all, "_check_design_md", return_value=True):
                with mock.patch.object(
                    sys, "argv", ["pd-check-all.py", "--keep-going"]
                ):
                    with redirect_stdout(output):
                        self.assertEqual(1, check_all.main())
        self.assertEqual(len(check_all.STEPS), run.call_count)
        self.assertIn("2/6 check(s) failed", output.getvalue())


class CompactFailureBaselines(unittest.TestCase):
    def make_progress_root(self, root: Path) -> tuple[Path, Path]:
        progress = root / "memory-bank" / "logs" / "progress"
        progress.mkdir(parents=True)
        source = progress / "2026-07-23-session.md"
        source.write_text(
            """---
title: Test Session
---

# Session

- Preserved source
""",
            encoding="utf-8",
        )
        return progress, source

    def test_compact_replace_failure_preserves_old_summary_and_sources(self) -> None:
        compact = load_tool("pd-compact-progress.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            progress, source = self.make_progress_root(root)
            summary = progress / "summary.md"
            summary.write_text("old summary\n", encoding="utf-8")
            summary_before = summary.read_bytes()
            source_before = source.read_bytes()
            stderr = StringIO()
            with mock.patch.multiple(
                compact,
                ROOT=root,
                PROGRESS_ROOT=progress,
                SUMMARY_PATH=summary,
            ):
                with mock.patch.object(compact.os, "replace", side_effect=OSError("injected")):
                    with mock.patch.object(
                        sys, "argv", ["pd-compact-progress.py", "--write"]
                    ):
                        with redirect_stderr(stderr):
                            self.assertEqual(1, compact.main())

            self.assertEqual(summary_before, summary.read_bytes())
            self.assertEqual(source_before, source.read_bytes())
            self.assertEqual([], list(progress.glob(".summary.md.*.tmp")))
            self.assertIn("PD_COMPACT_IO_ERROR", stderr.getvalue())

    def test_compact_invalid_source_does_not_replace_summary(self) -> None:
        compact = load_tool("pd-compact-progress.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            progress, source = self.make_progress_root(root)
            source.write_text("---\ntitle: [broken\n---\n", encoding="utf-8")
            summary = progress / "summary.md"
            summary.write_text("old summary\n", encoding="utf-8")
            summary_before = summary.read_bytes()
            stderr = StringIO()
            with mock.patch.multiple(
                compact,
                ROOT=root,
                PROGRESS_ROOT=progress,
                SUMMARY_PATH=summary,
            ):
                with mock.patch.object(
                    sys, "argv", ["pd-compact-progress.py", "--write"]
                ):
                    with redirect_stdout(StringIO()), redirect_stderr(stderr):
                        self.assertEqual(1, compact.main())

            self.assertEqual(summary_before, summary.read_bytes())
            self.assertIn("YAML_SYNTAX_ERROR", stderr.getvalue())


class IndexAtomicityBaselines(unittest.TestCase):
    def test_index_replace_failure_preserves_existing_file(self) -> None:
        index = load_tool("_index.py")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "knowledge-index.json"
            path.write_text("old index\n", encoding="utf-8")
            before = path.read_bytes()
            with mock.patch.object(index.os, "replace", side_effect=OSError("injected")):
                with self.assertRaises(OSError):
                    index.atomic_write_text(path, "new index\n")

            self.assertEqual(before, path.read_bytes())
            self.assertEqual([], list(path.parent.glob(".knowledge-index.json.*.tmp")))


class ExternalWorkspaceBaselineTests(unittest.TestCase):
    def test_relocated_workspace_passes_rebuild_and_quality_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "derived-workspace"
            project.mkdir()
            for directory in (
                ".paradigma/tools",
                ".paradigma/schemas",
                "memory-bank/knowledge",
                "docs/rfc",
            ):
                shutil.copytree(
                    ROOT / directory,
                    project / directory,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
            for file_name in (
                ".paradigma/config.yaml",
                "VERSION",
                "memory-bank/runtime/active-task.md",
                "memory-bank/logs/progress/index.md",
            ):
                target = project / file_name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / file_name, target)

            tools = project / ".paradigma" / "tools"
            rebuild = subprocess.run(
                [sys.executable, str(tools / "pd-index.py"), "rebuild"],
                cwd=project,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(0, rebuild.returncode, rebuild.stderr)
            self.assertTrue(
                (project / ".paradigma" / "cache" / "knowledge-index.json").exists()
            )

            checks = subprocess.run(
                [sys.executable, str(tools / "pd-check-all.py"), "--keep-going"],
                cwd=project,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            self.assertEqual(
                0,
                checks.returncode,
                f"stdout:\n{checks.stdout}\nstderr:\n{checks.stderr}",
            )
            self.assertIn("All 6 checks passed", checks.stdout)


if __name__ == "__main__":
    unittest.main()
