"""Canonical task, trace, verification, reward, and episode models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Classification = Literal[
    "accepted",
    "compile_error",
    "runtime_error",
    "test_failure",
    "hidden_test_failure",
    "contract_violation",
    "performance_regression",
    "incorrect_tool_use",
    "missing_evidence",
    "incomplete_task",
    "malformed_patch",
]


class CommandSet(BaseModel):
    public: list[list[str]] = Field(min_length=1)
    held_out: list[list[str]] = Field(min_length=1)
    benchmark: list[list[str]] = Field(default_factory=list)


class RewardWeights(BaseModel):
    tool_discovery: float = 0.05
    relevant_tool_selection: float = 0.05
    evidence_gathering: float = 0.10
    patch_correctness: float = 0.25
    public_tests: float = 0.15
    held_out_tests: float = 0.20
    maintainability: float = 0.05
    performance: float = 0.10
    final_explanation: float = 0.05

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> RewardWeights:
        if abs(sum(self.model_dump().values()) - 1.0) > 0.0001:
            raise ValueError("reward weights must sum to 1.0")
        return self


class ResourceLimits(BaseModel):
    max_tool_calls: int = Field(default=40, ge=1, le=200)
    command_timeout_seconds: int = Field(default=30, ge=1, le=120)
    max_output_bytes: int = Field(default=200_000, ge=1_000, le=2_000_000)
    network_enabled: bool = False


class TaskManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,79}$")
    title: str
    language: Literal["python", "java", "rust", "go", "typescript", "cpp"]
    task_type: Literal[
        "bug_fixing",
        "feature_implementation",
        "codebase_refactoring",
        "performance_optimisation",
        "reliability_fix",
        "algorithmic_correction",
    ]
    initial_prompt: str
    baseline_path: str = "baseline"
    public_tests_path: str = "public_tests"
    held_out_tests_path: str = "held_out_tests"
    golden_patch_path: str = "golden/solution.patch"
    incorrect_patch_paths: list[str] = Field(min_length=1)
    expected_trace_path: str = "expected_tool_trace.json"
    required_tools: list[str] = Field(min_length=1)
    required_evidence: list[str] = Field(min_length=1)
    hidden_information: list[str] = Field(min_length=1)
    failure_categories: list[Classification] = Field(min_length=1)
    allowed_changes: list[str] = Field(min_length=1)
    commands: CommandSet
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    performance_threshold: str | None = None
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    reward_weights: RewardWeights = Field(default_factory=RewardWeights)


class ToolCall(BaseModel):
    server: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    ok: bool
    content: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None


class ToolTraceEntry(BaseModel):
    sequence: int = Field(ge=1)
    call: ToolCall
    result: ToolResult
    duration_ms: int = Field(ge=0)


class ProcessEvidence(BaseModel):
    command: list[str]
    exit_code: int | None
    duration_ms: int = Field(ge=0)
    stdout: str
    stderr: str
    timed_out: bool = False
    output_truncated: bool = False


class VerificationResult(BaseModel):
    classification: Classification
    accepted: bool
    changed_files: list[str]
    public_results: list[ProcessEvidence]
    held_out_results: list[ProcessEvidence]
    benchmark_results: list[ProcessEvidence]
    errors: list[str] = Field(default_factory=list)
    candidate_workspace_exclusions_verified: bool
    duration_ms: int = Field(ge=0)


class RewardBreakdown(BaseModel):
    tool_discovery: float = Field(ge=0, le=1)
    relevant_tool_selection: float = Field(ge=0, le=1)
    evidence_gathering: float = Field(ge=0, le=1)
    patch_correctness: float = Field(ge=0, le=1)
    public_tests: float = Field(ge=0, le=1)
    held_out_tests: float = Field(ge=0, le=1)
    maintainability: float = Field(ge=0, le=1)
    performance: float = Field(ge=0, le=1)
    final_explanation: float = Field(ge=0, le=1)
    total: float = Field(ge=0, le=100)


class Episode(BaseModel):
    schema_version: str = "1.0"
    episode_id: str
    task_id: str
    initial_prompt: str
    available_servers: list[str]
    tool_trace: list[ToolTraceEntry]
    patch_sha256: str
    final_explanation: str
    verification: VerificationResult
    reward: RewardBreakdown
    started_at: datetime
    completed_at: datetime
