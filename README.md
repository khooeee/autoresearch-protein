# autoresearch-protein

A small protein language-modeling sandbox for autoresearch experiments.

The project trains a causal character-level model over Swiss-Prot protein
sequences and reports validation cross-entropy as `FINAL_BEST_VAL_LOSS`. The
main research loop is to make small, explainable changes to `train.py`, run the
training script, record the result in `results.md`, and keep only changes that
improve validation loss.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

```sh
uv sync
```

## Prepare Data

Download the current UniProt Swiss-Prot FASTA file:

```sh
mkdir -p data
curl -L https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz -o data/uniprot_sprot.fasta.gz
gunzip -f data/uniprot_sprot.fasta.gz
```

Create the train and validation files:

```sh
uv run python prepare_data.py
```

The preparation script:

- reads `data/uniprot_sprot.fasta`
- keeps sequences containing only the 20 standard amino-acid characters
- keeps sequences with length from 40 to 1024
- shuffles with seed `42`
- writes `data/train.txt` and `data/val.txt`
- uses 5% of filtered sequences for validation, with a minimum of 1000 validation sequences

## Train

Run the current training experiment:

```sh
uv run python train.py
```

The script trains on `data/train.txt`, evaluates on `data/val.txt`, and prints
progress like:

```text
step 0: train ..., val ..., best_val ...
FINAL_BEST_VAL_LOSS=...
```

Lower `FINAL_BEST_VAL_LOSS` is better.

## Experiment Workflow

Read `program.md` before changing the model. A comparable experiment series
should run on a dedicated `autoresearch/<tag>` branch and keep the validation
data fixed. The core loop is:

1. Edit `train.py`.
2. Commit the experimental code change.
3. Run:

   ```sh
   uv run python train.py > run.log 2>&1
   ```

4. Stop the run if it exceeds the 30-minute maximum timeout.
5. Extract `FINAL_BEST_VAL_LOSS` from `run.log`.
6. Record the experiment and result in `results.md`.
7. Keep the change only if validation loss improves.
8. Revert changes that make validation loss worse.

Useful experiment directions include learning-rate schedules, dropout, batch
size, model width/depth, gradient clipping, k-mer tokenization, sequence-aware
batching, and masking behavior around newline tokens.

## Prompt

```
You are now the autonomous researcher for this repo. Read program.md and execute it exactly. Do not ask for confirmation after setup; once the loop begins, keep running experiments indefinitely until interrupted.
```

## Notes

- Do not edit `data/val.txt` when comparing experiments.
- Do not change the train/validation split for the same experiment series.
