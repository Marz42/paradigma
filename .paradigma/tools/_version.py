"""Shared Paradigma version model helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from _paradigma_yaml import load_flat_yaml_file


SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class VersionModelError(ValueError):
    """Raised when required version metadata cannot be read."""


@dataclass(frozen=True)
class VersionInfo:
    distribution_version: str
    installed_distribution_version: str
    config_schema_version: str
    okf_version: str
    document_schema_version: str
    legacy_harness_version: str | None = None
    legacy_config_schema_version: str | None = None
    legacy_document_schema_version: str | None = None


def read_top_level_scalars(path: Path) -> dict[str, str]:
    flattened = load_flat_yaml_file(path, missing_ok=True)
    return {
        key: value
        for key, value in flattened.items()
        if "." not in key and isinstance(value, str)
    }


def read_distribution_version(root: Path) -> str:
    version_path = root / "VERSION"
    if not version_path.exists():
        raise VersionModelError("missing root VERSION")
    version = version_path.read_text(encoding="utf-8-sig").strip()
    if not version:
        raise VersionModelError("root VERSION is empty")
    return version


def read_installed_distribution_version(root: Path) -> tuple[str, str | None]:
    config = read_top_level_scalars(root / ".paradigma" / "config.yaml")
    installed = config.get("installed_distribution_version", "")
    legacy = config.get("paradigma_harness_version", "") or None
    return installed or legacy or "", legacy


def read_version_info(root: Path) -> VersionInfo:
    config = read_top_level_scalars(root / ".paradigma" / "config.yaml")
    schema = read_top_level_scalars(
        root / ".paradigma" / "schemas" / "paradigma-types.schema.yaml"
    )
    installed, legacy = read_installed_distribution_version(root)
    return VersionInfo(
        distribution_version=read_distribution_version(root),
        installed_distribution_version=installed,
        config_schema_version=config.get("config_schema_version", ""),
        okf_version=config.get("okf_version", ""),
        document_schema_version=schema.get("document_schema_version", ""),
        legacy_harness_version=legacy,
        legacy_config_schema_version=config.get("schema_version") or None,
        legacy_document_schema_version=schema.get("schema_version") or None,
    )


def validate_version_info(info: VersionInfo) -> list[str]:
    errors: list[str] = []
    required = {
        "distribution_version": info.distribution_version,
        "installed_distribution_version": info.installed_distribution_version,
        "config_schema_version": info.config_schema_version,
        "okf_version": info.okf_version,
        "document_schema_version": info.document_schema_version,
    }
    for field, value in required.items():
        if not value:
            errors.append(f"missing {field}")

    if info.distribution_version and not SEMVER_PATTERN.fullmatch(
        info.distribution_version
    ):
        errors.append(
            f"distribution_version is not SemVer: {info.distribution_version}"
        )
    if (
        info.installed_distribution_version
        and not SEMVER_PATTERN.fullmatch(info.installed_distribution_version)
    ):
        errors.append(
            "installed_distribution_version is not SemVer: "
            f"{info.installed_distribution_version}"
        )
    if (
        info.distribution_version
        and info.installed_distribution_version
        and info.distribution_version != info.installed_distribution_version
    ):
        errors.append(
            "installed_distribution_version does not match root VERSION: "
            f"{info.installed_distribution_version} != {info.distribution_version}"
        )
    if info.legacy_harness_version is not None:
        errors.append(
            "legacy paradigma_harness_version is present; migrate to "
            "installed_distribution_version"
        )
    if info.legacy_config_schema_version is not None:
        errors.append(
            "legacy config schema_version is present; migrate to "
            "config_schema_version"
        )
    if info.legacy_document_schema_version is not None:
        errors.append(
            "legacy registry schema_version is present; migrate to "
            "document_schema_version"
        )
    return errors
