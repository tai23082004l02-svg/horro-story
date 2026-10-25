import os, json, subprocess, shutil, math
from pathlib import Path
os.environ.setdefault('HF_HOME','/workspace/.cache/huggingface')
os.environ.setdefault('OMP_NUM_THREADS','2')
import torch, numpy as np, soundfile as sf
from kokoro import KPipeline
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent.parent
A=ROOT/'project/assets'
lines=['Did you know Vietnam has a bogeyman who carries children away in sacks?', 'They call him Ong Ba Bi.', 'Parents used his name to frighten children into behaving.', 'Three sacks. Nine straps. Twelve eyes.', 'Behave, or he will take you. That was the warning.', 'Now imagine that warning becoming a nightmare.', 'He bends beneath your ceiling. His footsteps stop outside your room.', 'The sacks on his back are breathing.', "His smile splits open. He didn't come to frighten you. He's hungry.", 'You hide beneath the covers. But the ceiling is watching.', 'The walls fold inward. Wood turns into woven cloth.', "Those footsteps weren't outside. You're already inside his sack."]
(ROOT/'script.txt').write_text('\n\n'.join(lines))
pipe=KPipeline(lang_code='a',repo_id='hexgrad/Kokoro-82M',device='cpu')
samples=[]; shots=[]; captions=[]; offset=0
for i,line in enumerate(lines):
    pieces=[]; words=[]; local=0
    spoken=line.replace('Ong Ba Bi','[Ong Ba Bi](/ɔŋ bɑː biː/)')
    for r in pipe(spoken,voice='am_michael',speed=1.0):
        x=r.audio.numpy();pieces.append(x)
        for t in r.tokens or []:
            if t.start_ts is not None and t.end_ts is not None:
                words.append(dict(text=t.text,space=t.whitespace or '',start=offset+local+t.start_ts,end=offset+local+t.end_ts))
        local+=len(x)/24000
    clean=[]
    for word in words:
        if clean and not any(c.isalnum() for c in word['text']):
            clean[-1]['text']+=word['text']
            clean[-1]['space']=word['space']
            clean[-1]['end']=max(clean[-1]['end'],word['end'])
        else: clean.append(word)
    words=clean
    pause=0.65 if i!=11 else 1.1
    duration=math.ceil((local+pause)*24)/24
    samples.extend(pieces);samples.append(np.zeros(round(duration*24000)-sum(map(len,pieces)),dtype=np.float32))
    for k in range(0,len(words),6):
        group=words[k:k+6]
        captions.append(dict(text=''.join(t['text']+t['space'] for t in group).strip(),start=group[0]['start'],end=group[-1]['end']))
    shots.append(dict(id=i+1,start=offset,end=offset+duration,text=line,image=f'project/assets/scene-{i+1:02}.png'))
    offset+=duration
    print(i+1,round(duration,2),flush=True)
voice=np.concatenate(samples)
sf.write(A/'narration-raw.wav',voice,24000)
t=np.arange(len(voice))/24000
fade=np.minimum(np.minimum(t/2,(len(voice)/24000-t)/1.5),1).clip(0,1)
bed=fade*(0.006*np.sin(2*np.pi*52*t)+0.003*np.sin(2*np.pi*78.3*t))
sf.write(A/'mix-raw.wav',voice+bed,24000)
sf.write(A/'ambience-original.wav',bed,24000)
(ROOT/'project/timeline.json').write_text(json.dumps(shots,indent=2))
(ROOT/'project/captions.json').write_text(json.dumps(captions,indent=2))
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(ROOT/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(captions))+'\n')
sources=['exec-07330d24-5d92-4888-8412-c9acd3bcd066.png','exec-fc1100c7-0a46-4b1f-b798-ff2fb453b4e5.png','exec-61a5ae8d-1909-4a1a-b7a2-133023f0f832.png']
def run(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
crops=[]
for j,name in enumerate(sources):
    src=A/f'sheet-{j+1}.png'
    if not src.exists(): shutil.copy2(Path('/workspace/generated_images')/name,src)
    meta=json.loads(subprocess.check_output(['ffprobe','-v','quiet','-show_streams','-of','json',str(src)]))['streams'][0]
    w,h=meta['width'],meta['height']
    for k in range(4):
        n=j*4+k+1;x=(k%2)*(w//2)+4;y=(k//2)*(h//2)+4;cw=w//2-8;ch=h//2-8
        crops.append(dict(scene=n,source=src.name,crop=[x,y,cw,ch]))
        run(['ffmpeg','-y','-i',str(src),'-vf',f'crop={cw}:{ch}:{x}:{y}', '-frames:v','1',str(A/f'scene-{n:02}.png')])
        shot=shots[n-1];dur=shot['end']-shot['start']
        run(['ffmpeg','-y','-loop','1','-i',str(A/f'scene-{n:02}.png'),'-t',str(dur),'-vf','scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1','-r','24','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-threads','2',str(A/f'clip-{n:02}.mp4')])
(ROOT/'project/grid-crops.json').write_text(json.dumps(crops,indent=2))
(A/'concat.txt').write_text('\n'.join(f"file 'clip-{i:02}.mp4'" for i in range(1,13)))
run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(A/'concat.txt'),'-c','copy',str(A/'picture.mp4')])
measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(A/'mix-raw.wav'),'-af','loudnorm=I=-16:TP=-2:LRA=9:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
m=json.JSONDecoder().raw_decode(measure[measure.rfind('{'):])[0]
(ROOT/'project/normalization-settings.json').write_text(json.dumps(m,indent=2))
norm=f"loudnorm=I=-16:TP=-2:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
run(['ffmpeg','-y','-i',str(A/'picture.mp4'),'-i',str(A/'mix-raw.wav'),'-vf',f"subtitles={ROOT/'subtitles.srt'}:force_style='FontName=DejaVu Sans,FontSize=18,Outline=2,Shadow=0,MarginV=55,MarginL=26,MarginR=42'",'-af',norm,'-c:v','libx264','-preset','fast','-crf','20','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','160k','-movflags','+faststart',str(ROOT/'video.mp4')])
run(['ffmpeg','-y','-i',str(A/'narration-raw.wav'),'-af',norm,'-ar','48000','-c:a','pcm_s16le',str(ROOT/'narration.wav')])
run(['ffmpeg','-y','-i',str(A/'scene-02.png'),'-vf','scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280','-frames:v','1',str(ROOT/'cover.jpg')])
print('DONE',offset,flush=True)
