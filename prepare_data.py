from Bio import SeqIO
from pathlib import Path
import random

DATA = Path("data")
INPUT = DATA / "uniprot_sprot.fasta"
TRAIN = DATA / "train.txt"
VAL = DATA / "val.txt"

random.seed(42)

seqs = []
for record in SeqIO.parse(INPUT, "fasta"):
    seq = str(record.seq).upper()

    # Keep simple protein alphabet examples.
    # Remove sequences with uncommon/ambiguous amino acid symbols.
    if all(c in "ACDEFGHIKLMNPQRSTVWY" for c in seq):
        if 40 <= len(seq) <= 1024:
            seqs.append(seq)

random.shuffle(seqs)

n_val = max(1000, int(0.05 * len(seqs)))
val = seqs[:n_val]
train = seqs[n_val:]

TRAIN.write_text("\n".join(train) + "\n")
VAL.write_text("\n".join(val) + "\n")

print(f"train sequences: {len(train)}")
print(f"val sequences: {len(val)}")
