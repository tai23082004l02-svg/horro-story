"""Create original quiet horror sound design and calibrate the actual AAC preview."""
import json
import re
import subprocess
import tempfile
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT=Path(__file__).resolve().parent
SR=48000

def call(args):
    return subprocess.run(args,check=True,capture_output=True,text=True)

def measurement(path):
    r=call(['ffmpeg','-hide_banner','-nostdin','-i',str(path),'-af','loudnorm=I=-16:TP=-4:LRA=9:print_format=json','-f','null','-'])
    return json.loads(re.findall(r'\{[^{}]+\}',r.stderr)[-1])

def locate(tokens,phrase,chapter=None):
    timed=[t for t in tokens if 'start' in t and (chapter is None or t['chapter']==chapter)]
    clean=lambda x:re.sub(r'[^a-z0-9]','',x.lower())
    target=clean(phrase)
    for i in range(len(timed)):
        text=''
        for j in range(i,min(len(timed),i+60)):
            text+=clean(timed[j]['text'])
            if text==target:return timed[i]['start'],timed[j]['end']
            if len(text)>len(target):break
    raise RuntimeError('Missing sound cue: '+phrase)

def colored_noise(rng,n,low,high):
    x=rng.standard_normal(n).astype(np.float32)
    spectrum=np.fft.rfft(x)
    freq=np.fft.rfftfreq(n,1/SR)
    mask=np.minimum(1,np.maximum(0,(freq-low)/max(20,low*.2)))
    mask*=np.minimum(1,np.maximum(0,(high-freq)/max(40,high*.15)))
    y=np.fft.irfft(spectrum*mask,n)
    return y/(np.std(y)+1e-12)

def build_mix():
    timeline=json.loads((ROOT/'timeline.json').read_text())
    tokens=json.loads((ROOT/'tokens.json').read_text())
    raw,rate=sf.read(ROOT/'assets/narration-raw.flac',dtype='float32')
    length=round(timeline['duration']*SR)
    voice=np.interp(np.arange(length)/SR,np.arange(len(raw))/rate,raw,left=0,right=0)
    # The narrator and radio double share the same synthetic voice, as the story requires.
    radio_phrases=[('01',"Whatever happens don't let her answer"),('02','You just made it easier'),('03','You should have picked up'),('05',"Don't touch the antenna"),('05',"I'm trying to help you"),('05','Look at me'),('06','Cut the power'),('06','Please Daniel Pick up'),('08','Lena Who are you talking to')]
    cues=[]
    for chapter,phrase in radio_phrases:
        start,end=locate(tokens,phrase,chapter)
        a,b=round(start*SR),round(end*SR)
        segment=voice[a:b].copy()
        freq=np.fft.rfftfreq(len(segment),1/SR)
        spectrum=np.fft.rfft(segment)
        filtered=np.fft.irfft(spectrum*((freq>380)&(freq<3100)),len(segment))
        old_rms=np.sqrt(np.mean(segment**2)+1e-12)
        filtered*=old_rms/(np.sqrt(np.mean(filtered**2)+1e-12))
        filtered=np.tanh(filtered*2)/2
        fade=np.minimum(1,np.minimum(np.arange(len(segment)),np.arange(len(segment))[::-1])/(.025*SR))
        voice[a:b]=segment*(1-.65*fade)+filtered*.65*fade
        cues.append({'kind':'radio_voice_bandpass','phrase':phrase,'chapter':chapter,'start':start,'end':end})
    rng=np.random.default_rng(197309)
    seconds=np.arange(length)/SR
    voice_rms=np.sqrt(np.mean(voice**2)+1e-12)
    # Original low bed: no downloaded music, harsh jump stings, or concealed speech.
    fade=np.minimum(1,seconds/2)*np.minimum(1,(timeline['duration']-seconds)/1.0)
    swell=.65+.20*np.sin(2*np.pi*.027*seconds)+.15*np.sin(2*np.pi*.071*seconds)
    left=colored_noise(rng,length,80,1100)*voice_rms*.045*swell
    right=colored_noise(rng,length,90,1000)*voice_rms*.045*swell
    drone=(np.sin(2*np.pi*43*seconds)+.35*np.sin(2*np.pi*64.7*seconds))*voice_rms*.025
    bed=np.column_stack((left+drone,right+drone))*fade[:,None]
    def knock(at,weight=.8,pan=0):
        duration=.24;n=round(duration*SR);t=np.arange(n)/SR
        sound=(rng.standard_normal(n)*np.exp(-t*55)*.20+np.sin(2*np.pi*105*t)*np.exp(-t*24))
        sound*=voice_rms*weight
        start=round(at*SR);stop=min(length,start+n);sound=sound[:stop-start]
        if start>=0 and stop>start:
            bed[start:stop,0]+=sound*(1-pan*.3);bed[start:stop,1]+=sound*(1+pan*.3)
    first,_=locate(tokens,'Three slow knocks','01')
    for delta in [0,.43,.86]:knock(first+delta,.75,-.5)
    window,_=locate(tokens,'another knock','03');knock(window+.1,.58,.7)
    ending=timeline['duration']-1.08
    for delta in [0,.31,.62]:knock(ending+delta,.82,.1)
    cues.extend([{'kind':'three_soft_knocks','start':first,'spacing_seconds':.43},{'kind':'window_tap','start':window+.1},{'kind':'ending_three_knocks','start':ending,'spacing_seconds':.31}])
    ring,_=locate(tokens,'telephone started ringing','08')
    for offset in [0,.55]:
        a=round((ring+offset)*SR);n=min(round(.30*SR),length-a);t=np.arange(n)/SR
        tone=(np.sin(2*np.pi*620*t)+.7*np.sin(2*np.pi*840*t))*voice_rms*.11*np.sin(np.pi*np.minimum(1,t/.30))**2
        bed[a:a+n,:]+=tone[:,None]
    cues.append({'kind':'original_synth_phone_ring','start':ring})
    mix=voice[:,None]+bed
    assets=ROOT/'assets';assets.mkdir(exist_ok=True)
    sf.write(assets/'sound-design-bed.flac',bed,SR,subtype='PCM_16')
    sf.write(assets/'mix-raw.flac',mix,SR,subtype='PCM_24')
    (ROOT/'sound-cues.json').write_text(json.dumps({'seed':197309,'provenance':'original procedural noise, oscillators, and synthetic-voice processing','cues':cues,'duration':timeline['duration']},indent=2)+'\n')
    return assets/'mix-raw.flac'

