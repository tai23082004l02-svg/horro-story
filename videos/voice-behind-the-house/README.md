# The Voice Behind the House

Original fictional Vietnamese folk horror for a US audience. Vertical 720×1280, 24 fps, static images, straight cuts, English subtitles and Kokoro American English narration (am_michael, speed 1.0).

- [Video](video.mp4)
- [Script](script.txt)
- [Subtitles](subtitles.srt)
- [Narration](narration.wav)
- [Cover](cover.jpg)
- [Production script](project/produce.py)

Twelve distinct scenes cropped from three AI-generated 2×2 sheets. Source panels are approximately 470×836 before trimming, enlarged for 720p output; this is not native 720p artwork. Images were inspected as sheets. Minor prop and framing variations remain between generated scenes.

## Fiction and continuity

This story is invented, inspired by Vietnamese rural settings and the horror motif of a familiar voice outside at night. It is not a documented event or a claim about Vietnamese beliefs.

A young adult is alone in a wooden house at midnight. His real mother is in the hospital. Something outside imitates her voice. He never answers it and never opens the door. The last line reveals that it already knows where he is.

## Rebuild

Use Python 3.12, kokoro 0.9.4, torch, numpy, soundfile and FFmpeg with libass. Run `project/produce.py` with the Kokoro virtual environment. Portable original sheets are included as `project/assets/sheet-*.png` and reused automatically. No credentials or model weights are included.

Token timestamps from Kokoro determine caption timing. Scene boundaries follow each synthesized sentence and an intentional short pause, rounded to 24 fps. Two-pass loudness normalization is measured on this narration. See validation-summary.json for final-file measurements and verification limits.
