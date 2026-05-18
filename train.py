import math
import random
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm

DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

DATA = Path("data")
TRAIN = DATA / "train.txt"
VAL = DATA / "val.txt"

AMINO = "ACDEFGHIKLMNPQRSTVWY"
SPECIAL = "\n"
VOCAB = SPECIAL + AMINO
stoi = {ch: i for i, ch in enumerate(VOCAB)}
itos = {i: ch for ch, i in stoi.items()}

vocab_size = len(VOCAB)
block_size = 256
batch_size = 64
max_steps = 2000
eval_interval = 200
learning_rate = 3e-4


def load_text(path):
    seqs = path.read_text().splitlines()
    text = "\n".join(seqs) + "\n"
    return torch.tensor([stoi[c] for c in text if c in stoi], dtype=torch.long)


train_data = load_text(TRAIN)
val_data = load_text(VAL)


def get_batch(split):
    data = train_data if split == "train" else val_data
    ix = torch.randint(len(data) - block_size - 1, (batch_size,))
    x = torch.stack([data[i : i + block_size] for i in ix])
    y = torch.stack([data[i + 1 : i + block_size + 1] for i in ix])
    return x.to(DEVICE), y.to(DEVICE)


class TinyProteinTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        n_embd = 128
        n_head = 4
        n_layer = 4

        self.token_emb = nn.Embedding(vocab_size, n_embd)
        self.pos_emb = nn.Embedding(block_size, n_embd)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=n_embd,
            nhead=n_head,
            dim_feedforward=4 * n_embd,
            dropout=0.1,
            batch_first=True,
            activation="gelu",
        )
        self.blocks = nn.TransformerEncoder(encoder_layer, num_layers=n_layer)
        self.ln = nn.LayerNorm(n_embd)
        self.head = nn.Linear(n_embd, vocab_size)

    def forward(self, idx, targets=None):
        b, t = idx.shape
        tok = self.token_emb(idx)
        pos = self.pos_emb(torch.arange(t, device=idx.device))
        x = tok + pos

        mask = torch.triu(torch.ones(t, t, device=idx.device), diagonal=1).bool()
        x = self.blocks(x, mask=mask)
        x = self.ln(x)
        logits = self.head(x)

        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, vocab_size), targets.view(-1))

        return logits, loss


@torch.no_grad()
def estimate_loss(model):
    model.eval()
    out = {}
    for split in ["train", "val"]:
        losses = []
        for _ in range(20):
            xb, yb = get_batch(split)
            _, loss = model(xb, yb)
            losses.append(loss.item())
        out[split] = sum(losses) / len(losses)
    model.train()
    return out


def main():
    torch.manual_seed(42)
    random.seed(42)

    model = TinyProteinTransformer().to(DEVICE)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    best_val = float("inf")

    for step in tqdm(range(max_steps)):
        xb, yb = get_batch("train")
        _, loss = model(xb, yb)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        if step % eval_interval == 0 or step == max_steps - 1:
            losses = estimate_loss(model)
            val_loss = losses["val"]
            best_val = min(best_val, val_loss)
            print(
                f"step {step}: train {losses['train']:.4f}, "
                f"val {val_loss:.4f}, best_val {best_val:.4f}"
            )

    print(f"FINAL_BEST_VAL_LOSS={best_val:.4f}")


if __name__ == "__main__":
    main()
