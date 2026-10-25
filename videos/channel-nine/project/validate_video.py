"""Validate the actual final delivery, retaining measured AAC loudness and decode status."""
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent
VIDEO=ROOT.parent

def execute(args):
    return subprocess.run(args,cwd=ROOT,check=True,capture_output=True,text=True)

def main():
    film=str(VIDEO/'video.mp4')
    probe=json.loads(execute(['ffprobe','-v','error','-show_streams','-show_format','-of','json',film]).stdout)
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['codec_name'],video['width'],video['height'],video['pix_fmt'],video['r_frame_rate'])==('h264',1280,720,'yuv420p','24/1')
    assert audio['codec_name']=='aac' and audio['sample_rate']=='48000' and audio['channels']==2
    timeline=json.loads((ROOT/'timeline.json').read_text())
    assert abs(float(video['duration'])-timeline['duration'])<1/24
    assert int(video['nb_frames'])==timeline['frames']
    # A still image must retain its composition while captions change inside it.
    # This catches applying subtitle rendering before still-frame duplication.
    frames=[]
    for timestamp in ['0.125','1.000']:
        r=subprocess.run(['ffmpeg','-v','error','-ss',timestamp,'-i',film,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],check=True,capture_output=True)
        frames.append(np.asarray(Image.open(io.BytesIO(r.stdout)).convert('RGB'),dtype=np.int16))
    difference=np.abs(frames[0]-frames[1])
    top_change=float(difference[:560].mean())
    bottom_changed_pixels=int((difference[580:].max(axis=2)>30).sum())
    assert top_change<2.0,('Still image unexpectedly changes',top_change)
    assert bottom_changed_pixels>300,('Subtitle did not appear inside first still shot',bottom_changed_pixels)
    # Full video+audio decode with underlying nonzero failures preserved.
    decoded=execute(['ffmpeg','-v','error','-xerror','-nostdin','-i',film,'-map','0:v:0','-map','0:a:0','-f','null','-'])
    assert not decoded.stderr.strip(),decoded.stderr
    measure=execute(['ffmpeg','-hide_banner','-nostdin','-i',film,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'])
    loudness=json.loads(re.findall(r'\{[^{}]+\}',measure.stderr)[-1])
    assert abs(float(loudness['input_i'])+16)<=0.4,loudness
    assert float(loudness['input_tp'])<=-1.5,loudness
    captions=json.loads((ROOT/'captions.json').read_text())
    assert captions and all(0<=c['start']<c['end']<=timeline['duration'] for c in captions)
    assert all(a['end']<=b['start'] for a,b in zip(captions,captions[1:]))
    assert all(len(c['lines'])<=2 and max(map(len,c['lines']))<=44 for c in captions)
    # Compare model graphemes with the actual authored narration, not merely counts.
    narrative=json.loads((ROOT/'narrative.json').read_text())
    def clean(t):return re.sub(r'\W+','',t).casefold()
    assert clean(' '.join(c['text'] for c in captions))==clean(' '.join(c['text'] for c in narrative))
    shots=timeline['shots']
    assert all(72<=s['frames']<=144 for s in shots)
    assert all(a['end_frame']==b['start_frame'] for a,b in zip(shots,shots[1:]))
    assert len({s['image'] for s in shots})==len(shots)
    digests=[hashlib.sha256((ROOT/s['image']).read_bytes()).hexdigest() for s in shots]
    assert len(set(digests))==len(digests),'Duplicate image files in timeline'
    reviews=json.loads((ROOT/'curation-notes.json').read_text())
    assert set(reviews['accepted_ids'])=={s['id'] for s in shots}
    crops=json.loads((ROOT/'image-crops.json').read_text())
    assert all(min(c['source_size'][0]/1280,c['source_size'][1]/720)>=1 for c in crops)
    assert (VIDEO/'thumbnail.jpg').exists()
    size=(VIDEO/'video.mp4').stat().st_size
    assert size<100*1024**2,'GitHub regular file limit exceeded'
    report={
        'status':'passed','duration_seconds':timeline['duration'],'frames':timeline['frames'],
        'shots':len(shots),'unique_image_files':len(digests),
        'average_shot_seconds':timeline['duration']/len(shots),
        'shortest_shot_seconds':min(s['frames']/24 for s in shots),
        'longest_shot_seconds':max(s['frames']/24 for s in shots),
        'caption_cues':len(captions),'caption_text_coverage':'all narration words in order',
        'caption_timing':'Kokoro model token durations; not uniform word allocation',
        'caption_intra_shot_change':{'status':'passed','timestamps_seconds':[0.125,1.0],'top_mean_pixel_delta':top_change,'subtitle_area_changed_pixels':bottom_changed_pixels},
        'video':{k:video[k] for k in ['codec_name','width','height','pix_fmt','r_frame_rate','nb_frames']},
        'audio':{k:audio[k] for k in ['codec_name','sample_rate','channels']},
        'actual_final_aac_input_measurement':loudness,
        'full_decode':'passed; video and audio; ffmpeg -xerror; zero diagnostics',
        'file_bytes':size,'sha256':hashlib.sha256((VIDEO/'video.mp4').read_bytes()).hexdigest(),
        'visual_review':'accepted_ids cover each full-frame image; actual review details in curation-notes.json',
        'manual_listening':'not claimed; automated checks and selected frame review only',
        'limitations':['Original fictional horror story; all characters and events invented.','Synthetic narration and original procedural sound design.','No real case or historical footage is represented.','Manual full-length listening/viewing must not be claimed unless actually performed.']
    }
    (VIDEO/'validation-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'ffprobe-final.json').write_text(json.dumps(probe,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
