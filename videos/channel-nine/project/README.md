# Continuing Channel Nine

This is an audio-ready, image-blocked original fictional horror project. Do not describe it as a completed illustrated film. Use the existing isolated checkout; do not create a worktree unless requested.

## Retained actual assets

- assets/narration-raw.flac: Kokoro am_michael at1.07,24kHz mono.
- assets/sound-design-bed.flac: original procedural stereo wind/drone, knocks and phone tones.
- assets/mix-raw.flac: processed radio voice plus original bed,48kHz stereo, before mastering.
- ../audio-preview.m4a: measured/mastered AAC preview.
- narrative.json, tokens.json, chapters.json, pronunciations.json: story and actual timing.
- captions.json, subtitles.ass, ../subtitles.srt: complete English captions using token durations.
- shots.json/timeline.json:96 planned3–6second cuts; image_status explicitly missing.
- shot-prompts.json:112 full-frame candidate prompts,96 selected=true. story-bible.json records continuity and plot logic.
- normalization-settings.json and sound-cues.json: exact mastering trace, measured AAC attempts and sound cue locations.
- visual-preflight.json:96 missing image inputs; curation-notes.json has no accepted images yet.

## Tested audio commands

Use /workspace/kokoro-env Python3.12 and system FFmpeg7.1.5. requirements.txt records installed Python dependencies. Public Kokoro model/voice cache lives outside the repository under /workspace/.cache/huggingface. Keep TLS and inherited proxy verification enabled.

```bash
cd /workspace/horro-story/videos/channel-nine/project
/workspace/kokoro-env/bin/python synthesize.py
/workspace/kokoro-env/bin/python prepare.py
/workspace/kokoro-env/bin/python master_audio.py
/workspace/kokoro-env/bin/python validate_audio.py
/workspace/kokoro-env/bin/python render_video.py --check-only
```

Per-section synthesis caches are ignored by Git. Invalidate only affected cached section files after editing narration, then regenerate timing/captions/mix. No uniform word-duration approximation is used. master_audio.py first measures this mix, normalizes with its own measured values, encodes AAC, and calibrates gain/limiting against actual encoded results. It preserves subprocess failures and refuses to mark audio ready if targets fail.

The last command is an actual tested preflight with blocked_images outcome, not a successful video render. Read image-generation.md and generate sharp full-frame sources before continuing. Preserve the first reference and use it to keep Daniel, Lena, the double and the station consistent. Every source must be at least1280×720. No4×4 panel upsampling or reuse of the previous video's farm images. Save accepted source PNGs under assets/images/<id>.png and record actual acceptance in curation-notes.json.

## Unrun video steps

After all images are present and visually accepted, render_video.py can make static720p24fps video with changing captions. It creates full-frame crop metadata, expands images to24fps BEFORE ASS subtitles, converts JPEG color range explicitly, and copies the already mastered AAC stream. This path has not run for this project. Create and inspect thumbnail.jpg from thumbnail-prompt.txt, then run validate_video.py against the actual MP4. Inspect final sample frames and document real review scope. Only then replace the partial README/validation/handoff status with completed measurements, commit/push and verify downloadable files.

The current audio-only validation report must remain clearly distinct from video readiness. Image generation was blocked by a tool usage limit. No credential is missing for the already prepared Kokoro/FFmpeg workflow. Do not claim that buying a chat subscription automatically supplies an external image API or that any API is connected here.
