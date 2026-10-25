import json, subprocess, hashlib, re
from pathlib import Path
R=Path(__file__).resolve().parent.parent
v=R/'video.mp4'
subprocess.run(['ffmpeg','-v','error','-i',str(v),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-show_format','-of','json',str(v)]))
log=subprocess.run(['ffmpeg','-hide_banner','-i',str(v),'-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
m=json.JSONDecoder().raw_decode(log[log.rfind('{'):])[0]; duration=float(probe['format']['duration'])
caps=json.loads((R/'project/captions.json').read_text()); shots=json.loads((R/'project/timeline.json').read_text())
assert all(0<=c['start']<c['end']<=duration for c in caps)
assert all(a['end']<=b['start']+0.01 for a,b in zip(caps,caps[1:]))
assert re.findall(r'\w+', ' '.join(c['text'] for c in caps).lower())==re.findall(r'\w+', (R/'script.txt').read_text().lower())
video=next(s for s in probe['streams'] if s['codec_type']=='video')
assert (video['width'],video['height'],video['codec_name'],video['pix_fmt'],video['r_frame_rate'])==(720,1280,'h264','yuv420p','24/1')
assert len(shots)==16 and len({s['image'] for s in shots})==16
assert float(m['input_tp'])<=-1.5 and abs(float(m['input_i'])+16)<1
report=dict(status='complete',duration_seconds=duration,scenes=len(shots),mean_scene_seconds=duration/len(shots),caption_cues=len(caps),loudness_lufs=float(m['input_i']),true_peak_dbtp=float(m['input_tp']),decode='passed',caption_bounds='passed',sha256=hashlib.sha256(v.read_bytes()).hexdigest(),streams=[dict(codec=s['codec_name'],type=s['codec_type'],width=s.get('width'),height=s.get('height'),fps=s.get('r_frame_rate'),sample_rate=s.get('sample_rate')) for s in probe['streams']],manual_review='All four original sheets inspected visually. Exported frames sampled. No complete manual audio/video playback.',source_resolution='Four panels per 941x1672 sheet, trimmed and enlarged for 720x1280 export.')
(R/'validation-summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