def main():
    raw=build_mix()
    first=measurement(raw)
    normalizer='loudnorm=I=-16:TP=-4:LRA=9:'+':'.join(['measured_I='+first['input_i'],'measured_TP='+first['input_tp'],'measured_LRA='+first['input_lra'],'measured_thresh='+first['input_thresh'],'offset='+first['target_offset'],'linear=true'])
    attempts=[]
    with tempfile.TemporaryDirectory(prefix='channel-nine-master-') as tmp:
        base=Path(tmp)/'normalized.wav'
        call(['ffmpeg','-v','error','-nostdin','-y','-i',str(raw),'-af',normalizer,'-ar',str(SR),'-c:a','pcm_s24le',str(base)])
        gain=0.;limiter=None
        target=ROOT.parent/'audio-preview.m4a'
        for iteration in range(4):
            filters=[]
            if limiter is not None:filters.append(f'alimiter=limit={limiter}:level=false:latency=true')
            filters.append(f'volume={gain:.3f}dB')
            call(['ffmpeg','-v','error','-nostdin','-y','-i',str(base),'-af',','.join(filters),'-c:a','aac','-b:a','128k','-ar',str(SR),str(target)])
            actual=measurement(target)
            attempts.append({'gain_db':gain,'limiter':limiter,'filter':','.join(filters),'actual_aac':actual})
            print(iteration,actual['input_i'],actual['input_tp'],flush=True)
            if abs(float(actual['input_i'])+16)<=.3 and float(actual['input_tp'])<=-1.5:break
            adjustment=-16-float(actual['input_i'])
            predicted=float(actual['input_tp'])+adjustment
            gain+=adjustment
            if predicted>-1.8:
                limiter=min(.8,10**((-4-gain)/20))
        else:raise RuntimeError('Audio master did not reach target; do not mark ready')
    report={'status':'audio_passed_video_blocked_image_quota','duration_seconds':sf.info(raw).duration,'first_pass':first,'two_pass_normalizer':normalizer,'mastering_attempts':attempts,'actual_final_aac':attempts[-1]['actual_aac'],'audio_file':'audio-preview.m4a','video_exists':False,'images_generated':0,'manual_listening':'not claimed; automated decoding/loudness validation only'}
    (ROOT/'normalization-settings.json').write_text(json.dumps(report,indent=2)+'\n')
    call(['ffmpeg','-v','error','-xerror','-i',str(ROOT.parent/'audio-preview.m4a'),'-f','null','-'])
    (ROOT.parent/'validation-summary.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
