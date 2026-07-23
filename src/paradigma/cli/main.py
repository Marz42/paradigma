"""Unified Paradigma command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ..application.configuration import config_validate_outcome
from ..application.diagnosis import diagnose_outcome
from ..application.indexing import index_rebuild_outcome, index_verify_outcome
from ..application.tasks import archive_outcome
from ..application.validation import check_outcome
from ..application.versioning import version_outcome
from ..diagnostics import Diagnostic
from ..errors import DiagnosticError, ParadigmaError
from ..parser import ParseFailure
from ..application.outcomes import CommandOutcome
from .output import render


def _leaf_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--project", type=Path, default=Path.cwd())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pd", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    version = commands.add_parser("version", help="report version dimensions")
    _leaf_options(version)

    config = commands.add_parser("config", help="configuration commands")
    config_commands = config.add_subparsers(dest="config_command", required=True)
    config_validate = config_commands.add_parser("validate", help="validate config")
    _leaf_options(config_validate)

    check = commands.add_parser("check", help="run repository quality gates")
    _leaf_options(check)

    diagnose = commands.add_parser("diagnose", help="compare project with upstream")
    diagnose.add_argument("--upstream", type=Path, required=True)
    _leaf_options(diagnose)

    index = commands.add_parser("index", help="derived index commands")
    index_commands = index.add_subparsers(dest="index_command", required=True)
    index_rebuild = index_commands.add_parser("rebuild", help="rebuild indexes")
    _leaf_options(index_rebuild)
    index_verify = index_commands.add_parser("verify", help="verify indexes")
    _leaf_options(index_verify)

    task = commands.add_parser("task", help="task lifecycle commands")
    task_commands = task.add_subparsers(dest="task_command", required=True)
    task_archive = task_commands.add_parser("archive", help="archive active task")
    task_archive.add_argument("--write", action="store_true")
    task_archive.add_argument("--force", action="store_true")
    _leaf_options(task_archive)
    return parser


def _dispatch(args: argparse.Namespace) -> CommandOutcome:
    root = args.project.resolve()
    if args.command == "version":
        return version_outcome(root, dry_run=args.dry_run)
    if args.command == "config" and args.config_command == "validate":
        return config_validate_outcome(root, dry_run=args.dry_run)
    if args.command == "check":
        return check_outcome(root, dry_run=args.dry_run)
    if args.command == "diagnose":
        return diagnose_outcome(root, args.upstream, dry_run=args.dry_run)
    if args.command == "index" and args.index_command == "rebuild":
        return index_rebuild_outcome(root, dry_run=args.dry_run)
    if args.command == "index" and args.index_command == "verify":
        return index_verify_outcome(root, dry_run=args.dry_run)
    if args.command == "task" and args.task_command == "archive":
        return archive_outcome(
            root,
            dry_run=args.dry_run or not args.write,
            force=args.force,
        )
    raise AssertionError("unreachable command")


def _error_outcome(command: str, error: Exception) -> CommandOutcome:
    if isinstance(error, DiagnosticError):
        diagnostic = error.diagnostic
        exit_code = error.exit_code
    elif isinstance(error, ParadigmaError):
        diagnostic = Diagnostic(error.code, str(error), command)
        exit_code = error.exit_code
    else:
        diagnostic = Diagnostic("PD_UNEXPECTED_ERROR", str(error), command)
        exit_code = 1
    return CommandOutcome(
        command=command,
        diagnostics=(diagnostic,),
        exit_code_override=exit_code,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = " ".join(
        str(value)
        for value in (
            args.command,
            getattr(args, "config_command", None),
            getattr(args, "index_command", None),
            getattr(args, "task_command", None),
        )
        if value
    )
    try:
        outcome = _dispatch(args)
    except (OSError, UnicodeError, ParadigmaError, ParseFailure) as error:
        outcome = _error_outcome(command, error)
    print(render(outcome, args.output_format))
    return outcome.exit_code


if __name__ == "__main__":
    sys.exit(main())
