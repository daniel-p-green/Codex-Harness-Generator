# Context Management

Preserve the source trail for every summary, decision, and plan update.

## Save

Use `/state-save` before compaction or pauses. Capture tool state, task state, artifact state, decision state, blocked state, and drift risk in `Docs/_working/state/`.

## Load

Use `/state-load` at session start when continuing prior work. Check whether referenced files still exist and whether newer notes or decisions changed the answer.

## Wiki

`Docs/index.md` is the only wiki file loaded by default. Load `Docs/Areas/` and `Docs/Decisions/` pages only when relevant.
