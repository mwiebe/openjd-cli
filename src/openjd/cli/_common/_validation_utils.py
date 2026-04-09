# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

from typing import Any
from pathlib import Path

from openjd.model import (
    DecodeValidationError,
    DocumentType,
    EnvironmentTemplate,
    JobTemplate,
    decode_job_template,
    decode_environment_template,
)
from openjd._openjd_rs import (
    decode_job_template_str,
    decode_environment_template_str,
)


def get_doc_type(filepath: Path) -> DocumentType:
    # If the file has a .json extension, treat it strictly
    # as JSON, otherwise treat it as YAML.
    if filepath.suffix.lower() == ".json":
        return DocumentType.JSON
    else:
        return DocumentType.YAML


def _read_template_string(template_file: Path) -> tuple[str, DocumentType]:
    """Read a template file and return (content, format)."""
    if not template_file.exists():
        raise RuntimeError(f"'{str(template_file)}' does not exist.")
    if not template_file.is_file():
        raise RuntimeError(f"'{str(template_file)}' is not a file.")

    filetype = get_doc_type(template_file)

    try:
        template_string = template_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Could not open file '{str(template_file)}': {str(exc)}")

    return template_string, filetype


def read_template(template_file: Path) -> dict[str, Any]:
    """Open a JSON or YAML-formatted file and parse it into a dict.
    Kept for backward compatibility — prefer read_job_template or read_environment_template.
    """
    import json
    import yaml

    content, filetype = _read_template_string(template_file)
    try:
        if filetype == DocumentType.JSON:
            parsed = json.loads(content)
        else:
            parsed = yaml.safe_load(content)
        if not isinstance(parsed, dict):
            raise ValueError()
        return parsed
    except Exception as exc:
        raise RuntimeError(f"'{str(template_file)}' failed checks: {str(exc)}")


def read_job_template(template_file: Path, *, supported_extensions: list[str]) -> JobTemplate:
    """Open a JSON or YAML-formatted file and decode it as a JobTemplate."""
    content, filetype = _read_template_string(template_file)
    try:
        return decode_job_template_str(content, filetype)
    except DecodeValidationError as exc:
        raise RuntimeError(f"'{str(template_file)}' failed checks: {str(exc)}")


def read_environment_template(
    template_file: Path, *, supported_extensions: list[str]
) -> EnvironmentTemplate:
    """Open a JSON or YAML-formatted file and decode it as an EnvironmentTemplate."""
    content, filetype = _read_template_string(template_file)
    try:
        return decode_environment_template_str(content, filetype)
    except DecodeValidationError as exc:
        raise RuntimeError(f"'{str(template_file)}' failed checks: {str(exc)}")
