"""Contract schema loading and validation.

Single authority for validating records against the versioned schemas in
contracts/schemas/. All adapters must validate their outputs through this
module so schema drift fails loudly in one place.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class ContractError(ValueError):
    """A record failed contract validation."""

    def __init__(self, contract: str, errors: list[str]):
        self.contract = contract
        self.errors = errors
        super().__init__(f"{contract}: " + "; ".join(errors))


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def schemas_dir() -> Path:
    return repo_root() / "contracts" / "schemas"


@lru_cache(maxsize=None)
def load_schema(contract: str) -> dict[str, Any]:
    """Load a schema by contract key, e.g. ``routing-decision.v1``."""
    path = schemas_dir() / f"{contract}.schema.json"
    if not path.is_file():
        raise ContractError(contract, [f"schema not found: {path}"])
    schema = json.loads(path.read_text())
    Draft202012Validator.check_schema(schema)
    return schema


@lru_cache(maxsize=None)
def _validator(contract: str) -> Draft202012Validator:
    return Draft202012Validator(load_schema(contract), format_checker=FormatChecker())


def validate(contract: str, record: dict[str, Any]) -> dict[str, Any]:
    """Validate ``record`` against ``contract``; return the record or raise."""
    errors = []
    for err in sorted(_validator(contract).iter_errors(record), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.path) or "<root>"
        errors.append(f"{loc}: {err.message}")
    if errors:
        raise ContractError(contract, errors)
    return record


def is_valid(contract: str, record: dict[str, Any]) -> bool:
    try:
        validate(contract, record)
    except ContractError:
        return False
    return True
