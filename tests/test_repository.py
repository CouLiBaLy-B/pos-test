from __future__ import annotations

import json
import stat
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


EXPECTED_FILES = [
    ROOT / "README.md",
    ROOT / ".env.example",
    ROOT / ".gitignore",
    ROOT / "Dockerfile.api",
    ROOT / "Makefile",
    ROOT / "docker-compose.yml",
    ROOT / "requirements.txt",
    ROOT / "requirements-dev.txt",
    ROOT / "CHANGELOG.md",
    ROOT / "assistant_api" / "config.py",
    ROOT / "assistant_api" / "main.py",
    ROOT / "assistant_api" / "models.py",
    ROOT / "assistant_api" / "service.py",
    ROOT / "config" / "claude" / "settings.json",
    ROOT / "config" / "litellm" / "config.yaml",
    ROOT / "docs" / "api.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "models.md",
    ROOT / "docs" / "roadmap-v0.2.0.md",
    ROOT / "docs" / "security.md",
    ROOT / "scripts" / "bootstrap.sh",
    ROOT / "scripts" / "healthcheck.sh",
    ROOT / "scripts" / "apply-branch-protection.sh",
    ROOT / "scripts" / "run-tests.sh",
    ROOT / "scripts" / "sync-labels.sh",
    ROOT / "scripts" / "setup-claude.sh",
    ROOT / "scripts" / "start.sh",
    ROOT / "scripts" / "stop.sh",
    ROOT / "skills" / "debug-loop" / "SKILL.md",
    ROOT / "skills" / "feature-dev" / "SKILL.md",
    ROOT / "skills" / "git-workflow" / "SKILL.md",
    ROOT / "skills" / "write-tests" / "SKILL.md",
    ROOT / ".github" / "CODEOWNERS",
    ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
    ROOT / ".github" / "labeler.yml",
    ROOT / ".github" / "labels.json",
    ROOT / ".github" / "workflows" / "ci.yml",
    ROOT / ".github" / "workflows" / "pr-labeler.yml",
    ROOT / ".github" / "workflows" / "release.yml",
    ROOT / "tests" / "test_assistant_api.py",
]


def test_expected_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in EXPECTED_FILES if not path.exists()]
    assert not missing, f"Missing files: {missing}"


def test_claude_settings_json_is_valid() -> None:
    data = json.loads((ROOT / "config" / "claude" / "settings.json").read_text())

    assert data["env"]["ANTHROPIC_BASE_URL"] == "http://localhost:4000"
    assert data["env"]["ENABLE_TOOL_SEARCH"] == "true"
    assert {"filesystem", "playwright"}.issubset(data["mcpServers"].keys())
    assert any(item.startswith("Bash(git:") for item in data["permissions"]["allow"])


def test_litellm_config_is_valid_yaml() -> None:
    data = yaml.safe_load((ROOT / "config" / "litellm" / "config.yaml").read_text())

    assert "model_list" in data
    model_names = {item["model_name"] for item in data["model_list"]}
    assert "claude-3-5-sonnet-20241022" in model_names
    assert "claude-3-5-haiku-20241022" in model_names

    for item in data["model_list"]:
        params = item["litellm_params"]
        assert params["model"] == "openai/qwen3-coder"
        assert params["api_base"] == "http://vllm:8000/v1"


def test_docker_compose_has_required_services() -> None:
    data = yaml.safe_load((ROOT / "docker-compose.yml").read_text())

    assert "services" in data
    services = data["services"]
    assert {"vllm", "litellm", "assistant-api"}.issubset(services.keys())

    vllm_command = services["vllm"]["command"]
    assert "--enable-auto-tool-choice" in vllm_command
    assert "--tool-call-parser" in vllm_command
    assert "--enable-prefix-caching" in vllm_command

    assert services["litellm"]["depends_on"]["vllm"]["condition"] == "service_healthy"
    assert services["assistant-api"]["depends_on"]["litellm"]["condition"] == "service_healthy"


def test_skills_have_front_matter_and_description() -> None:
    for skill_file in sorted((ROOT / "skills").glob("*/SKILL.md")):
        content = skill_file.read_text().strip()
        assert content.startswith("---\n"), f"{skill_file} should start with front matter"
        assert "\nname:" in content, f"{skill_file} should declare a skill name"
        assert "\ndescription:" in content, f"{skill_file} should declare a description"


def test_scripts_have_shebang_and_are_executable() -> None:
    for script in sorted((ROOT / "scripts").glob("*.sh")):
        first_line = script.read_text().splitlines()[0]
        mode = script.stat().st_mode
        assert first_line == "#!/usr/bin/env bash", f"Unexpected shebang in {script.name}"
        assert mode & stat.S_IXUSR, f"{script.name} must be executable by the owner"


def test_readme_mentions_test_and_setup_commands() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "make up" in readme
    assert "make health" in readme
    assert "make setup-claude" in readme
    assert "make test" in readme
    assert "http://localhost:8080/docs" in readme
    assert "/api/v1/chat" in readme


def test_github_community_files_are_present_and_valid() -> None:
    codeowners = (ROOT / ".github" / "CODEOWNERS").read_text()
    assert "@CouLiBaLy-B" in codeowners

    pr_template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text()
    assert "Checklist" in pr_template

    bug_template = yaml.safe_load((ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml").read_text())
    feature_template = yaml.safe_load((ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml").read_text())
    config_template = yaml.safe_load((ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml").read_text())

    assert bug_template["name"] == "Bug report"
    assert feature_template["name"] == "Feature request"
    assert config_template["blank_issues_enabled"] is False


def test_readme_mentions_badges_and_branch_protection() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "actions/workflows/release.yml/badge.svg" in readme
    assert "make protect-branch" in readme
    assert "make sync-labels" in readme
    assert "develop" in readme
    assert "code owner review" in readme.lower()


def test_labeler_and_labels_config_are_valid() -> None:
    labeler = yaml.safe_load((ROOT / ".github" / "labeler.yml").read_text())
    labels = json.loads((ROOT / ".github" / "labels.json").read_text())

    label_names = {item["name"] for item in labels}
    assert "documentation" in label_names
    assert "ci-cd" in label_names
    assert "roadmap" in label_names
    assert "documentation" in labeler
    assert "automation" in labeler


def test_roadmap_mentions_develop_and_v020() -> None:
    roadmap = (ROOT / "docs" / "roadmap-v0.2.0.md").read_text()

    assert "Roadmap v0.2.0" in roadmap
    assert "develop" in roadmap
    assert "main" in roadmap
