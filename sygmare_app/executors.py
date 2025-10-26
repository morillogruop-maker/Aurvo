from __future__ import annotations

import shutil
import subprocess
import sys
from time import perf_counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .models import BuildKind, Component
from .statuses import BuildStatus


@dataclass
class CommandResult:
    status: BuildStatus
    details: Optional[str] = None
    duration: float | None = None


def command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def shlex_quote(arg: str) -> str:
    if not arg:
        return "''"
    if all(ch.isalnum() or ch in "@%_=+,-./" for ch in arg):
        return arg
    return "'" + arg.replace("'", "'\\''") + "'"


def readable_cmd(cmd: Iterable[str]) -> str:
    return " ".join(shlex_quote(part) for part in cmd)


def run_command(cmd: List[str], *, cwd: Optional[Path], dry_run: bool) -> subprocess.CompletedProcess:
    display_cwd = f" (cwd={cwd})" if cwd else ""
    print(f"    → {readable_cmd(cmd)}{display_cwd}")
    if dry_run:
        return subprocess.CompletedProcess(cmd, 0, "", "")

    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    if result.stdout:
        for line in result.stdout.splitlines():
            print(f"      {line}")
    if result.returncode != 0:
        print(f"      ✖ Command exited with code {result.returncode}")
    return result


class PythonBuilder:
    def build(self, component: Component, *, dry_run: bool) -> CommandResult:
        if not component.path.exists():
            message = f"Ruta {component.path} no encontrada."
            print(f"  ⚠️  {component.name}: {message}")
            return CommandResult(BuildStatus.MISSING, message)

        if component.path.is_file():
            python_files = [component.path] if component.path.suffix == ".py" else []
        else:
            python_files = list(component.path.rglob("*.py"))

        if not python_files:
            message = "No se encontraron archivos Python para compilar."
            print(f"  ⚠️  {component.name}: {message}")
            return CommandResult(BuildStatus.SKIPPED, message)

        if component.path.is_file():
            cmd = [sys.executable, "-m", "py_compile", str(component.path)]
            cwd = component.path.parent
        else:
            cmd = [sys.executable, "-m", "compileall", str(component.path)]
            cwd = None

        started = perf_counter()
        result = run_command(cmd, cwd=cwd, dry_run=dry_run)
        duration = perf_counter() - started
        status = BuildStatus.BUILT if result.returncode == 0 else BuildStatus.FAILED
        return CommandResult(status, duration=duration)


class NodeBuilder:
    def build(self, component: Component, *, dry_run: bool) -> CommandResult:
        package_json = component.path / "package.json"
        if not component.path.exists() or not package_json.exists():
            message = f"package.json no encontrado en {component.path}"
            print(f"  ⚠️  {component.name}: {message}")
            return CommandResult(BuildStatus.MISSING, message)

        if not command_exists("npm"):
            message = "npm no está instalado en este entorno."
            print(f"  ⚠️  {component.name}: {message}")
            return CommandResult(BuildStatus.SKIPPED, message)

        commands = component.normalized_commands() or [["npm", "install"], ["npm", "run", "build"]]
        status = BuildStatus.BUILT
        elapsed = 0.0
        for cmd in commands:
            started = perf_counter()
            result = run_command(cmd, cwd=component.path, dry_run=dry_run)
            elapsed += perf_counter() - started
            if result.returncode != 0:
                status = BuildStatus.FAILED
                break
        return CommandResult(status, duration=elapsed if elapsed > 0 else None)


class ShellBuilder:
    def build(self, component: Component, *, dry_run: bool) -> CommandResult:
        if not component.path.exists():
            message = f"script {component.path} no encontrado"
            print(f"  ⚠️  {component.name}: {message}")
            return CommandResult(BuildStatus.MISSING, message)

        if not component.path.is_file():
            message = f"Se esperaba un archivo ejecutable y se encontró {component.path}."
            print(f"  ⚠️  {component.name}: {message}")
            return CommandResult(BuildStatus.FAILED, message)

        if not dry_run:
            current_mode = component.path.stat().st_mode
            component.path.chmod(current_mode | 0o111)

        elapsed = 0.0
        if command_exists("shellcheck"):
            started = perf_counter()
            result = run_command(["shellcheck", str(component.path)], cwd=None, dry_run=dry_run)
            elapsed += perf_counter() - started
            if result.returncode != 0:
                return CommandResult(BuildStatus.FAILED, "shellcheck falló", elapsed)

        for cmd in component.normalized_commands():
            started = perf_counter()
            result = run_command(cmd, cwd=component.path.parent, dry_run=dry_run)
            elapsed += perf_counter() - started
            if result.returncode != 0:
                return CommandResult(BuildStatus.FAILED, duration=elapsed)

        return CommandResult(BuildStatus.BUILT, duration=elapsed if elapsed > 0 else None)


def builder_registry() -> Dict[BuildKind, object]:
    return {
        BuildKind.PYTHON: PythonBuilder(),
        BuildKind.NODE: NodeBuilder(),
        BuildKind.SHELL: ShellBuilder(),
    }


__all__ = [
    "CommandResult",
    "PythonBuilder",
    "NodeBuilder",
    "ShellBuilder",
    "builder_registry",
    "command_exists",
    "run_command",
]
