"""Render only after all new full-frame images pass preflight. Images are currently missing."""
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent

def preflight():
    shots=json.loads((ROOT/'shots.json').read_text())
    missing=[];small=[]
    for s in shots:
        path=ROOT/s['image']
        if not path.exists():missing.append(s['id']);continue
        with Image.open(path) as im:
            if im.width<1280 or im.height<720:small.append({'id':s['id'],'size':list(im.size)})
    report={'status':'blocked_images' if missing or small else 'assets_present_manual_review_required','planned_shots':len(shots),'missing_images':missing,'undersized_images':small,'source_minimum':[1280,720],'video_rendered':False}
    (ROOT/'visual-preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    return shots,report

def main(check_only=False):
    shots,report=preflight()
    if check_only:
        print(json.dumps(report,indent=2));return
    if report['missing_images'] or report['undersized_images']:
        raise RuntimeError('Cannot render: missing or undersized new story images. See visual-preflight.json')
    accepted=json.loads((ROOT/'curation-notes.json').read_text())
    if set(accepted['accepted_ids'])!={s['id'] for s in shots}:
        raise RuntimeError('Manual visual review must cover all selected images')
    frames=ROOT/'assets/frames';frames.mkdir(exist_ok=True)
    concat=['ffconcat version 1.0'];crops=[]
    for s in shots:
        with Image.open(ROOT/s['image']) as im:
            width,height=im.size
            crop_width=min(width,round(height*16/9));crop_height=min(height,round(width*9/16))
            left=(width-crop_width)//2;top=(height-crop_height)//2;box=[left,top,left+crop_width,top+crop_height]
            out=f"assets/frames/{s['id']}.jpg"
            im.convert('RGB').crop(box).resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/out,quality=96,subsampling=0)
            crops.append({'id':s['id'],'source':s['image'],'source_size':[width,height],'crop':box,'output':out,'output_size':[1280,720],'upsampled':False})
        concat.extend([f"file '{out}'",'option framerate 24',f"duration {s['frames']/24:.9f}"])
    concat.extend([f"file '{out}'",'option framerate 24'])
    (ROOT/'images.ffconcat').write_text('\n'.join(concat)+'\n')
    (ROOT/'image-crops.json').write_text(json.dumps(crops,indent=2)+'\n')
    duration=json.loads((ROOT/'timeline.json').read_text())['duration']
    cmd=['ffmpeg','-hide_banner','-nostdin','-y','-filter_threads','2','-safe','0','-f','concat','-i','images.ffconcat',
         '-i','../audio-preview.m4a','-map','0:v:0','-map','1:a:0',
         '-vf','fps=fps=24:round=near,scale=in_range=full:out_range=limited:out_color_matrix=bt709,format=yuv420p,setrange=limited,subtitles=subtitles.ass',
         '-t',str(duration),'-r','24','-fps_mode','cfr','-c:v','libx264','-preset','medium','-tune','stillimage','-crf','23','-maxrate','1500k','-bufsize','3000k','-threads','3',
         '-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',
         '-c:a','copy','-movflags','+faststart','-metadata','title=The Last Voice on Channel Nine | Original Horror Story','../video.mp4']
    with (ROOT/'render.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
    print('Rendered video; final MP4 validation is still required')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check-only',action='store_true');main(p.parse_args().check_only)
