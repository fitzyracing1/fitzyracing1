import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SubmitResult:
    ok: bool
    message: str
    branch: str
    commit_hash: str


def auto_submit_changes(
    repo_dir: Path,
    branch: str,
    commit_message: str,
    push: bool,
    push_remote_name: str = "origin",
    push_remote_url: str = "",
) -> SubmitResult:
    try:
        subprocess.run(["git", "checkout", "-B", branch], cwd=repo_dir, check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "-A"], cwd=repo_dir, check=True, capture_output=True, text=True)
        commit_proc = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir,
            check=False,
            capture_output=True,
            text=True,
        )
        if commit_proc.returncode != 0 and "nothing to commit" not in commit_proc.stdout.lower():
            return SubmitResult(False, commit_proc.stderr.strip() or commit_proc.stdout.strip(), branch, "")

        rev = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        commit_hash = rev.stdout.strip()

        if push:
            push_target = push_remote_url.strip() or push_remote_name
            push_cmd = ["git", "push", push_target, f"{branch}:{branch}"] if push_remote_url.strip() else ["git", "push", "-u", push_target, branch]
            push_proc = subprocess.run(
                push_cmd,
                cwd=repo_dir,
                check=False,
                capture_output=True,
                text=True,
            )
            if push_proc.returncode != 0:
                return SubmitResult(
                    False,
                    f"Committed locally but push failed: {push_proc.stderr.strip() or push_proc.stdout.strip()}",
                    branch,
                    commit_hash,
                )

        return SubmitResult(True, "Submission completed", branch, commit_hash)
    except Exception as exc:
        return SubmitResult(False, str(exc), branch, "")


def auto_submit_paths(
    repo_dir: Path,
    branch: str,
    commit_message: str,
    paths: list[Path],
    push: bool,
    push_remote_name: str = "origin",
    push_remote_url: str = "",
) -> SubmitResult:
    try:
        subprocess.run(["git", "checkout", "-B", branch], cwd=repo_dir, check=True, capture_output=True, text=True)

        rel_paths: list[str] = []
        for p in paths:
            try:
                rel_paths.append(str(p.resolve().relative_to(repo_dir.resolve())))
            except Exception:
                rel_paths.append(str(p))

        add_cmd = ["git", "add", "--"] + rel_paths
        subprocess.run(add_cmd, cwd=repo_dir, check=True, capture_output=True, text=True)

        commit_proc = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=repo_dir,
            check=False,
            capture_output=True,
            text=True,
        )
        if commit_proc.returncode != 0 and "nothing to commit" not in commit_proc.stdout.lower():
            return SubmitResult(False, commit_proc.stderr.strip() or commit_proc.stdout.strip(), branch, "")

        rev = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True,
        )
        commit_hash = rev.stdout.strip()

        if push:
            push_target = push_remote_url.strip() or push_remote_name
            push_cmd = ["git", "push", push_target, f"{branch}:{branch}"] if push_remote_url.strip() else ["git", "push", "-u", push_target, branch]
            push_proc = subprocess.run(
                push_cmd,
                cwd=repo_dir,
                check=False,
                capture_output=True,
                text=True,
            )
            if push_proc.returncode != 0:
                return SubmitResult(
                    False,
                    f"Committed locally but push failed: {push_proc.stderr.strip() or push_proc.stdout.strip()}",
                    branch,
                    commit_hash,
                )

        return SubmitResult(True, "Submission completed", branch, commit_hash)
    except Exception as exc:
        return SubmitResult(False, str(exc), branch, "")
