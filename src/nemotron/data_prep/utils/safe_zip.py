# Copyright (c) 2026, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Safe zip extraction helpers for local data-prep archives."""

from __future__ import annotations

import shutil
import zipfile
from collections.abc import Iterable
from pathlib import Path, PurePosixPath, PureWindowsPath


def _member_name(member: zipfile.ZipInfo | str) -> str:
    return member.filename if isinstance(member, zipfile.ZipInfo) else member


def safe_zip_member_target(
    member: zipfile.ZipInfo | str,
    output_dir: Path,
) -> Path:
    """Return the extraction target for a zip member or raise on traversal.

    Rejects absolute POSIX paths, Windows drive/absolute paths, ``..`` path
    components, and any path whose resolved target would leave ``output_dir``.
    Backslashes are treated as path separators so Windows-style traversal is
    rejected even on POSIX hosts.
    """
    name = _member_name(member)
    normalized = name.replace("\\", "/")
    pure_posix = PurePosixPath(normalized)
    pure_windows = PureWindowsPath(name)

    if (
        not normalized
        or pure_posix.is_absolute()
        or pure_windows.is_absolute()
        or pure_windows.drive
    ):
        raise ValueError(
            f"Unsafe zip member path {name!r}: absolute paths are not allowed"
        )
    if ".." in pure_posix.parts:
        raise ValueError(f"Unsafe zip member path {name!r}: '..' traversal is not allowed")

    root = output_dir.resolve()
    target = (root / pure_posix).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"Unsafe zip member path {name!r}: resolved target escapes {root}"
        ) from exc
    return target


def validate_zip_members(
    zf: zipfile.ZipFile,
    output_dir: Path,
    members: Iterable[zipfile.ZipInfo] | None = None,
) -> list[zipfile.ZipInfo]:
    """Validate all zip member paths before extraction starts."""
    infos = list(members if members is not None else zf.infolist())
    for member in infos:
        safe_zip_member_target(member, output_dir)
    return infos


def safe_extract_zip_member(
    zf: zipfile.ZipFile,
    member: zipfile.ZipInfo,
    output_dir: Path,
) -> Path:
    """Extract one prevalidated zip member under ``output_dir``."""
    target = safe_zip_member_target(member, output_dir)
    if member.is_dir():
        target.mkdir(parents=True, exist_ok=True)
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(member) as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    return target


def safe_extract_zip(
    zf: zipfile.ZipFile,
    output_dir: Path,
    members: Iterable[zipfile.ZipInfo] | None = None,
) -> list[Path]:
    """Validate then extract zip members under ``output_dir``."""
    infos = validate_zip_members(zf, output_dir, members=members)
    return [safe_extract_zip_member(zf, member, output_dir) for member in infos]


__all__ = [
    "safe_extract_zip",
    "safe_extract_zip_member",
    "safe_zip_member_target",
    "validate_zip_members",
]
