# Ong Ba Bi: Vietnam's Bogeyman

American English folklore horror short in dark surrealism. Static portrait images, straight cuts, 720×1280, 24 fps, Kokoro am_michael at speed 1.0, English captions and an original synthesized low drone.

- [Watch/download MP4](video.mp4)
- [English script](script.txt)
- [English subtitles](subtitles.srt)
- [Voice-only WAV](narration.wav)
- [Cover](cover.jpg)
- [Sources and claim boundaries](SOURCES.md)
- [Validation](validation-summary.json)

## Cultural framing

Shots 1–5 introduce a Vietnamese bogeyman and the parental warning associated with him. Shot 6 explicitly introduces an invented nightmare. A breathing sack, hungry tooth-filled mouth, watchful ceiling and room becoming a sack are original fictional elaborations, not asserted traditional rules or reported events. This is horror entertainment for a general/adult audience, not children's programming.

The design is an artistic interpretation, not a canonical depiction. Anatomical eye counts and visible sack straps vary between generated shots; the verse's numbers are cultural motifs. A child appears unharmed beside a protective mother in one contextual scene; no child assault or injury is depicted.

## Images and sound

Twelve distinct compositions from three AI-generated 2×2 sheets. Individual panels are approximately 470×836 before edge trimming, enlarged for 720p export; sources are not native 720p panels. All sheets inspected visually; source continuity is approximate. Static crops remove panel dividers. The monster's scale, eyes and architecture become impossible deliberately.

Original 52 Hz and 78.3 Hz synthesized tones form a quiet ambience bed. No third-party music or sound recordings. Kokoro speaks US English; the Vietnamese name uses an approximate IPA override, not a native Vietnamese recording.

## Rebuild

Python 3.12, kokoro 0.9.4, torch, numpy, soundfile, FFmpeg with libass/libx264. Run `project/produce.py`; it reuses included `project/assets/sheet-*.png`, generates narration and true token timestamps, then renders. Run `project/validate.py` to decode and measure the final MP4. Model download access is required; no models or credentials included. Generated intermediate MP4 clips are ignored by Git.

See validation-summary.json for measured duration, audio and review scope. No complete manual playback is claimed. Upload metadata is prepared; nothing is published to YouTube.
