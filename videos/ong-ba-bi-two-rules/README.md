# Two Rules Won't Save You — Ong Ba Bi

Pilot for **Vietnam's Forbidden Folklore**. Original fictional story inspired by Vietnamese folklore, for a US horror audience.

- [Video MP4](video.mp4)
- [English script](script.txt)
- [English subtitles](subtitles.srt)
- [US English narration](narration.wav)
- [Cover](cover.jpg)
- [Sources / fiction boundaries](SOURCES.md)
- [Measured validation](validation-summary.json)

## Story

A sack appears outside a bedroom although the gate is locked. A remembered warning gives two prohibitions. The protagonist follows both, but the breathing moves beneath his bed. The sack outside was a decoy; an old arm is pulling another sack around the mattress.

The hook opens before the folklore introduction. The middle supplies instructions and a false moment of relief. The last four shots explain the distraction and reveal the entity. This structure is a retention experiment, not evidence that audience retention has improved. Compare the opening drop, midpoint drop and completion rate with the previous episode after publication.

## Cultural boundaries

The folk figure, parental warning function and numerical rhyme are sourced. The cold open and the two rules are invented. Shot 5 explicitly says this is a fictional version. The images imitate inexpensive flash photographs; they are generated illustrations, not genuine footage. No historical person is identified as a demon and no actual incident is claimed.

## Production

Sixteen distinct static compositions from four 2×2 sheets; straight cuts, no pan/zoom/shake. Portrait 720×1280, H.264/yuv420p, 24 fps, AAC 48 kHz. Kokoro am_michael US English, speed 1.0, token-based English captions. Vietnamese name uses approximate IPA. Captions move above the subject for the final two shots so the face under the bed stays visible. Original synthesized low drone, no external music/SFX recordings.

Source sheets are 941×1672; individual panels are about 470×836 before trimming, enlarged to 720p. Minor generated differences in face, door angle and prop placement remain. All four sheets inspected visually, with final frames sampled; no complete manual playback claimed.

## Rebuild

Python 3.12, kokoro 0.9.4, torch, numpy, soundfile, FFmpeg with libass/libx264. Run `project/produce.py` using the Kokoro environment; included original sheets are reused. Internet access for model files may be needed. Run `project/validate.py` afterward. No model weights or credentials included; intermediate clips are ignored by Git.

Upload metadata is supplied. No upload or scheduling to YouTube was performed.
