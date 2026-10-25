"""Crop reviewed grids, make phrase-aligned still-shot timing and token-based captions."""
import json
import math
import re
import textwrap
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
VIDEO = ROOT.parent
FPS = 24

def write_json(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')

def clock(seconds, srt=False):
    ms = round(seconds * (1000 if srt else 100))
    div = 1000 if srt else 100
    hours, ms = divmod(ms, 3600 * div)
    minutes, ms = divmod(ms, 60 * div)
    seconds, ms = divmod(ms, div)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}' if srt else f'{hours}:{minutes:02d}:{seconds:02d}.{ms:02d}'

def captions(tokens):
    # Punctuation without model timestamps attaches to its preceding spoken token.
    words = []
    for token in tokens:
        if 'start' not in token:
            if words:
                words[-1]['text'] += token['text'] + token.get('whitespace', '')
            continue
        if token['end'] <= token['start']:
            continue
        words.append({'text':token['text']+token.get('whitespace',''), 'start':token['start'], 'end':token['end'], 'chapter':token['chapter']})
    groups, current = [], []
    def flush():
        if current:
            text=''.join(w['text'] for w in current).strip()
            groups.append({'start':current[0]['start'],'end':current[-1]['end'],'text':text,'chapter':current[0]['chapter']})
            current.clear()
    for word in words:
        if current:
            candidate=''.join(w['text'] for w in current)+word['text']
            if word['chapter'] != current[0]['chapter'] or len(candidate.strip()) > 72 or word['end']-current[0]['start']>4.2:
                flush()
        current.append(word)
        if re.search(r'[.!?]["\']?\s*$',word['text']) and word['end']-current[0]['start']>=0.9:
            flush()
    flush()
    for i,cap in enumerate(groups):
        # Extend only within real inter-token silence; never cross the next cue.
        limit=groups[i+1]['start']-0.025 if i+1<len(groups) else cap['end']+0.1
        cap['end']=min(cap['end']+0.09,limit)
        assert cap['end']>cap['start']
        cap['lines']=[cap['text']]
        if len(cap['text'])>42:
            terms=cap['text'].split()
            choices=[(' '.join(terms[:k]),' '.join(terms[k:])) for k in range(1,len(terms))]
            choices=[x for x in choices if max(map(len,x))<=42]
            assert choices,'Caption too long to wrap'
            cap['lines']=list(min(choices,key=lambda x:abs(len(x[0])-len(x[1]))))
    # Verify every spoken grapheme appears once in subtitle order.
    a=re.sub(r'\s+','',''.join(t['text'] for t in tokens))
    b=re.sub(r'\s+','',''.join(c['text'] for c in groups))
    assert a==b, 'Caption text coverage mismatch'
    write_json('captions.json',groups)
    (VIDEO/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{clock(c['start'],True)} --> {clock(c['end'],True)}\n"+'\n'.join(c['lines']) for i,c in enumerate(groups))+'\n')
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,30,&H00FFFFFF,&H00FFFFFF,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,2.2,0.3,2,72,72,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events=[]
    for c in groups:
        txt=r'\N'.join(c['lines']).replace('{','').replace('}','')
        events.append(f"Dialogue: 0,{clock(c['start'])},{clock(c['end'])},Default,,0,0,0,,{txt}")
    (ROOT/'subtitles.ass').write_text(header+'\n'.join(events)+'\n')
    return words

def boundaries(start, end, count, words):
    # Dynamic programming chooses actual word/phrase boundaries, not uniform slices.
    candidates={start:0.0,end:0.0}
    for w in words:
        frame=round((w['end']+0.045)*FPS)
        if start<frame<end:
            punctuation=bool(re.search(r'[.!?]["\']?\s*$',w['text']))
            comma=bool(re.search(r'[,;:]["\']?\s*$',w['text']))
            candidates[frame]=0 if punctuation else (0.45 if comma else 1.4)
    points=sorted(candidates)
    ideal=(end-start)/count
    dp={(0,start):(0,[])}
    for step in range(1,count+1):
        state={}
        for end_frame in points:
            if step==count and end_frame!=end:continue
            if step<count and end_frame==end:continue
            best=None
            for (k,prev),(cost,path) in dp.items():
                duration=end_frame-prev
                if not 3*FPS<=duration<=6*FPS:continue
                if not (count-step)*3*FPS<=end-end_frame<=(count-step)*6*FPS:continue
                score=cost+((duration-ideal)/FPS)**2+candidates[end_frame]
                if best is None or score<best[0]:best=(score,path+[end_frame])
            if best:state[(step,end_frame)]=best
        dp=state
    if (count,end) not in dp:raise RuntimeError(f'No 3–6 second phrase timing for {count} shots in {(end-start)/FPS}s')
    return [start]+dp[(count,end)][1]

def main():
    narrative=json.loads((ROOT/'narrative.json').read_text())
    chapters=json.loads((ROOT/'chapters.json').read_text())
    words=captions(json.loads((ROOT/'tokens.json').read_text()))
    shots=[]
    omitted={'01':[4,6],'02':[1,14],'03':[2,6],'04':[2,7],'05':[4,6],'06':[4,7],'07':[3,6],'08':[4,12]}
    for n,c in zip(narrative,chapters):
        start=round(c['start']*FPS)
        end=round((chapters[int(c['id'])]['start'] if int(c['id'])<len(chapters) else c['end']+0.42+1.1)*FPS)
        selected=[(i,concept) for i,concept in enumerate(n['scenes'],1) if i not in omitted[n['id']]]
        cuts=boundaries(start,end,len(selected),[w for w in words if w['chapter']==n['id']])
        for j,(i,concept) in enumerate(selected):
            id=f"{n['id']}-{i:02d}"
            shots.append({'id':id,'chapter':n['id'],'image':f'assets/images/{id}.png','concept':concept,'start_frame':cuts[j],'end_frame':cuts[j+1],'frames':cuts[j+1]-cuts[j],'start':cuts[j]/FPS,'end':cuts[j+1]/FPS,'image_status':'not_generated_quota_blocked','source_requirement':'one full frame source image, at least1280x720; do not crop grid cells or upsample low resolution art'})
    write_json('shots.json',shots)
    write_json('timeline.json',{'status':'planned_audio_timed_images_missing','fps':24,'frames':shots[-1]['end_frame'],'duration':shots[-1]['end'],'shots':shots,'outro_sfx_seconds':1.1})
    print('Planned',len(shots),'shots,',shots[-1]['end'],'seconds; NO IMAGES GENERATED')

if __name__=='__main__':main()
