from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from mcp_rl_lab.verifier import verify_patch
from tests.conftest import ROOT


def test_python_golden_is_accepted_and_wrong_patch_is_rejected(python_task) -> None:
    golden = verify_patch(python_task, python_task.path(python_task.manifest.golden_patch_path))
    wrong = verify_patch(python_task, python_task.path("incorrect_patches/linear-backoff.patch"))
    assert golden.accepted and golden.classification == "accepted"
    assert not wrong.accepted and wrong.classification == "hidden_test_failure"
    assert golden.candidate_workspace_exclusions_verified


def test_verification_result_matches_schema(python_task) -> None:
    result = verify_patch(python_task, python_task.path(python_task.manifest.golden_patch_path))
    schema = json.loads((ROOT / "schemas/verification.schema.json").read_text())
    Draft202012Validator(schema).validate(result.model_dump(mode="json"))
