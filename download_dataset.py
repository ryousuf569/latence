#!/usr/bin/env python3
"""
ML audio dataset downloader — Deezer 30-second previews + Free Music Archive via HuggingFace.

# pip install requests torchaudio datasets pandas numpy torch

No API credentials needed. Just run:
  python download_dataset.py
"""

import csv
import logging
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import miniaudio
import pandas as pd
import soundfile as sf
import requests
from datasets import Audio, load_dataset

# ── Config ────────────────────────────────────────────────────────────────────

TARGET_DEEZER  = 3_000
TARGET_FMA     = 3_000
SAMPLE_RATE    = 16_000          # 16 kHz mono int16 → ~940 KB per 30 s clip
DEEZER_SLEEP   = 1.0             # seconds between Deezer API calls
FMA_SLEEP      = 1.0             # seconds between FMA downloads
MAX_RETRIES    = 3

DATA_DIR     = Path("data")
DEEZER_DIR   = DATA_DIR / "deezer"
FMA_DIR      = DATA_DIR / "fma"
DEEZER_META  = DATA_DIR / "deezer_metadata.csv"
FMA_META     = DATA_DIR / "fma_metadata.csv"
FULL_META    = DATA_DIR / "full_metadata.csv"

DEEZER_FIELDS = ["track_id", "title", "artist", "genre", "duration_sec", "source"]
FMA_FIELDS    = ["index",    "title", "artist", "genre", "duration_sec", "source"]

# ── Logging ───────────────────────────────────────────────────────────────────

log = logging.getLogger(__name__)

