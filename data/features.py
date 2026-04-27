import torch
import torchaudio
import torchaudio.transforms as T

SAMPLE_RATE = 16000

_mel = T.MelSpectrogram(
    sample_rate=SAMPLE_RATE,
    n_fft=1024,
    hop_length=512,
    n_mels=128,
    f_min=20.0,
    f_max=8000.0,
    power=2.0,
)

"""[C, T] → [C, 128, T_mel]"""
def extract_mel(waveform: torch.Tensor) -> torch.Tensor:
    return _mel(waveform)

"""Load audio file, resample if needed, return mel spectrogram [C, 128, T_mel]"""
def load_and_extract(path: str) -> torch.Tensor:
    waveform, sr = torchaudio.load(path)
    if sr != SAMPLE_RATE:
        waveform = T.Resample(sr, SAMPLE_RATE)(waveform)
    return extract_mel(waveform)