# Task Knowledge

<!-- METADATA:SESSION=1 -->

- The task182 run-spec docs URL pin is intentionally the assignment commit
  `510b6eec33edece3d212a3187b16db3d1b4a8a15`, even after rebasing the branch
  onto newer main `df45842edade40c19fd0496f3844ef20653a94cc`.
- Static tests should read recipe entrypoints as text only; importing the
  entrypoints would cross the static-only boundary and may pull heavy runtime
  dependencies.
