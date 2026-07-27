from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path
from urllib.parse import quote

from flask import Flask, redirect, render_template_string, request, url_for

from .config import AgentConfig
from .models import TaskProfile
from .proposal import write_proposal_file
from .store import MemoryStore


def create_app(task_choices: list[str]) -> Flask:
    app = Flask(__name__)

    workspace_root = Path.cwd().resolve()
    generated_root = (workspace_root / "generated_software").resolve()
    logs_root = (workspace_root / "logs").resolve()
    proposal_projects_root = (generated_root / "proposal_projects").resolve()
    proposals_root = (logs_root / "proposals").resolve()

    def _remote_repo_http_url() -> str | None:
      git_config = workspace_root / ".git" / "config"
      if not git_config.exists():
        return None

      parser = ConfigParser()
      parser.read(git_config, encoding="utf-8")
      section = 'remote "origin"'
      if not parser.has_section(section):
        return None

      remote_url = parser.get(section, "url", fallback="").strip()
      if not remote_url:
        return None
      if remote_url.startswith("git@github.com:"):
        remote_url = "https://github.com/" + remote_url.split(":", 1)[1]
      if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
      if remote_url.startswith("https://") or remote_url.startswith("http://"):
        return remote_url
      return None

    repo_http_url = _remote_repo_http_url()

    def _safe_path(path_str: str) -> Path | None:
        candidate = Path(path_str)
        if not candidate.is_absolute():
            candidate = (workspace_root / candidate).resolve()
        else:
            candidate = candidate.resolve()

        allowed_roots = [generated_root, logs_root]
        for root in allowed_roots:
            if candidate == root or root in candidate.parents:
                return candidate
        return None

    code_patterns = ("*.py", "*.md", "*.toml", "*.txt", "*.json", "*.yaml", "*.yml")
    ignored_dir_names = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}

    def _is_generated_code_file(file_path: Path) -> bool:
        relative_parts = file_path.relative_to(generated_root).parts
        if any(part in ignored_dir_names or part.endswith(".egg-info") for part in relative_parts):
            return False
        return file_path.is_file()

    def _list_project_files(project_dir: Path) -> list[dict[str, str]]:
        files: list[Path] = []
        for pattern in code_patterns:
            files.extend(project_dir.rglob(pattern))

        out: list[dict[str, str]] = []
        for file_path in sorted(files):
            if not _is_generated_code_file(file_path):
                continue
            out.append(
                {
                    "display": str(file_path.relative_to(project_dir)).replace("\\", "/"),
                    "path": str(file_path.relative_to(workspace_root)).replace("\\", "/"),
                }
            )
        return out

    def _generated_project_label(file_path: Path) -> str:
        relative_parts = file_path.relative_to(generated_root).parts
        if not relative_parts:
            return "generated_software"
        if relative_parts[0] == "proposal_projects" and len(relative_parts) > 1:
            return f"proposal_projects/{relative_parts[1]}"
        if len(relative_parts) == 1:
            return "generated_software"
        return relative_parts[0]

    def _list_all_generated_code() -> list[dict[str, str | int]]:
        if not generated_root.exists():
            return []

        files: list[Path] = []
        for pattern in code_patterns:
            files.extend(generated_root.rglob(pattern))

        entries: list[dict[str, str | int]] = []
        for file_path in sorted(files):
            if not _is_generated_code_file(file_path):
                continue
            content = file_path.read_text(encoding="utf-8", errors="replace")
            entries.append(
                {
                    "project": _generated_project_label(file_path),
                    "display": str(file_path.relative_to(generated_root)).replace("\\", "/"),
                    "path": str(file_path.relative_to(workspace_root)).replace("\\", "/"),
                    "size": file_path.stat().st_size,
                    "content": content,
                }
            )
        return entries

    def _count_generated_code_files() -> int:
        if not generated_root.exists():
            return 0

        count = 0
        for pattern in code_patterns:
            for file_path in generated_root.rglob(pattern):
                if _is_generated_code_file(file_path):
                    count += 1
        return count

    def _parse_proposal_file(path: Path) -> dict[str, str | float]:
        data = {
            "title": path.stem,
            "task_scope": "",
            "source_url": "",
            "status": "",
            "branch": "",
            "commit": "",
        "estimated_value_usd": 0.0,
            "proposal_path": str(path.relative_to(workspace_root)).replace("\\", "/"),
        }

        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if stripped.startswith("# Proposal:"):
                data["title"] = stripped.replace("# Proposal:", "", 1).strip()
            elif stripped.startswith("- Task Scope:"):
                data["task_scope"] = stripped.replace("- Task Scope:", "", 1).strip()
            elif stripped.startswith("- Source:"):
                data["source_url"] = stripped.replace("- Source:", "", 1).strip()
            elif stripped.startswith("- Status:"):
                data["status"] = stripped.replace("- Status:", "", 1).strip()
            elif stripped.startswith("- Branch:"):
                data["branch"] = stripped.replace("- Branch:", "", 1).strip()
            elif stripped.startswith("- Commit:"):
                data["commit"] = stripped.replace("- Commit:", "", 1).strip()
            elif stripped.startswith("- Estimated Value (USD):"):
              raw_value = stripped.replace("- Estimated Value (USD):", "", 1).strip().replace("$", "")
              try:
                data["estimated_value_usd"] = float(raw_value)
              except ValueError:
                data["estimated_value_usd"] = 0.0

        branch = data["branch"]
        commit = data["commit"]
        if repo_http_url and branch:
            data["repo_branch_url"] = f"{repo_http_url}/tree/{quote(branch, safe='/')}"
        else:
            data["repo_branch_url"] = ""
        if repo_http_url and commit and commit != "n/a":
            data["repo_commit_url"] = f"{repo_http_url}/commit/{quote(commit)}"
        else:
            data["repo_commit_url"] = ""

        return data

    def _list_proposals(min_estimated_value_usd: float = 0.0, task_filter: str = "all") -> list[dict[str, str | float]]:
        if not proposals_root.exists():
            return []
        proposal_files = sorted(proposals_root.glob("proposal_*.md"), reverse=True)
        proposals = [_parse_proposal_file(path) for path in proposal_files]
        proposals = [p for p in proposals if float(p.get("estimated_value_usd", 0.0)) >= min_estimated_value_usd]
        if task_filter != "all":
            proposals = [p for p in proposals if str(p.get("task_scope", "")).strip().lower() == task_filter]
        return proposals

    template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agent Control Center</title>
  <style>
    body { font-family: Segoe UI, system-ui, sans-serif; margin: 0; background: #f6f8fb; color: #1f2937; }
    .wrap { max-width: 1100px; margin: 24px auto; padding: 0 16px; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 12px; }
    .card { background: #fff; border: 1px solid #dbe3ee; border-radius: 10px; padding: 14px; }
    .span-12 { grid-column: span 12; }
    .span-6 { grid-column: span 6; }
    .span-4 { grid-column: span 4; }
    h1, h2 { margin: 0 0 10px 0; }
    h2 { font-size: 1.05rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
    th, td { text-align: left; border-bottom: 1px solid #e8eef6; padding: 6px; }
    .muted { color: #5f6b7a; font-size: 0.9rem; }
    .ok { color: #0f766e; }
    .warn { color: #b45309; }
    .msg { margin: 8px 0 12px; padding: 10px; border-radius: 8px; background: #ecfeff; border: 1px solid #bae6fd; }
    input, select { width: 100%; padding: 8px; border: 1px solid #cfd8e3; border-radius: 6px; background: #fff; }
    .row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 8px; }
    button { padding: 9px 12px; border: 0; border-radius: 7px; background: #0b62d6; color: #fff; cursor: pointer; }
    code { background: #eef3fb; padding: 2px 5px; border-radius: 4px; }
    .cmd { margin: 8px 0; }
    .link { color: #0b62d6; text-decoration: none; }
    .link:hover { text-decoration: underline; }
    .actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .actions a { white-space: nowrap; }
    @media (max-width: 900px) {
      .span-6, .span-4 { grid-column: span 12; }
      .row { grid-template-columns: 1fr; }
    }
  </style>
  <script>
    async function copyText(text) {
      try {
        await navigator.clipboard.writeText(text);
        alert('Copied to clipboard');
      } catch (err) {
        alert('Copy failed');
      }
    }
  </script>
</head>
<body>
<div class="wrap">
  <h1>Agent Control Center</h1>
  <div class="muted">Live results + retraining command runner</div>
  {% if message %}<div class="msg">{{ message }}</div>{% endif %}

  <div class="grid">
    <div class="card span-4">
      <h2>Latest Cycle</h2>
      {% if latest %}
      <div><b>Task:</b> {{ latest['task_name'] }}</div>
      <div><b>Mission:</b> {{ latest['mission_name'] }}</div>
      <div><b>Cycle:</b> #{{ latest['cycle_index'] }}</div>
      <div><b>Findings:</b> {{ latest['findings_count'] }}</div>
      <div><b>Avg Confidence:</b> {{ '%.2f'|format(latest['avg_confidence']) }}</div>
      <div><b>Status:</b> <span class="{{ 'ok' if latest['pass'] else 'warn' }}">{{ 'PASS' if latest['pass'] else 'FAIL' }}</span></div>
      {% else %}
      <div class="muted">No metrics yet.</div>
      {% endif %}
    </div>

    <div class="card span-4">
      <h2>Revenue Snapshot</h2>
      <div><b>Open Items:</b> {{ revenue_count }}</div>
      <div><b>Estimated USD:</b> {{ '%.2f'|format(revenue_total) }}</div>
      <div class="muted">Source: revenue_ledger</div>
    </div>

    <div class="card span-4">
      <h2>Benchmark Snapshot</h2>
      {% if bench %}
      <div><b>Task:</b> {{ bench['task_name'] }}</div>
      <div><b>Pass Rate:</b> {{ '%.2f'|format(bench['pass_rate']) }}</div>
      <div><b>Avg Findings:</b> {{ '%.2f'|format(bench['avg_findings']) }}</div>
      <div><b>Avg Conf:</b> {{ '%.2f'|format(bench['avg_confidence']) }}</div>
      {% else %}
      <div class="muted">No benchmark rows yet.</div>
      {% endif %}
    </div>

    <div class="card span-12">
      <h2>Retrain Task</h2>
      <form method="post" action="{{ url_for('retrain') }}">
        <div class="row">
          <div>
            <label>Task</label>
            <select name="task">{% for t in tasks %}<option value="{{ t }}">{{ t }}</option>{% endfor %}</select>
          </div>
          <div>
            <label>Novelty</label>
            <input name="novelty" placeholder="1.15" />
          </div>
          <div>
            <label>Reliability</label>
            <input name="reliability" placeholder="2.8" />
          </div>
          <div>
            <label>Speed</label>
            <input name="speed" placeholder="0.45" />
          </div>
        </div>
        <div class="row">
          <div style="grid-column: span 4;">
            <label>Notes</label>
            <input name="notes" placeholder="Optional training note" />
          </div>
        </div>
        <button type="submit">Apply Retraining</button>
      </form>
      <div class="muted" style="margin-top:8px;">Equivalent command: <code>python -m agent.main train --task &lt;task&gt; --novelty &lt;n&gt; --reliability &lt;r&gt; --speed &lt;s&gt;</code></div>
    </div>

    <div class="card span-12">
      <h2>CLI Commands (Push Separately)</h2>
      <div class="cmd"><code id="buildcmd">python -m agent.main execute-proposals --proposal-dir logs/proposals --output-dir generated_software/proposal_projects --artifact-dir release_artifacts --branch-prefix proposal --run-tests --package</code></div>
      <button onclick="copyText(document.getElementById('buildcmd').innerText)">Copy Build-Only Command</button>
      <div class="cmd"><code id="pushcmd">python -m agent.main execute-proposals --proposal-dir logs/proposals --output-dir generated_software/proposal_projects --artifact-dir release_artifacts --branch-prefix proposal --run-tests --package --push</code></div>
      <button onclick="copyText(document.getElementById('pushcmd').innerText)">Copy Push Command</button>
      <div class="muted" style="margin-top:8px;">Run build-only first to review code in the explorer, then run push when ready.</div>
    </div>

    <div class="card span-12">
      <h2>Money Threshold</h2>
      <form method="get" action="{{ url_for('dashboard') }}">
        <div class="row">
          <div>
            <label>Minimum Estimated USD</label>
            <input type="number" min="0" step="1000" name="min_estimated_value_usd" value="{{ '%.2f'|format(min_estimated_value_usd) }}" />
          </div>
          <div>
            <label>Task Filter</label>
            <select name="task_filter">
              <option value="all" {% if task_filter == 'all' %}selected{% endif %}>all</option>
              {% for t in tasks %}
              <option value="{{ t }}" {% if task_filter == t %}selected{% endif %}>{{ t }}</option>
              {% endfor %}
            </select>
          </div>
          <div style="display:flex; align-items:end; gap:8px;">
            <button type="submit">Apply Filter</button>
          </div>
          <div style="display:flex; align-items:end; gap:8px;">
            <a class="link" href="{{ url_for('dashboard') }}">Clear Filter</a>
          </div>
          <div>
            <label>Money Loop Command</label>
            <div class="cmd"><code id="moneycmd">python -m agent.main money-loop --task {{ task_filter if task_filter != 'all' else 'software_solver' }} --min-estimated-value-usd {{ '%.2f'|format(min_estimated_value_usd) }}</code></div>
          </div>
        </div>
      </form>
      <button onclick="copyText(document.getElementById('moneycmd').innerText)">Copy Money-Loop Command</button>
      <div class="muted" style="margin-top:8px;">This filters the dashboard lists and gives you the matching CLI command for new runs.</div>
    </div>

    <div class="card span-12">
      <h2>Generated Code Explorer</h2>
      <div class="cmd">
        <a class="link" href="{{ url_for('all_generated_code') }}">Show All Generated Code</a>
        <span class="muted">({{ generated_file_count }} files)</span>
      </div>
      {% if projects %}
      <table>
        <thead><tr><th>Project</th><th>Action</th></tr></thead>
        <tbody>
        {% for project in projects %}
          <tr>
            <td>{{ project }}</td>
            <td><a class="link" href="{{ url_for('project_files', project_name=project) }}">Open Files</a></td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
      {% else %}
      <div class="muted">No generated projects found yet.</div>
      {% endif %}
    </div>

    <div class="card span-6">
      <h2>Found Proposals</h2>
      <form method="post" action="{{ url_for('draft_proposals') }}" style="margin-bottom:10px;">
        <input type="hidden" name="task_filter" value="{{ task_filter }}" />
        <div class="row" style="grid-template-columns: repeat(3, 1fr);">
          <div>
            <label>Draft Limit</label>
            <input type="number" min="1" max="500" name="limit" value="25" />
          </div>
          <div>
            <label>Status</label>
            <select name="status">
              <option value="open">open</option>
              <option value="proposed">proposed</option>
              <option value="exported">exported</option>
            </select>
          </div>
          <div>
            <label>Min Estimated USD</label>
            <input type="number" min="0" step="1000" name="min_estimated_value_usd" value="{{ '%.2f'|format(min_estimated_value_usd) }}" />
          </div>
        </div>
        <div style="display:flex; gap:10px; align-items:center; margin-top:8px;">
          <label style="display:flex; align-items:center; gap:6px;">
            <input type="checkbox" name="overwrite" value="1" /> overwrite existing files
          </label>
          <label style="display:flex; align-items:center; gap:6px;">
            <input type="checkbox" name="mark_as_proposed" value="1" /> mark drafted entries as proposed
          </label>
          <button type="submit">Generate Proposals</button>
        </div>
      </form>
      {% if proposals %}
      <table>
        <thead><tr><th>Proposal</th><th>Task</th><th>USD</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
        {% for proposal in proposals %}
          <tr>
            <td>{{ proposal.title }}</td>
            <td>{{ proposal.task_scope or 'n/a' }}</td>
            <td>{{ '%.2f'|format(proposal.estimated_value_usd) }}</td>
            <td>{{ proposal.status or 'draft' }}</td>
            <td>
              <div class="actions">
                <a class="link" href="{{ url_for('view_code') }}?path={{ proposal.proposal_path }}">Open Proposal</a>
                {% if proposal.source_url %}<a class="link" href="{{ proposal.source_url }}" target="_blank" rel="noreferrer">Open Website</a>{% endif %}
                {% if proposal.repo_branch_url %}<a class="link" href="{{ proposal.repo_branch_url }}" target="_blank" rel="noreferrer">Open Repo Branch</a>{% endif %}
                {% if proposal.repo_commit_url %}<a class="link" href="{{ proposal.repo_commit_url }}" target="_blank" rel="noreferrer">Open Commit</a>{% endif %}
              </div>
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
      {% else %}
      <div class="muted">No proposals found yet.</div>
      {% endif %}
    </div>

    <div class="card span-6">
      <h2>Recent Revenue Entries</h2>
      <table>
        <thead><tr><th>ID</th><th>Task</th><th>Title</th><th>USD</th><th>Status</th></tr></thead>
        <tbody>
        {% for r in revenue_rows %}
          <tr>
            <td>{{ r['id'] }}</td>
            <td>{{ r['task_name'] }}</td>
            <td>{{ r['title'][:48] }}</td>
            <td>{{ '%.2f'|format(r['estimated_value_usd']) }}</td>
            <td>{{ r['status'] }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>

    <div class="card span-6">
      <h2>Task Profiles</h2>
      <table>
        <thead><tr><th>Task</th><th>Novelty</th><th>Reliability</th><th>Speed</th></tr></thead>
        <tbody>
        {% for p in profiles %}
          <tr>
            <td>{{ p.name }}</td>
            <td>{{ '%.2f'|format(p.novelty_weight) }}</td>
            <td>{{ '%.2f'|format(p.reliability_weight) }}</td>
            <td>{{ '%.2f'|format(p.speed_weight) }}</td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
</body>
</html>
"""

    all_code_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>All Generated Code</title>
  <style>
    body { font-family: Segoe UI, system-ui, sans-serif; margin: 0; background: #f6f8fb; color: #1f2937; }
    .wrap { max-width: 1180px; margin: 24px auto; padding: 0 16px; }
    .card { background: #fff; border: 1px solid #dbe3ee; border-radius: 10px; padding: 14px; margin-bottom: 12px; }
    .toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
    .muted { color: #5f6b7a; font-size: 0.9rem; }
    .file-head { display: flex; align-items: baseline; justify-content: space-between; gap: 10px; flex-wrap: wrap; }
    pre { background: #0f172a; color: #e2e8f0; border-radius: 8px; padding: 12px; overflow: auto; tab-size: 2; }
    code { font-family: Consolas, ui-monospace, SFMono-Regular, monospace; font-size: 0.9rem; }
    a { color: #0b62d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<div class="wrap">
  <div class="toolbar">
    <div>
      <h1>All Generated Code</h1>
      <div class="muted">{{ files|length }} files from generated_software</div>
    </div>
    <a href="{{ url_for('dashboard') }}">Back to dashboard</a>
  </div>
  {% if files %}
    {% for f in files %}
    <section class="card">
      <div class="file-head">
        <div>
          <div><b>{{ f.display }}</b></div>
          <div class="muted">{{ f.project }} · {{ f.size }} bytes</div>
        </div>
        <a href="{{ url_for('view_code') }}?path={{ f.path }}">Open single file</a>
      </div>
      <pre><code>{{ f.content }}</code></pre>
    </section>
    {% endfor %}
  {% else %}
    <div class="card muted">No generated code files found yet.</div>
  {% endif %}
</div>
</body>
</html>
"""

    project_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ project_name }} Files</title>
  <style>
    body { font-family: Segoe UI, system-ui, sans-serif; margin: 0; background: #f6f8fb; color: #1f2937; }
    .wrap { max-width: 1100px; margin: 24px auto; padding: 0 16px; }
    .card { background: #fff; border: 1px solid #dbe3ee; border-radius: 10px; padding: 14px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.92rem; margin-top: 10px; }
    th, td { text-align: left; border-bottom: 1px solid #e8eef6; padding: 6px; }
    a { color: #0b62d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<div class="wrap">
  <div class="card">
    <h2>{{ project_name }} Files</h2>
    <div><a href="{{ url_for('dashboard') }}">Back to dashboard</a></div>
    <table>
      <thead><tr><th>File</th><th>Action</th></tr></thead>
      <tbody>
      {% for f in files %}
      <tr>
        <td>{{ f.display }}</td>
        <td><a href="{{ url_for('view_code') }}?path={{ f.path }}">Open Code</a></td>
      </tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
</body>
</html>
"""

    code_template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ rel_path }}</title>
  <style>
    body { font-family: Segoe UI, system-ui, sans-serif; margin: 0; background: #f6f8fb; color: #1f2937; }
    .wrap { max-width: 1100px; margin: 24px auto; padding: 0 16px; }
    .card { background: #fff; border: 1px solid #dbe3ee; border-radius: 10px; padding: 14px; }
    pre { background: #0f172a; color: #e2e8f0; border-radius: 8px; padding: 12px; overflow: auto; }
    button { padding: 9px 12px; border: 0; border-radius: 7px; background: #0b62d6; color: #fff; cursor: pointer; margin: 8px 0; }
    a { color: #0b62d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
  <script>
    async function copyCode() {
      try {
        await navigator.clipboard.writeText(document.getElementById('code').innerText);
        alert('Copied to clipboard');
      } catch (err) {
        alert('Copy failed');
      }
    }
  </script>
</head>
<body>
<div class="wrap">
  <div class="card">
    <h2>{{ rel_path }}</h2>
    <div><a href="{{ back_url }}">Back</a></div>
    <button onclick="copyCode()">Copy Code</button>
    <pre id="code">{{ content }}</pre>
  </div>
</div>
</body>
</html>
"""

    @app.get("/")
    def dashboard():
      cfg = AgentConfig()
      store = MemoryStore(cfg.db_path)
      raw_min_value = request.args.get("min_estimated_value_usd", "0")
      task_filter = (request.args.get("task_filter", "all") or "all").strip().lower()
      if task_filter != "all" and task_filter not in {t.lower() for t in task_choices}:
        task_filter = "all"

      try:
        min_estimated_value_usd = max(0.0, float(raw_min_value))
      except ValueError:
        min_estimated_value_usd = 0.0

      metrics = store.recent_cycle_metrics(limit=20)
      latest = metrics[0] if metrics else None
      bench_rows = store.recent_task_benchmarks(limit=1)
      bench = bench_rows[0] if bench_rows else None

      open_revenue_rows = store.recent_revenue_entries(limit=1000, status="open")
      if task_filter != "all":
        open_revenue_rows = [
          row for row in open_revenue_rows if str(row["task_name"]).strip().lower() == task_filter
        ]

      filtered_open_revenue_rows = [
        row for row in open_revenue_rows if float(row["estimated_value_usd"]) >= min_estimated_value_usd
      ]
      revenue_rows = filtered_open_revenue_rows[:20]
      revenue_count = len(filtered_open_revenue_rows)
      revenue_total = sum(float(row["estimated_value_usd"]) for row in filtered_open_revenue_rows)
      profiles = [store.get_task_profile(task) for task in task_choices]

      projects: list[str] = []
      if proposal_projects_root.exists():
        projects = [p.name for p in sorted(proposal_projects_root.iterdir()) if p.is_dir()]

      return render_template_string(
        template,
        latest=latest,
        bench=bench,
        revenue_rows=revenue_rows,
        proposals=_list_proposals(min_estimated_value_usd=min_estimated_value_usd, task_filter=task_filter),
        revenue_count=revenue_count,
        revenue_total=revenue_total,
        min_estimated_value_usd=min_estimated_value_usd,
        task_filter=task_filter,
        profiles=profiles,
        projects=projects,
        generated_file_count=_count_generated_code_files(),
        tasks=task_choices,
        message=request.args.get("message", ""),
      )

    @app.get("/generated-code")
    def all_generated_code():
        files = _list_all_generated_code()
        return render_template_string(all_code_template, files=files)

    @app.get("/projects/<project_name>")
    def project_files(project_name: str):
        project_dir = (proposal_projects_root / project_name).resolve()
        if not project_dir.exists() or proposal_projects_root not in project_dir.parents:
            return redirect(url_for("dashboard", message=f"Unknown project: {project_name}"))

        files = _list_project_files(project_dir)
        return render_template_string(project_template, project_name=project_name, files=files)

    @app.get("/code")
    def view_code():
        rel_path = request.args.get("path", "")
        safe = _safe_path(rel_path)
        if safe is None or not safe.exists() or safe.is_dir():
            return redirect(url_for("dashboard", message="Invalid file path"))

        content = safe.read_text(encoding="utf-8", errors="replace")
        normalized_rel = str(safe.relative_to(workspace_root)).replace("\\", "/")
        back_url = url_for("dashboard")
        parts = list(safe.parts)
        if "proposal_projects" in parts:
            idx = parts.index("proposal_projects")
            if idx + 1 < len(parts):
                back_url = url_for("project_files", project_name=parts[idx + 1])

        return render_template_string(
            code_template,
            rel_path=normalized_rel,
            content=content,
            back_url=back_url,
        )

    @app.post("/retrain")
    def retrain():
        cfg = AgentConfig()
        store = MemoryStore(cfg.db_path)

        task = request.form.get("task", "trend_watch")
        profile = store.get_task_profile(task)

        def parse_float(v: str | None, default: float) -> float:
            if v is None or v.strip() == "":
                return default
            try:
                return float(v)
            except ValueError:
                return default

        novelty = parse_float(request.form.get("novelty"), profile.novelty_weight)
        reliability = parse_float(request.form.get("reliability"), profile.reliability_weight)
        speed = parse_float(request.form.get("speed"), profile.speed_weight)
        notes = request.form.get("notes") or profile.notes

        updated = TaskProfile(
            name=task,
            novelty_weight=novelty,
            reliability_weight=reliability,
            speed_weight=speed,
            notes=notes,
        )
        store.upsert_task_profile(updated)

        msg = (
            f"Retrained {task}: novelty={updated.novelty_weight:.2f}, "
            f"reliability={updated.reliability_weight:.2f}, speed={updated.speed_weight:.2f}"
        )
        return redirect(url_for("dashboard", message=msg))

    @app.post("/draft-proposals")
    def draft_proposals():
        cfg = AgentConfig()
        store = MemoryStore(cfg.db_path)

        raw_status = (request.form.get("status") or "open").strip().lower()
        status = raw_status if raw_status in {"open", "proposed", "exported"} else "open"
        raw_limit = request.form.get("limit", "25")
        try:
            limit = max(1, min(500, int(raw_limit)))
        except ValueError:
            limit = 25

        raw_min_value = request.form.get("min_estimated_value_usd", "0")
        try:
            min_estimated_value_usd = max(0.0, float(raw_min_value))
        except ValueError:
            min_estimated_value_usd = 0.0

        overwrite = request.form.get("overwrite") == "1"
        mark_as_proposed = request.form.get("mark_as_proposed") == "1"
        task_filter = (request.form.get("task_filter") or "all").strip().lower()
        out_dir = proposals_root
        out_dir.mkdir(parents=True, exist_ok=True)

        entries = store.recent_revenue_entries(limit=limit, status=status)
        if task_filter != "all":
            entries = [entry for entry in entries if str(entry["task_name"]).strip().lower() == task_filter]
        entries = [
            entry for entry in entries if float(entry["estimated_value_usd"]) >= min_estimated_value_usd
        ]

        existing_paths = set(out_dir.glob("proposal_*.md"))
        created = 0
        reused = 0
        for entry in entries:
            path = write_proposal_file(out_dir, entry, overwrite=overwrite)
            if path in existing_paths and not overwrite:
                reused += 1
            else:
                created += 1
                existing_paths.add(path)

        if mark_as_proposed and entries:
            ids = [int(entry["id"]) for entry in entries]
            store.mark_revenue_entries_status(ids, "proposed")

        msg = (
            f"Drafted proposals: created={created}, reused={reused}, "
            f"scanned={len(entries)} from status={status}"
        )
        return redirect(
            url_for(
                "dashboard",
                message=msg,
                min_estimated_value_usd=f"{min_estimated_value_usd:.2f}",
                task_filter=task_filter,
            )
        )

    return app


def run_web_server(task_choices: list[str], host: str, port: int) -> None:
    app = create_app(task_choices)
    app.run(host=host, port=port)
