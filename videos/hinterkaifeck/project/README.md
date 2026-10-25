# Rebuilding this film

Run from an existing checkout. The task is already isolated; do not create a Git worktree unless explicitly requested.

## Retained inputs

- `narrative.json` and `../script.txt`: authored English narration in twelve sections. Section names are organizational metadata; no chapter bars appear in the video.
- `assets/narration-raw.flac`: real Kokoro `am_michael` speech, speed 1.07, 24 kHz mono, before loudness normalization.
- `tokens.json`: model-provided token times, with real chunk and section offsets. `chapters.json` records actual section boundaries. `pronunciations.json` records approximate name overrides.
- `assets/grids/`: fifteen original 4×4 image sheets, 240 generated panels. `grids.json` records source files and actual dimensions. The discovery grid was revised to remove a victim look-alike.
- `curation-notes.json`: fifteen rejected panels and explicit reasons; `shot-order.json` selects 225 unique source panels. No rejected panel is used at another crop.
- `grid-crops.json`: actual crop rectangles and output sizes. Small panel sources are resized to 720p; they are not native 720p images.
- `shots.json`, `timeline.json`, `images.ffconcat`: integer-frame timing, 24 fps. Boundaries follow Kokoro word/phrase candidates, constrained to 3–6 seconds; average approximately 4.09 seconds. No pan, zoom, shake or transitions.
- `captions.json`, `subtitles.ass`, `../subtitles.srt`: complete narration coverage; model token timing, maximum two balanced lines, white text with dark outline and no opaque band.
- `normalization-settings.json`: two-pass loudness measurements/settings from this exact narration. Final AAC is independently remeasured by validation.

## Environment

Prepared with Python 3.12, FFmpeg 7.1.5, CPU PyTorch, Kokoro 0.9.4, and spaCy English model 3.8.0. Exact installed Python package versions are in `requirements.txt`. The current cloud machine has `/workspace/kokoro-env`. It is outside the checkout and is not distributed as project content.

To recreate the Python environment on a machine with Python 3.12 and `uv`:

```bash
python3 -m venv /workspace/kokoro-env
export UV_CACHE_DIR=/workspace/.cache/uv
uv pip install --python /workspace/kokoro-env/bin/python 'torch==2.14.1+cpu' --index-url https://download.pytorch.org/whl/cpu
uv pip install --python /workspace/kokoro-env/bin/python -r requirements.txt
uv pip check --python /workspace/kokoro-env/bin/python
```

Run those commands from this `project` directory. Keep inherited TLS/proxy settings. FFmpeg/ffprobe with libx264, AAC and libass must also be installed. DejaVu Sans is used for subtitles.

## Rebuild from retained assets

```bash
cd /workspace/horro-story/videos/hinterkaifeck/project
/workspace/kokoro-env/bin/python prepare.py
/workspace/kokoro-env/bin/python render.py
/workspace/kokoro-env/bin/python validate.py
```

`prepare.py` recreates cropped JPEGs, captions and the still-image timeline. `render.py` measures the retained raw narration, applies two-pass normalization with AAC headroom, expands the image timeline to 24 fps **before** burning changing captions, explicitly converts JPEG full range to limited-range BT.709/yuv420p, and renders `../video.mp4`. It uses a temporary WAV outside the checkout and preserves FFmpeg failure status. `validate.py` checks full decoding, actual final AAC loudness/peak, stream properties, frame count, caption order/coverage, a changing subtitle within an otherwise static shot, shot duration, unique source images and GitHub's per-file limit. Results are written to `../validation-summary.json` and `ffprobe-final.json`.

For this exact narration the first AAC measurement required a calibrated +0.85 dB pre-limiter trim, transient limiting, and a +0.95 dB final trim before AAC encoding. The intermediate limited AAC measured −16.94 LUFS / −3.24 dBTP, providing enough peak margin for the final trim. This mastering stage and its basis are saved in `normalization-settings.json`. `render.py --audio-only` applies the same current audio pipeline and copies the existing video stream, preserving pictures and captions. Revalidate after any narration or mastering change; these settings are not a universal preset for unrelated recordings.

To regenerate speech instead of using the saved recording:

```bash
export HF_HOME=/workspace/.cache/huggingface
export XDG_CACHE_HOME=/workspace/.cache
export HF_HUB_DISABLE_XET=1 OMP_NUM_THREADS=2
/workspace/kokoro-env/bin/python synthesize.py
```

This requires the public `hexgrad/Kokoro-82M` model and `am_michael` voice. Their downloads may redirect from `huggingface.co` to `us.aws.cdn.hf.co`. No Hugging Face token was required for this production. Optional per-section synthesis caches are ignored by Git; after editing narration, invalidate affected cached section files before synthesis. Speech regeneration can vary with model/runtime versions. The retained FLAC is the exact production input.

## Image generation and limitations

Images and thumbnail were made with the session's `image_gen` tool. Its underlying model version was not exposed. `prompt-01.txt` through `prompt-12.txt` retain base scene briefs; `narrative.json`, `shot-order.json` and curation notes record selected/replacement concepts and identity corrections. For new images, use these briefs, the retained source sheets as visual references, and the character/setting bible. Regeneration is nondeterministic and is not needed to reproduce this edit. This repository does not claim an installed image-generation server or exact image regeneration from a seed.

The setting, faces, clothing details, tool close-ups, archive interiors, and memorials are illustrative, not an exact survey or authentic evidence. No genuine victim or suspect likeness is asserted. No production images are reused from news articles. The narrator is synthetic. Research limitations and factual decisions are in `../SOURCES.md`.

All source contact sheets were visually inspected and selected rendered frames were checked. Automated audio/decoding checks do not constitute a complete human listening pass. No claim is made that the full film was manually watched or listened to from beginning to end.
