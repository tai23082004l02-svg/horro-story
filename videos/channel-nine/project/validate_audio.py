"""Validate the audio-only delivery; never establish video readiness from these checks."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from master_audio import measurement

ROOT=Path(__file__).resolve().parent

def main():
    preview=ROOT.parent/'audio-preview.m4a'
    timeline=json.loads((ROOT/'timeline.json').read_text())
    captions=json.loads((ROOT/'captions.json').read_text())
    narrative=json.loads((ROOT/'narrative.json').read_text())
    clean=lambda x:re.sub(r'\W+','',x).casefold()
    assert clean(' '.join(c['text'] for c in captions))==clean(' '.join(c['text'] for c in narrative))
    assert all(0<=c['start']<c['end']<=timeline['duration'] for c in captions)
    assert all(a['end']<=b['start'] for a,b in zip(captions,captions[1:]))
    assert all(len(c['lines'])<=2 and max(map(len,c['lines']))<=42 for c in captions)
    assert len({s['id'] for s in timeline['shots']})==len(timeline['shots'])
    assert all(72<=s['frames']<=144 for s in timeline['shots'])
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(preview)],check=True,capture_output=True,text=True)
    streams=json.loads(probe.stdout)
    assert len(streams['streams'])==1
    stream=streams['streams'][0]
    assert (stream['codec_name'],stream['sample_rate'],stream['channels'])==('aac','48000',2)
    assert abs(float(streams['format']['duration'])-timeline['duration'])<.05
    decoded=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(preview),'-f','null','-'],check=True,capture_output=True,text=True)
    assert not decoded.stderr.strip()
    actual=measurement(preview)
    assert abs(float(actual['input_i'])+16)<=.3
    assert float(actual['input_tp'])<=-1.5
    missing=[s['id'] for s in timeline['shots'] if not (ROOT/s['image']).exists()]
    report={'status':'partial_audio_ready_video_blocked','duration_seconds':timeline['duration'],'audio_decode':'passed','audio_codec':'aac','sample_rate':48000,'channels':2,'actual_final_aac':actual,'caption_cues':len(captions),'caption_text_coverage':'all narration words in order','caption_timing':'Kokoro token times','planned_shots':len(timeline['shots']),'planned_average_shot_seconds':timeline['duration']/len(timeline['shots']),'image_files_present':len(timeline['shots'])-len(missing),'image_files_missing':len(missing),'missing_image_reason':'image_gen HTTP429 usage_limit_reached','video_rendered':False,'video_checks':'not run: no new images, no video.mp4','thumbnail_generated':False,'manual_listening':'not claimed; automated loudness, timing and decode checks','sha256_audio':hashlib.sha256(preview.read_bytes()).hexdigest()}
    (ROOT.parent/'validation-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'ffprobe-audio.json').write_text(json.dumps(streams,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
