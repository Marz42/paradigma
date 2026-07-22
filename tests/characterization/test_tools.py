from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".paradigma" / "tools"
EXPECTED_TOOLS = {
    "pd-archive-task.py",
    "pd-check-all.py",
    "pd-check-hot-size.py",
    "pd-check-links.py",
    "pd-compact-progress.py",
    "pd-diagnose.py",
    "pd-lint-okf.py",
    "pd-sync-index.py",
}


def run_tool(
    script: str,
    *args: str,
    cwd: Path = ROOT,
    tools_root: Path = TOOLS,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(tools_root / script), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def load_tool(script: str):
    module_name = "characterization_" + script.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, TOOLS / script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class ToolInventoryTests(unittest.TestCase):
    def test_expected_tool_inventory(self) -> None:
        actual = {path.name for path in TOOLS.glob("*.py")}
        self.assertEqual(EXPECTED_TOOLS, actual)

    def test_every_tool_exposes_help(self) -> None:
        for script in sorted(EXPECTED_TOOLS):
            with self.subTest(script=script):
                result = run_tool(script, "--help")
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("usage:", result.stdout.lower())


class RepositoryCliBaselineTests(unittest.TestCase):
    def assert_tool_passes(self, script: str, *args: str) -> str:
        result = run_tool(script, *args)
        self.assertEqual(
            0,
            result.returncode,
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result.stdout

    def test_strict_lint_passes(self) -> None:
        output = self.assert_tool_passes("pd-lint-okf.py", "--strict")
        self.assertIn("errors=0, warnings=0, mode=strict", output)

    def test_link_check_passes(self) -> None:
        output = self.assert_tool_passes("pd-check-links.py", "--allow-warnings")
        self.assertIn("errors=0, warnings=0", output)

    def test_indexes_are_current(self) -> None:
        output = self.assert_tool_passes("pd-sync-index.py", "--check")
        self.assertIn("stale=0", output)

    def test_hot_size_check_passes(self) -> None:
        output = self.assert_tool_passes("pd-check-hot-size.py")
        self.assertIn("errors=0, warnings=0", output)

    def test_check_all_passes(self) -> None:
        output = self.assert_tool_passes("pd-check-all.py", "--keep-going")
        self.assertIn("All 5 checks passed", output)

    def test_compact_progress_dry_run_does_not_write(self) -> None:
        summary = ROOT / "memory-bank" / "logs" / "progress" / "summary.md"
        before = summary.read_bytes() if summary.exists() else None
        output = self.assert_tool_passes("pd-compact-progress.py")
        after = summary.read_bytes() if summary.exists() else None
        self.assertEqual(before, after)
        self.assertIn("# Progress Summary", output)

    def test_self_diagnose_reports_current_harness_baseline(self) -> None:
        output = self.assert_tool_passes(
            "pd-diagnose.py",
            "--project",
            str(ROOT),
            "--upstream",
            str(ROOT),
            "--json",
        )
        report = json.loads(output)
        self.assertEqual("0.4.2", report["detected_version"])
        self.assertEqual("0.4.2", report["upstream_version"])
        self.assertTrue(report["version_match"])
        self.assertEqual([], report["gaps"])


class IsolatedMutationBaselineTests(unittest.TestCase):
    def make_archive_repository(self, root: Path) -> Path:
        tools = root / ".paradigma" / "tools"
        tools.mkdir(parents=True)
        shutil.copy2(TOOLS / "pd-archive-task.py", tools)

        runtime = root / "memory-bank" / "runtime"
        runtime.mkdir(parents=True)
        (runtime / "active-task.md").write_text(
            """# Active Task

## Task ID

TASK-001

## Current Status

Completed.

## Checklist

- [x] characterized
""",
            encoding="utf-8",
        )

        template = root / "memory-bank-template" / "runtime"
        template.mkdir(parents=True)
        (template / "active-task.template.md").write_text(
            """---
timestamp: YYYY-MM-DDTHH:mm:ssZ
---

# Active Task

## Task ID

## Current Status
""",
            encoding="utf-8",
        )
        return tools

    def test_archive_dry_run_is_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = self.make_archive_repository(root)
            active = root / "memory-bank" / "runtime" / "active-task.md"
            before = active.read_bytes()

            result = run_tool("pd-archive-task.py", cwd=root, tools_root=tools)

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Dry run only", result.stdout)
            self.assertEqual(before, active.read_bytes())
            progress = root / "memory-bank" / "logs" / "progress"
            self.assertFalse(progress.exists())

    def test_archive_write_creates_log_and_resets_active_task(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = self.make_archive_repository(root)

            result = run_tool(
                "pd-archive-task.py",
                "--write",
                cwd=root,
                tools_root=tools,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            logs = list((root / "memory-bank" / "logs" / "progress").glob("*.md"))
            self.assertEqual(1, len(logs))
            self.assertIn("TASK-001", logs[0].read_text(encoding="utf-8"))
            active = (root / "memory-bank" / "runtime" / "active-task.md").read_text(
                encoding="utf-8"
            )
            self.assertNotIn("TASK-001", active)
            self.assertNotIn("YYYY-MM-DDTHH:mm:ssZ", active)

    def test_compact_write_preserves_source_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / ".paradigma" / "tools"
            tools.mkdir(parents=True)
            shutil.copy2(TOOLS / "pd-compact-progress.py", tools)
            progress = root / "memory-bank" / "logs" / "progress"
            progress.mkdir(parents=True)
            source = progress / "2026-07-22-session.md"
            source.write_text(
                """---
title: Characterization Session
---

# Session

- Preserved signal
""",
                encoding="utf-8",
            )
            before = source.read_bytes()

            result = run_tool(
                "pd-compact-progress.py",
                "--write",
                cwd=root,
                tools_root=tools,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(before, source.read_bytes())
            summary = (progress / "summary.md").read_text(encoding="utf-8")
            self.assertIn("Characterization Session", summary)
            self.assertIn("Preserved signal", summary)


class ParserAndFunctionBaselineTests(unittest.TestCase):
    def test_yaml_subset_parsers_agree_on_supported_nested_lists(self) -> None:
        source = """knowledge_roots:
  - memory-bank/knowledge
  - docs/rfc
paradigma:
  temperature: warm
"""
        expected_roots = ["memory-bank/knowledge", "docs/rfc"]
        for script in ("pd-lint-okf.py", "pd-check-links.py", "pd-sync-index.py"):
            with self.subTest(script=script):
                parsed = load_tool(script).parse_yaml_subset(source)
                self.assertEqual(expected_roots, parsed["knowledge_roots"])
                self.assertEqual("warm", parsed["paradigma.temperature"])

    def test_diagnose_upstream_version_currently_prefers_harness_config(self) -> None:
        diagnose = load_tool("pd-diagnose.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / ".paradigma"
            config.mkdir()
            (config / "config.yaml").write_text(
                'paradigma_harness_version: "0.4.2"\n', encoding="utf-8"
            )
            (root / "VERSION").write_text("0.5.0\n", encoding="utf-8")
            self.assertEqual("0.4.2", diagnose._read_upstream_version(root))

    def test_archive_completion_baseline(self) -> None:
        archive = load_tool("pd-archive-task.py")
        completed = "## Current Status\n\nCompleted.\n\n## Checklist\n\n- [x] done\n"
        active = "## Current Status\n\nActive.\n\n## Checklist\n\n- [ ] pending\n"
        checklist_only = "## Current Status\n\nActive.\n\n## Checklist\n\n- [x] done\n"
        self.assertTrue(archive.is_completed(completed))
        self.assertFalse(archive.is_completed(active))
        self.assertTrue(archive.is_completed(checklist_only))

    def test_link_checker_strips_code_regions(self) -> None:
        links = load_tool("pd-check-links.py")
        source = """Visible [link](missing.md).

```markdown
[ignored](inside-fence.md)
```

Inline `[ignored](inline.md)`.
"""
        stripped = links.strip_code_content(source)
        self.assertIn("[link](missing.md)", stripped)
        self.assertNotIn("inside-fence.md", stripped)
        self.assertNotIn("inline.md", stripped)


if __name__ == "__main__":
    unittest.main()
