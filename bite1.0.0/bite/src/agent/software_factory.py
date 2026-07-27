import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FactoryResult:
    ok: bool
    message: str
    path: Path | None = None


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug or "software_app"


def generate_spec(product_name: str, output_dir: Path, mission_statement: str) -> FactoryResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = _slug(product_name)
    spec_path = output_dir / f"{slug}_spec.md"

    spec = [
        f"# Product Spec: {product_name}",
        "",
        "## Mission",
        f"- {mission_statement}",
        "",
        "## Problem",
        "- Teams need repeatable, testable software workflows with clear operational evidence and low manual overhead.",
        "",
        "## Core Capabilities",
        "- Capture structured inputs and operational constraints.",
        "- Produce validated outputs with risk and quality signals.",
        "- Record traceable decisions, assumptions, and audit notes.",
        "",
        "## Non-Functional Requirements",
        "- Deterministic outputs from same inputs.",
        "- Structured logs and test coverage >= 80% for core logic.",
        "- Exportable artifacts in JSON and Markdown.",
        "",
        "## Interfaces",
        "- CLI: build-output, score-risk, export-report.",
        "- Python API: solution_app.core module.",
        "",
        "## Test Strategy",
        "- Unit tests for validation and scoring.",
        "- Integration test for end-to-end output generation.",
    ]
    spec_path.write_text("\n".join(spec) + "\n", encoding="utf-8")
    return FactoryResult(True, "Specification generated.", spec_path)


def generate_code(product_name: str, output_dir: Path) -> FactoryResult:
    slug = _slug(product_name)
    root = output_dir / slug
    pkg = root / "solution_app"
    tests = root / "tests"

    pkg.mkdir(parents=True, exist_ok=True)
    tests.mkdir(parents=True, exist_ok=True)

    (tests / "__init__.py").write_text("", encoding="utf-8")

    (root / "README.md").write_text(
        f"# {product_name}\n\n"
        "Generated scaffold for domain-neutral production software.\n",
        encoding="utf-8",
    )

    (pkg / "__init__.py").write_text(
        "from .core import build_output, score_risk\n",
        encoding="utf-8",
    )

    (pkg / "core.py").write_text(
        "from dataclasses import dataclass\n\n"
        "@dataclass\n"
        "class SolutionInput:\n"
        "    workflow_steps: float\n"
        "    integration_points: float\n"
        "    automation_window_hours: float\n\n"
        "def score_risk(inp: SolutionInput) -> float:\n"
        "    score = 0.0\n"
        "    if inp.workflow_steps > 25:\n"
        "        score += 0.35\n"
        "    if inp.integration_points > 8:\n"
        "        score += 0.25\n"
        "    if inp.automation_window_hours < 4:\n"
        "        score += 0.30\n"
        "    return min(1.0, score)\n\n"
        "def build_output(inp: SolutionInput) -> dict:\n"
        "    risk = score_risk(inp)\n"
        "    return {\n"
        "        'workflow_steps': inp.workflow_steps,\n"
        "        'integration_points': inp.integration_points,\n"
        "        'automation_window_hours': inp.automation_window_hours,\n"
        "        'risk_score': risk,\n"
        "        'risk_band': 'high' if risk >= 0.7 else 'medium' if risk >= 0.35 else 'low',\n"
        "    }\n",
        encoding="utf-8",
    )

    (pkg / "cli.py").write_text(
        "import argparse\n"
        "import json\n"
        "from .core import SolutionInput, build_output\n\n"
        "def main() -> None:\n"
        f"    p = argparse.ArgumentParser(description='{product_name}')\n"
        "    p.add_argument('--workflow-steps', type=float, required=True)\n"
        "    p.add_argument('--integration-points', type=float, required=True)\n"
        "    p.add_argument('--automation-window-hours', type=float, required=True)\n"
        "    args = p.parse_args()\n"
        "    inp = SolutionInput(args.workflow_steps, args.integration_points, args.automation_window_hours)\n"
        "    print(json.dumps(build_output(inp), indent=2))\n\n"
        "if __name__ == '__main__':\n"
        "    main()\n",
        encoding="utf-8",
    )

    (tests / "test_core.py").write_text(
        "import unittest\n\n"
        "from solution_app.core import SolutionInput, build_output, score_risk\n\n"
        "class CoreTests(unittest.TestCase):\n"
        "    def test_score_risk_low(self):\n"
        "        inp = SolutionInput(workflow_steps=8, integration_points=2, automation_window_hours=12)\n"
        "        self.assertLess(score_risk(inp), 0.35)\n\n"
        "    def test_build_output_has_keys(self):\n"
        "        inp = SolutionInput(workflow_steps=30, integration_points=10, automation_window_hours=2)\n"
        "        output = build_output(inp)\n"
        "        self.assertIn('risk_score', output)\n"
        "        self.assertIn('risk_band', output)\n\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n",
        encoding="utf-8",
    )

    (root / "pyproject.toml").write_text(
        "[build-system]\n"
        "requires = ['setuptools>=61.0']\n"
        "build-backend = 'setuptools.build_meta'\n\n"
        "[project]\n"
        f"name = '{slug}'\n"
        "version = '0.1.0'\n"
        "description = 'Generated production software scaffold'\n"
        "requires-python = '>=3.10'\n",
        encoding="utf-8",
    )

    return FactoryResult(True, "Software scaffold generated.", root)


def run_tests(project_dir: Path) -> FactoryResult:
    if not project_dir.exists():
        return FactoryResult(False, "Project directory does not exist.")

    cmd = [sys.executable, "-m", "unittest", "-v", "tests.test_core"]
    proc = subprocess.run(cmd, cwd=project_dir, text=True, capture_output=True)
    combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
    out_path = project_dir / "test_output.txt"
    out_path.write_text(combined, encoding="utf-8")

    if "Ran 0 tests" in combined:
        return FactoryResult(False, "No tests were executed. See test_output.txt", out_path)

    if proc.returncode == 0:
        return FactoryResult(True, "Tests passed.", out_path)
    return FactoryResult(False, "Tests failed. See test_output.txt", out_path)


def package_release(project_dir: Path, artifact_dir: Path) -> FactoryResult:
    if not project_dir.exists():
        return FactoryResult(False, "Project directory does not exist.")

    artifact_dir.mkdir(parents=True, exist_ok=True)
    base_name = artifact_dir / project_dir.name
    archive_path = Path(shutil.make_archive(str(base_name), "zip", root_dir=project_dir))

    manifest = {
        "project": project_dir.name,
        "archive": archive_path.name,
        "includes": ["solution_app", "tests", "README.md", "pyproject.toml"],
    }
    manifest_path = artifact_dir / f"{project_dir.name}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return FactoryResult(True, "Release package created.", archive_path)
