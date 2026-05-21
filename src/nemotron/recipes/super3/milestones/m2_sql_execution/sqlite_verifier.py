# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0

"""Safe local SQLite execution scaffold for ``sql_execution_match``.

This is the Session 1 M2 bridge between the M0 BIRD ``sql_text_to_query``
environment and a future DB/container runner. It intentionally uses only
an in-memory SQLite database built from record-local schema + fixtures:
no network, no external DB service, and no host database path.
"""

from __future__ import annotations

import re
import sqlite3
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


JsonDict = dict[str, Any]

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_LINE_COMMENT_RE = re.compile(r"--[^\n\r]*")
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_FORBIDDEN_QUERY_TOKEN_RE = re.compile(
    r"\b("
    r"attach|alter|create|delete|detach|drop|insert|pragma|replace|truncate|"
    r"update|vacuum"
    r")\b",
    re.IGNORECASE,
)
_FORBIDDEN_SCHEMA_TOKEN_RE = re.compile(
    r"\b(attach|detach|load_extension|vacuum)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class SqlExecutionResult:
    """Score + diagnostics emitted by the local SQL execution scaffold."""

    score: float
    diagnostics: JsonDict


def _nested_sql_context(context: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not context:
        return {}
    nested = context.get("sql_execution")
    if isinstance(nested, Mapping):
        return nested
    return context


def has_sqlite_execution_context(context: Mapping[str, Any] | None) -> bool:
    """Return true when *context* has enough local data to execute SQL."""

    sql_context = _nested_sql_context(context)
    if sql_context.get("available") is False:
        return False
    engine = str(sql_context.get("engine") or "sqlite").lower()
    if engine != "sqlite":
        return False
    return bool(
        sql_context.get("schema_sql")
        or sql_context.get("fixture_rows")
        or sql_context.get("sqlite_fixture_rows")
    )


def _strip_sql_comments(sql: str) -> str:
    return _LINE_COMMENT_RE.sub("", _BLOCK_COMMENT_RE.sub("", sql))


def _single_readonly_statement(sql: Any) -> tuple[str | None, str | None]:
    text = str(sql or "").strip()
    if not text:
        return None, "empty SQL"
    text_without_comments = _strip_sql_comments(text).strip()
    while text_without_comments.endswith(";"):
        text_without_comments = text_without_comments[:-1].rstrip()
    if not text_without_comments:
        return None, "empty SQL"
    if ";" in text_without_comments:
        return None, "multiple SQL statements are not allowed"
    lowered = text_without_comments.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        return None, "only SELECT/WITH queries are allowed"
    if _FORBIDDEN_QUERY_TOKEN_RE.search(lowered):
        return None, "query contains a non-read-only SQL token"
    return text_without_comments, None


def _quote_identifier(identifier: str) -> str:
    if not _IDENTIFIER_RE.match(identifier):
        raise ValueError(f"unsafe SQLite identifier {identifier!r}")
    return f'"{identifier}"'


def _sqlite_type(value: Any) -> str:
    if isinstance(value, bool):
        return "INTEGER"
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    if isinstance(value, (bytes, bytearray)):
        return "BLOB"
    return "TEXT"


def _infer_columns(rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    columns: dict[str, str] = {}
    for row in rows:
        for key, value in row.items():
            if key not in columns and value is not None:
                columns[key] = _sqlite_type(value)
            elif key not in columns:
                columns[key] = "TEXT"
    return columns


def _create_fixture_table(
    conn: sqlite3.Connection,
    table_name: str,
    rows: Sequence[Mapping[str, Any]],
) -> None:
    columns = _infer_columns(rows)
    if not columns:
        return
    table = _quote_identifier(table_name)
    column_defs = ", ".join(
        f"{_quote_identifier(name)} {sqlite_type}"
        for name, sqlite_type in columns.items()
    )
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table} ({column_defs})")
    column_names = list(columns)
    placeholders = ", ".join("?" for _ in column_names)
    quoted_columns = ", ".join(_quote_identifier(name) for name in column_names)
    conn.executemany(
        f"INSERT INTO {table} ({quoted_columns}) VALUES ({placeholders})",
        [[row.get(name) for name in column_names] for row in rows],
    )


def _load_fixture_rows(conn: sqlite3.Connection, context: Mapping[str, Any]) -> None:
    raw_fixtures = context.get("fixture_rows") or context.get("sqlite_fixture_rows") or {}
    if not isinstance(raw_fixtures, Mapping):
        raise ValueError("fixture_rows must be a mapping of table name to row list")
    for table_name, rows in raw_fixtures.items():
        if not isinstance(table_name, str):
            raise ValueError("fixture table names must be strings")
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
            raise ValueError(f"fixture_rows[{table_name!r}] must be a list of mappings")
        normalized_rows: list[Mapping[str, Any]] = []
        for index, row in enumerate(rows):
            if not isinstance(row, Mapping):
                raise ValueError(
                    f"fixture_rows[{table_name!r}][{index}] must be a mapping"
                )
            normalized_rows.append(row)
        _create_fixture_table(conn, table_name, normalized_rows)


def _build_connection(context: Mapping[str, Any]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    # Bounded progress keeps accidental cross joins from hanging local tests.
    max_steps = int(context.get("max_sql_steps") or 100_000)
    step_counter = {"count": 0}

    def _progress() -> int:
        step_counter["count"] += 1
        return 1 if step_counter["count"] > max_steps else 0

    conn.set_progress_handler(_progress, 100)
    schema_sql = str(context.get("schema_sql") or "").strip()
    if schema_sql:
        if _FORBIDDEN_SCHEMA_TOKEN_RE.search(_strip_sql_comments(schema_sql)):
            raise ValueError("schema_sql contains an unsafe SQLite token")
        conn.executescript(schema_sql)
    _load_fixture_rows(conn, context)
    return conn


def _execute_select(
    conn: sqlite3.Connection,
    sql: str,
    *,
    label: str,
) -> tuple[list[tuple[Any, ...]] | None, JsonDict]:
    readonly_sql, error = _single_readonly_statement(sql)
    if error:
        return None, {f"{label}_error": error}
    assert readonly_sql is not None
    try:
        cursor = conn.execute(readonly_sql)
        rows = [tuple(row) for row in cursor.fetchall()]
    except sqlite3.Error as exc:
        return None, {f"{label}_error": str(exc)}
    return rows, {f"{label}_row_count": len(rows)}


def _normalize_cell(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 12)
    if isinstance(value, bytes):
        return value.hex()
    return value


def _normalize_rows(rows: Sequence[Sequence[Any]]) -> list[tuple[Any, ...]]:
    return [tuple(_normalize_cell(cell) for cell in row) for row in rows]


def _rows_match(
    candidate_rows: Sequence[Sequence[Any]],
    expected_rows: Sequence[Sequence[Any]],
    *,
    order_sensitive: bool,
) -> bool:
    norm_candidate = _normalize_rows(candidate_rows)
    norm_expected = _normalize_rows(expected_rows)
    if order_sensitive:
        return norm_candidate == norm_expected
    return Counter(norm_candidate) == Counter(norm_expected)


def score_sqlite_execution_match(
    candidate: Any,
    expected: Any,
    context: Mapping[str, Any] | None,
) -> SqlExecutionResult:
    """Execute candidate and gold SQL against an in-memory SQLite fixture.

    If *context* lacks executable schema/fixtures, callers should use the
    M0 normalized-string fallback instead; this function returns a diagnostic
    miss rather than pretending execution happened.
    """

    sql_context = _nested_sql_context(context)
    diagnostics: JsonDict = {
        "sql_execution_mode": "local_sqlite",
        "sql_execution_engine": "sqlite",
    }
    if not has_sqlite_execution_context(context):
        diagnostics["sql_execution_skipped"] = "missing local SQLite schema/fixtures"
        return SqlExecutionResult(score=0.0, diagnostics=diagnostics)

    try:
        conn = _build_connection(sql_context)
    except (sqlite3.Error, TypeError, ValueError) as exc:
        diagnostics["sql_execution_setup_error"] = str(exc)
        return SqlExecutionResult(score=0.0, diagnostics=diagnostics)

    try:
        expected_rows, expected_diag = _execute_select(
            conn,
            str(expected or ""),
            label="expected",
        )
        diagnostics.update(expected_diag)
        if expected_rows is None:
            diagnostics["sql_execution_error"] = diagnostics.get("expected_error")
            return SqlExecutionResult(score=0.0, diagnostics=diagnostics)

        candidate_rows, candidate_diag = _execute_select(
            conn,
            str(candidate or ""),
            label="candidate",
        )
        diagnostics.update(candidate_diag)
        if candidate_rows is None:
            diagnostics["sql_execution_error"] = diagnostics.get("candidate_error")
            return SqlExecutionResult(score=0.0, diagnostics=diagnostics)
    finally:
        conn.close()

    order_sensitive = bool(sql_context.get("order_sensitive"))
    matched = _rows_match(
        candidate_rows,
        expected_rows,
        order_sensitive=order_sensitive,
    )
    diagnostics["sql_execution_match"] = matched
    diagnostics["sql_execution_order_sensitive"] = order_sensitive
    return SqlExecutionResult(score=1.0 if matched else 0.0, diagnostics=diagnostics)
