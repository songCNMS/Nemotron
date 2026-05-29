# Task Knowledge

<!-- METADATA:SESSION=3 -->

- The task182 run-spec docs URL pin is intentionally the assignment commit
  `510b6eec33edece3d212a3187b16db3d1b4a8a15`, even after rebasing the branch
  onto newer main `df45842edade40c19fd0496f3844ef20653a94cc`.
- Static tests should read recipe entrypoints as text only; importing the
  entrypoints would cross the static-only boundary and may pull heavy runtime
  dependencies.
- Session 2 added only closeout metadata; no new product-scope knowledge or
  validation change was introduced.
- Task182 was merged to main at
  `90b3122c5b803ed0192ac0dab273473da6a3c52f` from exact tested head
  `6126f54dac84d4b101a01860a383926a31a24b69`.
