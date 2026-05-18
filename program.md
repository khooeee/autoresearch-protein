# autoresearch-protein

This is an experiment to have the LLM do its own protein language-modeling
research.

## Setup

To set up a new experiment series, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date, such as
   `2026-05-17`. The branch `autoresearch/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current
   `main`.
3. **Read the in-scope files**: the repo is small. Read these files for full
   context:
   - `README.md` - repository context and data setup.
   - `prepare_data.py` - fixed data filtering, shuffling, and train/val split.
     Do not modify during a comparable experiment series.
   - `train.py` - the file you modify. Model architecture, optimizer,
     hyperparameters, training loop, batching, and evaluation sampling live here.
   - `results.md` - experiment ledger.
4. **Verify data exists**: check that `data/train.txt` and `data/val.txt` exist.
   If not, tell the human to follow the README data setup and run
   `uv run python prepare_data.py`.
5. **Initialize results.md**: if it does not already contain a clear experiment
   table, add one before the first run. The baseline will be recorded after the
   first run.
6. **Confirm and go**: confirm setup looks good, then begin experimentation.

Once the experiment loop begins, continue autonomously until the human manually
interrupts you.

## Experimentation

Each experiment runs locally with:

```sh
uv run python train.py
```

The goal is simple: get the lowest `FINAL_BEST_VAL_LOSS`. This is validation
cross-entropy, and lower is better.

**What you CAN do:**
- Modify `train.py`. Everything in that file is fair game: model architecture,
  optimizer, learning rate, batch size, context length, tokenization, batching,
  masking, training loop, evaluation cadence, and sampling strategy.
- Make small documentation or ignore-file updates if they help the experiment
  workflow.

**What you CANNOT do:**
- Modify `data/val.txt` or otherwise change the validation data.
- Change the train/validation split inside an ongoing comparable experiment
  series.
- Edit `prepare_data.py` for a comparable run unless the user explicitly starts
  a new data-preparation experiment series.
- Install new packages or add dependencies unless the user explicitly approves.
- Optimize for training loss at the expense of validation loss.

**Simplicity criterion**: all else being equal, simpler is better. A tiny
validation improvement that adds fragile complexity is probably not worth
keeping. A tiny improvement from deleting or simplifying code is excellent. When
deciding whether to keep a change, weigh the validation gain against the added
complexity.

**The first run**: always establish the baseline first by running the training
script as-is and recording the result.

## Output Format

The script prints progress during training and ends with:

```text
FINAL_BEST_VAL_LOSS=1.2345
```

Extract the key metric from a redirected log with:

```sh
grep "^FINAL_BEST_VAL_LOSS=" run.log
```

If useful, also inspect the best progress line:

```sh
grep "^step " run.log | tail -n 5
```

## Logging Results

When an experiment is done, log it in `results.md`. Keep `results.md` as the
human-readable Markdown ledger for this repo.

Use a compact table with these columns:

```md
| Commit | Val loss | Status | Description |
| --- | ---: | --- | --- |
```

Column meanings:

1. `Commit`: short git commit hash, usually 7 characters. Use `none` for the
   initial uncommitted baseline only if no commit exists yet.
2. `Val loss`: `FINAL_BEST_VAL_LOSS`, such as `1.2345`. Use `crash` if the run
   did not produce the metric.
3. `Status`: `keep`, `discard`, or `crash`.
4. `Description`: short text describing the change.

Example:

```md
| Commit | Val loss | Status | Description |
| --- | ---: | --- | --- |
| a1b2c3d | 1.2345 | keep | baseline |
| b2c3d4e | 1.2101 | keep | increase embedding size to 192 |
| c3d4e5f | 1.2600 | discard | reduce dropout to zero |
| d4e5f6a | crash | crash | double context length caused OOM |
```

Commit code changes, but do not commit `results.md` updates unless the user asks
you to make a checkpoint commit that includes the ledger.

## The Experiment Loop

The experiment runs on a dedicated branch, for example `autoresearch/2026-05-17`.

LOOP FOREVER:

1. Look at the git state: current branch, current commit, and dirty files.
2. Pick one experimental idea and edit `train.py` directly.
3. Commit the code change.
4. Run the experiment with redirected output:

   ```sh
   uv run python train.py > run.log 2>&1
   ```

5. Read the result:

   ```sh
   grep "^FINAL_BEST_VAL_LOSS=" run.log
   ```

6. If the grep output is empty, the run crashed. Read the stack trace:

   ```sh
   tail -n 80 run.log
   ```

   If the crash is a simple typo or shape bug, fix it and rerun. If the idea is
   fundamentally broken or too expensive, log `crash` in `results.md`, reset the
   branch back to the pre-experiment commit, and move on.
7. Record the result in `results.md`.
8. If validation loss improved, keep the commit and advance the branch.
9. If validation loss is equal or worse, mark it `discard` in `results.md` and
   reset back to the pre-experiment commit.

The idea is that you are an autonomous researcher trying things out. If they
work, keep them. If they do not, discard them. Advance the branch only when the
validation metric improves.

**Timeout**: If a run takes much longer than the normal baseline time for this
machine, kill it and treat it as a failure unless the user explicitly approved a
larger experiment.

**Crashes**: Use judgment. Fix obvious implementation mistakes. Do not spend a
long time rescuing an idea that is complicated, memory-hungry, or inconsistent
with the repo's constraints.

**NEVER STOP**: Once the experiment loop has begun, do not pause to ask whether
to continue. The human may expect the system to run unattended. If you run out
of obvious ideas, re-read the code, inspect near-misses in `results.md`, combine
promising changes, simplify existing code, or try a more substantial
architecture change.

## Ideas To Try

- learning-rate changes
- batch-size changes
- dropout changes
- model width/depth changes
- CNN, RNN, state-space, or Transformer variants
- k-mer tokenization
- sequence-aware batching so batches do not cross protein boundaries
- masking or downweighting newline tokens
- weight decay
- cosine learning-rate schedule
- warmup
- gradient clipping
- sequence length changes
- tied input/output embeddings
- optimizer parameter grouping
- evaluation sample count changes only if the metric remains comparable

## Important

The score is validation cross-entropy printed as `FINAL_BEST_VAL_LOSS`. Lower is
better. Keep the validation data fixed, record every experiment in `results.md`,
and prefer improvements that make the system easier to understand.
