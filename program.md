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
   entry, add one before the first run. The baseline will be recorded after the
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
- Modify `train.py`. Everything in that file is fair game, including model
  architecture, optimizer, hyperparameters, training loop, batching, masking,
  evaluation cadence, sampling strategy, and tokenization. Additional ideas include:
  - optimization changes: learning rate, cosine schedule, warmup, weight decay,
    gradient clipping, optimizer parameter grouping
  - capacity changes: batch size, block size/context length, dropout, model
    width/depth
  - architecture changes: CNN baselines, RNN/state-space/Transformer variants,
    tied input/output embeddings
  - data and tokenization changes: better sequence-aware batching, k-mer
    tokenization, newline-token masking or downweighting
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

Use the existing section-and-bullets format:

```md
Experiment Name:
- Commit: <short git hash or Baseline>
- Val loss: <FINAL_BEST_VAL_LOSS, crash, or timeout>
- Status: <keep, discard, crash, or timeout>
- Description: <short description of what changed>
```

Field meanings:

1. `Commit`: short git commit hash, usually 7 characters. Use `Baseline` for
   the initial baseline entry if no experiment commit exists yet.
2. `Val loss`: `FINAL_BEST_VAL_LOSS`, such as `1.2345`. Use `crash` if the run
   failed before producing the metric, and `timeout` if it exceeded 30 minutes.
3. `Status`: `keep`, `discard`, `crash`, or `timeout`.
4. `Description`: short text describing the change.

Example:

```md
Baseline:
- Commit: Baseline
- Val loss: 1.2345
- Status: keep
- Description: initial work

Experiment 1:
- Commit: b2c3d4e
- Val loss: 1.2101
- Status: keep
- Description: increase embedding size to 192

Experiment 2:
- Commit: c3d4e5f
- Val loss: 1.2600
- Status: discard
- Description: reduce dropout to zero

Experiment 3:
- Commit: d4e5f6a
- Val loss: crash
- Status: crash
- Description: double context length caused OOM

Experiment 4:
- Commit: e5f6a7b
- Val loss: timeout
- Status: timeout
- Description: wider model exceeded 30-minute limit
```

Commit code changes.

## The Experiment Loop

The experiment runs on a dedicated branch, for example `autoresearch/2026-05-17`.

LOOP FOREVER:

1. Look at the git state: current branch, current commit, and dirty files.
2. Pick one experimental idea and edit `train.py` directly.
3. Commit the code change.
4. Run the experiment with redirected output and enforce a 30-minute maximum
   timeout using the available tool or shell timeout mechanism:

   ```sh
   uv run python train.py > run.log 2>&1
   ```

5. Read the result:

   ```sh
   grep "^FINAL_BEST_VAL_LOSS=" run.log
   ```

6. If the run exceeded 30 minutes, kill it, record it in `results.md` with
   `Val loss: timeout` and `Status: timeout`, reset back to the pre-experiment
   commit, and move on unless the user explicitly approved a larger experiment.
7. If the grep output is empty, the run crashed. Read the stack trace:

   ```sh
   tail -n 80 run.log
   ```

   If the crash is a simple typo or shape bug, fix it and rerun. If the idea is
   fundamentally broken or too expensive, log `crash` in `results.md`, reset the
   branch back to the pre-experiment commit, and move on.
8. Record the result in `results.md`.
9. If validation loss improved, keep the commit and advance the branch.
10. If validation loss is equal or worse, mark it `discard` in `results.md` and
   reset back to the pre-experiment commit.

The idea is that you are an autonomous researcher trying things out. If they
work, keep them. If they do not, discard them. Advance the branch only when the
validation metric improves.

**Timeout**: The maximum timeout is 30 minutes per experiment.

**Crashes**: Use judgment. Fix obvious implementation mistakes. Do not spend a
long time rescuing an idea that is complicated, memory-hungry, or inconsistent
with the repo's constraints.

**NEVER STOP**: Once the experiment loop has begun, do not pause to ask whether
to continue. The human may expect the system to run unattended. If you run out
of obvious ideas, re-read the code, inspect near-misses in `results.md`, combine
promising changes, simplify existing code, or try a more substantial
architecture change.
