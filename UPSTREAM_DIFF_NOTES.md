# Upstream diff notes

Every difference between a vendored module under
`src/prompt_master/prompt_engine/upstream/` and the corresponding file in the
pinned Prompt-Master-LD checkout must be declared here. `tools/check_upstream_sync.py`
parses this file and fails the build on any undeclared change.

## Status

**No modules are vendored yet.** The upstream repository
`Brojakhoeman/Prompt-Master-LD` was not reachable when this file was created, so
the port has not started. See "Blocked" below.

## What does not need an entry

The sync checker auto-approves hunks in which every changed line is an import
statement or a blank/comment line. These are the packaging edits the porting
contract permits:

- rewriting an absolute import as a package-relative import,
- deleting a ComfyUI import,
- deleting a Torch import that only served tensor conversion,
- adding `from __future__ import annotations` or a typing-only import.

Everything else needs an entry, including any added type annotation, because an
annotation edit touches the same lines as behavior.

## Entry format

The parser expects a heading naming the module, followed by four fields. Line
numbers are 1-based and inclusive.

```
### accents.py
- Original lines: 12-14
- New lines: 12-16
- Reason: <what changed and why the porting contract permits it>
- Behavior unchanged: yes
```

`Behavior unchanged: yes` is a required confirmation, not a formality: it
asserts that `tools/compare_upstream_engine.py` produces identical system
prompts, user prompts, base negatives, budgets, and frame counts across this
change. A hunk whose entry lacks the confirmation fails the check.

An entry may cover several adjacent hunks by widening its ranges, but prefer one
entry per logical change so the reason stays specific.

## Approved differences

_None. No modules have been vendored._

## Blocked

The port could not be started because the source-of-truth repository is not
reachable from the build environment:

| Probe | Result |
| --- | --- |
| `git ls-remote https://github.com/psf/requests.git` (public control) | succeeds |
| `git ls-remote https://github.com/Brojakhoeman/Prompt-Master-LD.git` | authentication required |
| `raw.githubusercontent.com/torvalds/linux/master/README` (public control) | 200 |
| `raw.githubusercontent.com/Brojakhoeman/Prompt-Master-LD/main/brain.py` | 404 |
| `raw.githubusercontent.com/Brojakhoeman/Gemma4Prompt/main/README.md` | 404 |

Anonymous access to public GitHub content works from this environment, and every
repository under the `Brojakhoeman` account returns 404 or demands credentials —
not just `Prompt-Master-LD`. The repository is private, renamed, or removed.

To unblock, supply the upstream source by one of:

1. make `Brojakhoeman/Prompt-Master-LD` public, or
2. grant the build environment a credential that can read it, or
3. vendor the eleven engine modules plus the four reference modules into this
   repository directly, together with the upstream commit SHA in
   `src/prompt_master/prompt_engine/UPSTREAM_COMMIT.txt`.

Once the source is present, `tools/check_upstream_sync.py --upstream <path>`
runs without further changes.
