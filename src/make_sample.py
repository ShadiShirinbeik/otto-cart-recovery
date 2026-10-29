# Picks 1M random sessions from the full file and saves them as a flat events table.
# Run:  python src/make_sample.py   (or from a notebook:  %run ../src/make_sample.py)
# Takes a few minutes, the whole 11 GB file is read once.

import json
from pathlib import Path

import numpy as np
import pandas as pd

# paths are based on where this file is, so it works from any folder
ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "otto-recsys-train.jsonl"
OUT_FILE = ROOT / "data" / "processed" / "events_sample_raw.parquet"

N_SESSIONS = 12_899_779  # total sessions, counted in notebook 01
SAMPLE_SIZE = 1_000_000
SEED = 42  # same seed = same sample every time


def to_frame(rows):
    df = pd.DataFrame(rows, columns=["session", "aid", "ts", "type"])
    df["session"] = df["session"].astype("int32")
    df["aid"] = df["aid"].astype("int32")
    df["type"] = pd.Categorical(df["type"], categories=["clicks", "carts", "orders"])
    return df


rng = np.random.default_rng(SEED)
keep = set(rng.choice(N_SESSIONS, size=SAMPLE_SIZE, replace=False).tolist())

# session ids are the line numbers (0, 1, 2, ...), so only the kept lines need to be parsed
chunks = []
rows = []
with open(RAW_FILE, encoding="utf-8") as f:
    for line_no, line in enumerate(f):
        if line_no in keep:
            session = json.loads(line)
            if session["session"] != line_no:
                raise ValueError(f"session id doesn't match line number at line {line_no}")
            for e in session["events"]:
                rows.append((line_no, e["aid"], e["ts"], e["type"]))

        # turn rows into a dataframe from time to time, uses much less memory
        if len(rows) >= 2_000_000:
            chunks.append(to_frame(rows))
            rows = []

        if line_no > 0 and line_no % 1_000_000 == 0:
            print(f"{line_no:,} lines read")

chunks.append(to_frame(rows))
events = pd.concat(chunks, ignore_index=True)

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
events.to_parquet(OUT_FILE, index=False)

print(f"Saved {events['session'].nunique():,} sessions and {len(events):,} events to {OUT_FILE}")
