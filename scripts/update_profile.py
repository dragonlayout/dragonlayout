#!/usr/bin/env python3
"""Update profile README dynamic sections.

This script updates two sections in README.md:
1. Build log block from profile/build-log.md
2. Activity block from GitHub API
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

START_BUILD_LOG = "<!--START_BUILD_LOG-->"
END_BUILD_LOG = "<!--END_BUILD_LOG-->"
START_ACTIVITY = "<!--START_ACTIVITY-->"
END_ACTIVITY = "<!--END_ACTIVITY-->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update profile README sections.")
    parser.add_argument("--readme", default="README.md", help="Path to README file.")
    parser.add_argument(
        "--build-log",
        default="profile/build-log.md",
        help="Path to the build log source file.",
    )
    parser.add_argument(
        "--username",
        default=None,
        help="GitHub username. Defaults to owner in GITHUB_REPOSITORY.",
    )
    parser.add_argument(
        "--max-build-log",
        type=int,
        default=4,
        help="How many week sections to include.",
    )
    parser.add_argument(
        "--max-repos",
        type=int,
        default=5,
        help="How many repositories to list in activity section.",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=5,
        help="How many public events to list in activity section.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Do not call GitHub API. Keep current activity block.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print whether changes would be made without writing files.",
    )
    return parser.parse_args()


def determine_username(cli_username: str | None) -> str | None:
    if cli_username:
        return cli_username

    repository = os.getenv("GITHUB_REPOSITORY", "")
    if repository and "/" in repository:
        return repository.split("/", 1)[0]

    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def replace_block(content: str, start: str, end: str, new_body: str) -> str:
    start_idx = content.find(start)
    end_idx = content.find(end)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise ValueError(f"Cannot find marker pair: {start} ... {end}")

    replacement = f"{start}\n{new_body.strip()}\n{end}"
    return content[:start_idx] + replacement + content[end_idx + len(end) :]


def extract_block(content: str, start: str, end: str) -> str:
    start_idx = content.find(start)
    end_idx = content.find(end)
    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        raise ValueError(f"Cannot find marker pair: {start} ... {end}")

    body_start = start_idx + len(start)
    block = content[body_start:end_idx]
    return block.strip()


def split_week_sections(build_log_text: str) -> list[str]:
    lines = build_log_text.splitlines()
    sections: list[list[str]] = []
    current: list[str] | None = None

    for line in lines:
        if line.startswith("## Week "):
            if current:
                sections.append(current)
            current = [line]
            continue

        if current is not None:
            current.append(line)

    if current:
        sections.append(current)

    return ["\n".join(section).strip() for section in sections if "\n".join(section).strip()]


def render_build_log(build_log_path: Path, max_sections: int) -> str:
    if not build_log_path.exists():
        return "- Build log source not found.\n- 未找到构建日志源文件。"

    text = read_text(build_log_path)
    sections = split_week_sections(text)
    if not sections:
        return "- No weekly sections found yet.\n- 暂无周度记录。"

    selected = sections[:max_sections]
    return "\n\n".join(selected)


def api_get(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-readme-updater",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def normalize_date(iso_text: str | None) -> str:
    if not iso_text:
        return "unknown"
    return iso_text[:10]


def render_repo_lines(repos: Iterable[dict[str, Any]], max_repos: int) -> list[str]:
    filtered = [repo for repo in repos if not repo.get("fork")]
    filtered.sort(key=lambda repo: repo.get("pushed_at", ""), reverse=True)

    lines: list[str] = []
    for repo in filtered[:max_repos]:
        name = repo.get("name", "unknown")
        html_url = repo.get("html_url", "")
        stars = repo.get("stargazers_count", 0)
        language = repo.get("language") or "n/a"
        pushed = normalize_date(repo.get("pushed_at"))
        lines.append(
            f"- [{name}]({html_url}) - {language}, updated {pushed}, stars {stars}"
        )

    return lines


def summarize_event(event: dict[str, Any]) -> str | None:
    event_type = event.get("type")
    repo_name = (event.get("repo") or {}).get("name", "unknown/unknown")
    repo_url = f"https://github.com/{repo_name}"
    created = normalize_date(event.get("created_at"))
    payload = event.get("payload") or {}

    if event_type == "PushEvent":
        commit_count = len(payload.get("commits") or [])
        return f"- {created}: pushed {commit_count} commit(s) to [{repo_name}]({repo_url})"

    if event_type == "ReleaseEvent":
        action = payload.get("action", "published")
        release = payload.get("release") or {}
        tag = release.get("tag_name", "latest")
        return (
            f"- {created}: {action} release `{tag}` in [{repo_name}]({repo_url})"
        )

    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        pr = payload.get("pull_request") or {}
        number = pr.get("number", "?")
        return f"- {created}: {action} PR #{number} in [{repo_name}]({repo_url})"

    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        issue = payload.get("issue") or {}
        number = issue.get("number", "?")
        return f"- {created}: {action} issue #{number} in [{repo_name}]({repo_url})"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "resource")
        ref_name = payload.get("ref") or ""
        suffix = f" `{ref_name}`" if ref_name else ""
        return f"- {created}: created {ref_type}{suffix} in [{repo_name}]({repo_url})"

    return None


def render_event_lines(events: Iterable[dict[str, Any]], max_events: int) -> list[str]:
    lines: list[str] = []
    for event in events:
        summary = summarize_event(event)
        if summary:
            lines.append(summary)
        if len(lines) >= max_events:
            break
    return lines


def render_activity(username: str, token: str | None, max_repos: int, max_events: int) -> str:
    repos_url = (
        f"https://api.github.com/users/{username}/repos"
        "?type=owner&sort=updated&per_page=100"
    )
    events_url = f"https://api.github.com/users/{username}/events/public?per_page=30"

    repos_data = api_get(repos_url, token)
    events_data = api_get(events_url, token)

    repo_lines = render_repo_lines(repos_data, max_repos)
    event_lines = render_event_lines(events_data, max_events)

    generated_at = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"Last refreshed: {generated_at}",
        f"最近刷新时间：{generated_at}",
        "",
        "### Recently Updated Repositories",
    ]

    if repo_lines:
        lines.extend(repo_lines)
    else:
        lines.append("- No repositories found.")

    lines.extend(["", "### Recent Public Activity"])

    if event_lines:
        lines.extend(event_lines)
    else:
        lines.append("- No recent public activity found.")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()

    readme_path = Path(args.readme)
    build_log_path = Path(args.build_log)

    if not readme_path.exists():
        print(f"README not found: {readme_path}", file=sys.stderr)
        return 1

    original = read_text(readme_path)

    build_log_content = render_build_log(build_log_path, args.max_build_log)
    updated = replace_block(original, START_BUILD_LOG, END_BUILD_LOG, build_log_content)

    existing_activity = extract_block(updated, START_ACTIVITY, END_ACTIVITY)
    activity_content = existing_activity

    if not args.offline:
        username = determine_username(args.username)
        if not username:
            print(
                "Cannot determine GitHub username. Set --username or GITHUB_REPOSITORY.",
                file=sys.stderr,
            )
            return 1

        token = os.getenv("GITHUB_TOKEN")
        try:
            activity_content = render_activity(
                username=username,
                token=token,
                max_repos=args.max_repos,
                max_events=args.max_events,
            )
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            print(
                f"Warning: failed to refresh activity from GitHub API: {exc}. "
                "Keeping existing activity block.",
                file=sys.stderr,
            )

    updated = replace_block(updated, START_ACTIVITY, END_ACTIVITY, activity_content)

    changed = updated != original
    if args.dry_run:
        print("README would be updated." if changed else "No changes needed.")
        return 0

    if changed:
        write_text(readme_path, updated)
        print(f"Updated {readme_path}")
    else:
        print("No changes needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
