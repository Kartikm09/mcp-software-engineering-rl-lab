from __future__ import annotations

import json

import yaml
from jsonschema import Draft202012Validator

from mcp_rl_lab.task_loader import discover_tasks
from tests.conftest import ROOT


def test_catalogue_contains_six_languages_and_original_tasks() -> None:
    tasks = discover_tasks(ROOT / "tasks")
    assert len(tasks) == 6
    assert {task.manifest.language for task in tasks} == {
        "python",
        "java",
        "rust",
        "go",
        "typescript",
        "cpp",
    }
    assert len({task.manifest.id for task in tasks}) == 6


def test_manifests_are_self_contained_and_network_disabled() -> None:
    for task in discover_tasks(ROOT / "tasks"):
        assert task.manifest.hidden_information
        assert "accepted" in task.manifest.failure_categories
        assert not task.manifest.resource_limits.network_enabled
        assert task.path(task.manifest.golden_patch_path).is_file()
        assert task.path("golden/explanation.md").is_file()
        assert task.path("golden/verification.json").is_file()


def test_task_and_environment_documents_validate_against_json_schema() -> None:
    task_schema = json.loads((ROOT / "schemas/task.schema.json").read_text(encoding="utf-8"))
    environment_schema = json.loads(
        (ROOT / "schemas/environment.schema.json").read_text(encoding="utf-8")
    )
    for manifest in ROOT.glob("tasks/*/*/task.yaml"):
        Draft202012Validator(task_schema).validate(yaml.safe_load(manifest.read_text()))
    descriptors = list(ROOT.glob("environments/*/environment.yaml"))
    assert len(descriptors) == 6
    for descriptor in descriptors:
        Draft202012Validator(environment_schema).validate(yaml.safe_load(descriptor.read_text()))