def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(DATA_DIR / "download.log"),
        ],
    )
    for noisy in ("httpx", "httpcore", "datasets", "huggingface_hub",
                  "urllib3", "filelock", "fsspec", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

# ── Shared utilities ──────────────────────────────────────────────────────────

def _setup_dirs():
    DEEZER_DIR.mkdir(parents=True, exist_ok=True)
    FMA_DIR.mkdir(parents=True, exist_ok=True)


def retry_call(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """Call func(*args, **kwargs) with exponential backoff on any error."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt + random.uniform(0.5, 1.5)
            log.warning("Attempt %d/%d failed (%s: %s). Retrying in %.1f s.",
                        attempt + 1, max_retries, type(exc).__name__, exc, wait)
            time.sleep(wait)


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def audio_bytes_to_wav(audio_bytes: bytes, out: Path) -> float:
    """Decode raw audio bytes → 16 kHz mono int16 WAV. Returns duration (s)."""
    decoded = miniaudio.decode(
        audio_bytes,
        output_format=miniaudio.SampleFormat.SIGNED16,
        nchannels=1,
        sample_rate=SAMPLE_RATE,
    )
    samples = np.frombuffer(decoded.samples, dtype=np.int16)
    sf.write(str(out), samples, SAMPLE_RATE, subtype="PCM_16")
    return decoded.num_frames / SAMPLE_RATE


def existing_ids(directory: Path, prefix: str) -> set[str]:
    """IDs already on disk, parsed from filenames like {prefix}_{id}.wav."""
    return {f.stem[len(prefix) + 1:] for f in directory.glob(f"{prefix}_*.wav")}


def open_csv(path: Path, fields: list) -> tuple:
    """Open a CSV for append; write header only if the file is new."""
    is_new = not path.exists()
    fh = open(path, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=fields)
    if is_new:
        writer.writeheader()
    return fh, writer


def dir_size_mb(d: Path) -> float:
    return sum(f.stat().st_size for f in d.rglob("*.wav") if f.is_file()) / 1_048_576


# ── Deezer ────────────────────────────────────────────────────────────────────
# Deezer public API — no auth required, 30-second MP3 previews still work.
# Search: GET https://api.deezer.com/search?q={q}&limit=25&index={offset}
# Each track has a `preview` field with a direct MP3 URL.

# Deezer chart endpoints — returns Deezer's actual trending tracks by genre.
# genre_id 0=global, 116=hip-hop, 132=rap, 165=r&b/soul, 122=pop
DEEZER_CHARTS: list[tuple[str, str]] = [
    ("https://api.deezer.com/chart/0/tracks",   "pop"),      # global top — mostly pop/mainstream
    ("https://api.deezer.com/chart/116/tracks",  "hip-hop"),
    ("https://api.deezer.com/chart/132/tracks",  "rap"),
    ("https://api.deezer.com/chart/165/tracks",  "r&b"),
    ("https://api.deezer.com/chart/122/tracks",  "pop"),
]

# Artist searches — sorted by RANKING so we get their biggest hits first.
# Plain-text genre queries removed: they return obscure/random tracks.
DEEZER_ARTIST_QUERIES: list[tuple[str, str]] = [
    ("Drake",               "hip-hop"),
    ("Kendrick Lamar",      "rap"),
    ("Travis Scott",        "hip-hop"),
    ("Future",              "hip-hop"),
    ("Metro Boomin",        "hip-hop"),
    ("21 Savage",           "rap"),
    ("SZA",                 "r&b"),
    ("Post Malone",         "hip-hop"),
    ("J. Cole",             "rap"),
    ("Lil Baby",            "hip-hop"),
    ("Nicki Minaj",         "rap"),
    ("Cardi B",             "rap"),
    ("Young Thug",          "hip-hop"),
    ("Gunna",               "hip-hop"),
    ("Roddy Ricch",         "hip-hop"),
    ("NBA YoungBoy",        "hip-hop"),
    ("Juice WRLD",          "hip-hop"),
    ("Lil Durk",            "hip-hop"),
    ("Polo G",              "rap"),
    ("Don Toliver",         "hip-hop"),
    ("Baby Keem",           "rap"),
    ("Latto",               "rap"),
    ("GloRilla",            "hip-hop"),
    ("Sexyy Red",           "hip-hop"),
    ("Ice Spice",           "hip-hop"),
    ("Moneybagg Yo",        "hip-hop"),
    ("Key Glock",           "hip-hop"),
    ("The Weeknd",          "r&b"),
    ("Frank Ocean",         "r&b"),
    ("SZA",                 "r&b"),
    ("Bryson Tiller",       "r&b"),
    ("H.E.R.",              "r&b"),
    ("Giveon",              "r&b"),
    ("Summer Walker",       "r&b"),
    ("Brent Faiyaz",        "r&b"),
    ("Chris Brown",         "r&b"),
    ("Usher",               "r&b"),
    ("Daniel Caesar",       "r&b"),
    ("Steve Lacy",          "r&b"),
    ("Kehlani",             "r&b"),
    ("Jhene Aiko",          "r&b"),
    ("Blxst",               "r&b"),
    ("Lucky Daye",          "r&b"),
    ("Ari Lennox",          "r&b"),
    ("Tyler the Creator",   "hip-hop"),
    ("Childish Gambino",    "hip-hop"),
    ("ASAP Rocky",          "hip-hop"),
    ("Kanye West",          "hip-hop"),
    ("Jay-Z",               "rap"),
    ("Eminem",              "rap"),
    ("Lil Wayne",           "rap"),
    ("Pusha T",             "rap"),
    ("Meek Mill",           "rap"),
    ("Rick Ross",           "rap"),
    ("2 Chainz",            "rap"),
    ("Wiz Khalifa",         "hip-hop"),
    ("Doja Cat",            "pop"),
    ("Ariana Grande",       "pop"),
    ("Billie Eilish",       "pop"),
    ("Olivia Rodrigo",      "pop"),
    ("Harry Styles",        "pop"),
    ("Dua Lipa",            "pop"),
    ("Taylor Swift",        "pop"),
    ("The Kid LAROI",       "pop"),
    ("Bad Bunny",           "pop"),
    ("Peso Pluma",          "pop"),
]


def download_deezer(target: int = TARGET_DEEZER) -> tuple[int, int]:
    done_ids   = existing_ids(DEEZER_DIR, "deezer")
    downloaded = len(done_ids)
    failed     = 0

    if downloaded >= target:
        print(f"[Deezer] {downloaded}/{target} already downloaded. Skipping.")
        return downloaded, failed

    print(f"[Deezer] Resuming at {downloaded}/{target}.")

    seen: set[str] = set(done_ids)
    if DEEZER_META.exists():
        try:
            seen.update(pd.read_csv(DEEZER_META)["track_id"].astype(str))
        except Exception:
            pass

    fh, writer = open_csv(DEEZER_META, DEEZER_FIELDS)

    def handle(track: dict, genre: str):
        nonlocal downloaded, failed
        if downloaded >= target or not track:
            return
        tid = str(track.get("id", ""))
        if not tid or tid in seen:
            return
        seen.add(tid)

        preview = track.get("preview")
        if not preview:
            return

        out = DEEZER_DIR / f"deezer_{tid}.wav"
        try:
            raw = retry_call(fetch_bytes, preview)
            dur = audio_bytes_to_wav(raw, out)
            writer.writerow({
                "track_id":     tid,
                "title":        track.get("title", ""),
                "artist":       (track.get("artist") or {}).get("name", ""),
                "genre":        genre,
                "duration_sec": round(dur, 2),
                "source":       "deezer",
            })
            fh.flush()
            downloaded += 1
            print(f"\r[Deezer] {downloaded}/{target} downloaded", end="", flush=True)
        except Exception as exc:
            log.error("[Deezer] Failed %s: %s", tid, exc)
            out.unlink(missing_ok=True)
            failed += 1

    def _get(url: str, params: dict) -> dict:
        resp = requests.get(url, params=params, timeout=15)
        if not resp.ok:
            log.error("[Deezer] HTTP %d %s — %s", resp.status_code, url, resp.text[:300])
        resp.raise_for_status()
        return resp.json()

    try:
        # ── Phase 1: Deezer charts (actual trending tracks) ──────────────────
        for chart_url, genre in DEEZER_CHARTS:
            if downloaded >= target:
                break
            for index in range(0, 500, 100):
                if downloaded >= target:
                    break
                try:
                    data = retry_call(_get, chart_url, {"limit": 100, "index": index})
                    time.sleep(DEEZER_SLEEP)
                except Exception as exc:
                    log.error("[Deezer] chart '%s' @%d: %s", chart_url, index, exc)
                    break
                tracks = data.get("data") or []
                if not tracks:
                    break
                for track in tracks:
                    if downloaded >= target:
                        break
                    handle(track, genre)

        # ── Phase 2: artist searches sorted by popularity ────────────────────
        for query, genre in DEEZER_ARTIST_QUERIES:
            if downloaded >= target:
                break
            for index in range(0, 500, 25):
                if downloaded >= target:
                    break
                try:
                    data = retry_call(_get, "https://api.deezer.com/search",
                                      {"q": query, "order": "RANKING", "limit": 25, "index": index})
                    time.sleep(DEEZER_SLEEP)
                except Exception as exc:
                    log.error("[Deezer] search '%s' @%d: %s", query, index, exc)
                    break
                tracks = data.get("data") or []
                if not tracks:
                    break
                for track in tracks:
                    if downloaded >= target:
                        break
                    handle(track, genre)

    finally:
        fh.close()

    print(f"\n[Deezer] {downloaded}/{target} downloaded, {failed} failed.")
    return downloaded, failed


# ── FMA ───────────────────────────────────────────────────────────────────────

# Soft per-genre caps — sum intentionally exceeds TARGET_FMA so all genres have
# room; the cap relaxes automatically in the final 300-track stretch.
GENRE_CAPS: dict[str, int] = {
    "Hip-Hop":       450,
    "Pop":           400,
    "Rock":          400,
    "Electronic":    350,
    "Experimental":  250,
    "Folk":          250,
    "Instrumental":  250,
    "International": 250,
    "Jazz":          200,
    "Classical":     200,
    "Country":       150,
    "Soul-RnB":      150,
    "Spoken":        100,
}
DEFAULT_GENRE_CAP = 150


def _fma_genre(sample: dict) -> str:
    for key in ("genre", "genres", "track_genre", "top_genre"):
        val = sample.get(key)
        if val:
            if isinstance(val, list):
                val = val[0]
            g = str(val).strip()
            if g:
                return g
    return "Unknown"


def download_fma(target: int = TARGET_FMA) -> tuple[int, int]:
    done_ids   = existing_ids(FMA_DIR, "fma")
    done_ints  = {int(x) for x in done_ids if x.isdigit()}
    downloaded = len(done_ints)
    failed     = 0

    if downloaded >= target:
        print(f"[FMA] {downloaded}/{target} already downloaded. Skipping.")
        return downloaded, failed

    print(f"[FMA] Resuming at {downloaded}/{target}.")

    # Positions in the shuffled stream we've already decided about
    seen: set[int] = set(done_ints)
    if FMA_META.exists():
        try:
            seen.update(pd.read_csv(FMA_META)["index"].astype(int))
        except Exception:
            pass

    # Pre-fill genre counts from existing metadata
    genre_counts: dict[str, int] = defaultdict(int)
    if FMA_META.exists():
        try:
            for g, cnt in pd.read_csv(FMA_META)["genre"].value_counts().items():
                genre_counts[str(g)] = int(cnt)
        except Exception:
            pass

    fh, writer = open_csv(FMA_META, FMA_FIELDS)

    try:
        ds = load_dataset(
            "benjamin-paine/free-music-archive-large",
            split="train",
            streaming=True,
        )
        # decode=False → datasets returns raw bytes instead of calling torchcodec
        # (torchcodec requires FFmpeg DLLs; miniaudio decodes the bytes instead)
        ds = ds.cast_column("audio", Audio(decode=False))
        ds = ds.shuffle(seed=42, buffer_size=500)

        _logged_keys = False
        log.info("[FMA] Starting stream — first sample may take 30–60 s to arrive.")

        pos = 0
        for sample in ds:
            if downloaded >= target:
                break

            if not _logged_keys:
                log.info("[FMA] Dataset fields: %s", list(sample.keys()))
                _logged_keys = True

            if pos in seen:
                pos += 1
                continue

            genre     = _fma_genre(sample)
            cap       = GENRE_CAPS.get(genre, DEFAULT_GENRE_CAP)
            remaining = target - downloaded

            # Relax per-genre cap in the home stretch so we finish the quota
            if genre_counts[genre] >= cap and remaining > 300:
                pos += 1
                continue

            audio = sample.get("audio")
            if audio is None:
                pos += 1
                continue

            out = FMA_DIR / f"fma_{pos}.wav"
            try:
                if isinstance(audio, dict):
                    raw = audio.get("bytes")
                    if not raw:
                        raise ValueError("audio dict has no bytes")
                    dur = audio_bytes_to_wav(bytes(raw), out)
                elif isinstance(audio, (bytes, bytearray)):
                    dur = audio_bytes_to_wav(bytes(audio), out)
                else:
                    raise ValueError(f"unexpected audio type: {type(audio).__name__}")

                writer.writerow({
                    "index":       pos,
                    "title":       str(sample.get("title")       or ""),
                    "artist":      str(sample.get("artist")      or
                                       sample.get("artist_name") or ""),
                    "genre":       genre,
                    "duration_sec": round(dur, 2),
                    "source":      "fma",
                })
                fh.flush()
                genre_counts[genre] += 1
                seen.add(pos)
                downloaded += 1
                print(f"\r[FMA] {downloaded}/{target} downloaded", end="", flush=True)
                time.sleep(FMA_SLEEP)

            except Exception as exc:
                log.error("[FMA] pos=%d: %s", pos, exc)
                out.unlink(missing_ok=True)
                failed += 1

            pos += 1

    finally:
        fh.close()

    print(f"\n[FMA] {downloaded}/{target} downloaded, {failed} failed.")
    return downloaded, failed


# ── Summary & merge ───────────────────────────────────────────────────────────

def summarize(dz_dl: int, dz_fail: int, fma_dl: int, fma_fail: int):
    dz_mb  = dir_size_mb(DEEZER_DIR)
    fma_mb = dir_size_mb(FMA_DIR)
    total  = dz_dl + fma_dl

    print()
    print("=" * 58)
    print("  DOWNLOAD SUMMARY")
    print("=" * 58)
    print(f"  Deezer  : {dz_dl:>5,} downloaded  {dz_fail:>4,} failed  {dz_mb:>7.1f} MB")
    print(f"  FMA     : {fma_dl:>5,} downloaded  {fma_fail:>4,} failed  {fma_mb:>7.1f} MB")
    print(f"  ─────────────────────────────────────────────────────")
    print(f"  Total   : {total:>5,} tracks                {dz_mb + fma_mb:>7.1f} MB")
    print("=" * 58)


def merge_metadata():
    parts = []
    for path, id_col in [(DEEZER_META, "track_id"), (FMA_META, "index")]:
        if path.exists():
            df = pd.read_csv(path)
            df = df.rename(columns={id_col: "id"})
            parts.append(df)
    if not parts:
        log.warning("No metadata files found to merge.")
        return
    combined = pd.concat(parts, ignore_index=True)
    combined.to_csv(FULL_META, index=False)
    print(f"\nFull metadata → {FULL_META}  ({len(combined):,} rows)")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    _setup_dirs()
    _setup_logging()

    dz_dl,  dz_fail  = download_deezer()
    fma_dl, fma_fail = download_fma()

    summarize(dz_dl, dz_fail, fma_dl, fma_fail)
    merge_metadata()


if __name__ == "__main__":
    main()
