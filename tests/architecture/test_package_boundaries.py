from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "src" / "paradigma"


class PackageArchitectureTests(unittest.TestCase):
    def test_pyproject_uses_src_layout_and_root_version(self) -> None:
        data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(["VERSION"], data["tool"]["setuptools"]["dynamic"]["version"]["file"])
        self.assertEqual(["src"], data["tool"]["setuptools"]["packages"]["find"]["where"])
        self.assertEqual(">=3.11", data["project"]["requires-python"])

    def test_application_core_has_no_cli_or_legacy_tool_dependencies(self) -> None:
        for path in sorted(PACKAGE.rglob("*.py")):
            if "cli" in path.relative_to(PACKAGE).parts:
                continue
            with self.subTest(module=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertNotIn(".paradigma.tools", source)
                self.assertNotIn("sys.path", source)
                self.assertNotIn("import argparse", source)
                self.assertNotIn("import subprocess", source)
                self.assertNotIn("print(", source)

    def test_legacy_tools_are_adapters_not_business_implementations(self) -> None:
        tools = ROOT / ".paradigma" / "tools"
        forbidden = (
            "import yaml",
            "import hashlib",
            "import tempfile",
            "import subprocess",
            "os.replace(",
            "rglob(\"*.md\")",
            "def parse_markdown_text",
        )
        for path in sorted(tools.glob("*.py")):
            with self.subTest(tool=path.name):
                source = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, source)
                if path.name != "_bootstrap.py":
                    self.assertTrue(
                        "from paradigma" in source
                        or "from _index import" in source
                        or "from _version import" in source
                    )


if __name__ == "__main__":
    unittest.main()
