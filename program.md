# Protein Autoresearch Program

You are improving a small protein language model.

Goal:
Minimize `FINAL_BEST_VAL_LOSS` from `uv run python train.py`.

Rules:
- You may edit `train.py`.
- Do not edit the validation data.
- Do not change the train/val split.
- Keep each experiment reasonably small.
- Prefer changes that are simple and explainable.
- After every experiment, record what changed and the result in `results.md`.
- If validation loss improves, keep the change.
- If validation loss gets worse, revert it.
- Optimize for real validation loss, not training loss.

Ideas to try:
- learning rate changes
- batch size changes
- dropout changes
- model width/depth changes
- CNN vs Transformer
- k-mer tokenization
- better sampling so batches do not cross sequence boundaries
- masking newline tokens differently
- weight decay
- cosine learning-rate schedule
- gradient clipping
- sequence length changes

Important:
The score is validation cross-entropy. Lower is better.
