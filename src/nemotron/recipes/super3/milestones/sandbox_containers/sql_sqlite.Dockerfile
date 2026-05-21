# syntax=docker/dockerfile:1.7
#
# sql_sqlite sandbox image for the M2 `sql_text_to_query` local execution
# scaffold. The verifier builds an in-memory SQLite DB from record-local
# schema + fixtures and only executes read-only SELECT/WITH queries.
#
# Caller must pass runtime isolation flags (`--network=none`, `--read-only`,
# `--tmpfs /tmp`, memory/cpu caps). Session 1 tests lint the image shape and
# registry mapping only; no DB container smoke is required in this PR.
FROM python:3.12-slim

# sqlite3 is part of CPython's stdlib in this image. Keep the layer minimal
# so the SQL sandbox does not ship extra tools the verifier does not need.
RUN python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Drop privileges. UID 1000 mirrors the convention most CI runners use.
RUN useradd --create-home --uid 1000 sandboxer
USER sandboxer
WORKDIR /home/sandboxer

CMD ["python", "-c", "import sqlite3, sys; sys.stdout.write(f'sqlite {sqlite3.sqlite_version} ok\\n')"]
