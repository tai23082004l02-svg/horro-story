"""Rebuild the final static 720p film from saved crops, timing, captions and narration."""
import json
import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def run(args):
    return subprocess.run(args,cwd=ROOT,check=True,capture_output=True,text=True)

def main(audio_only=False):
    timeline=json.loads((ROOT/'timeline.json').read_text())
    raw='assets/narration-raw.flac'
    measured=run(['ffmpeg','-hide_banner','-nostdin','-i',raw,'-af','loudnorm=I=-16:TP=-2.5:LRA=9:print_format=json','-f','null','-'])
    stats=json.loads(re.findall(r'\{[^{}]+\}',measured.stderr)[-1])
    second='loudnorm=I=-16:TP=-2.5:LRA=9:'+':'.join([
        'measured_I='+stats['input_i'],'measured_TP='+stats['input_tp'],
        'measured_LRA='+stats['input_lra'],'measured_thresh='+stats['input_thresh'],
        'offset='+stats['target_offset'],'linear=true','print_format=json'])
    # Calibrated against this recording's first encoded AAC measurement:
    # -16.77 LUFS / -1.37 dBTP. Guard transients before the AAC encoder.
    mastering=',volume=0.85dB,alimiter=limit=0.6:level=false:attack=5:release=50:latency=true,volume=0.95dB'
    settings={'target_i':-16,'normalizer_tp_headroom':-2.5,'delivery_max_tp':-1.5,'raw_measurement':stats,'second_pass_filter':second,'post_normalization_mastering':mastering.lstrip(','),'mastering_basis':'First encoded AAC measured -16.77 LUFS / -1.37 dBTP. Pre-limiter +0.85 dB and limiter produced -16.94 LUFS / -3.24 dBTP. Final +0.95 dB trim calibrated for this exact recording; validate final output independently.'}
    (ROOT/'normalization-settings.json').write_text(json.dumps(settings,indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='hinterkaifeck-render-') as tmp:
        normalized=str(Path(tmp)/'normalized.wav')
        run(['ffmpeg','-hide_banner','-nostdin','-y','-i',raw,'-af',second+mastering,'-ar','48000','-c:a','pcm_s16le',normalized])
        if audio_only:
            fixed=str(Path(tmp)/'fixed.mp4')
            run(['ffmpeg','-hide_banner','-nostdin','-y','-i','../video.mp4','-i',normalized,
                 '-map','0:v:0','-map','1:a:0','-map_metadata','0','-c:v','copy',
                 '-c:a','aac','-b:a','96k','-ar','48000','-ac','1',
                 '-t',str(timeline['duration']),'-movflags','+faststart',fixed])
            # The temporary filesystem can differ from the checkout mount.
            import shutil
            shutil.copyfile(fixed, ROOT.parent/'video-audio-fixed.mp4')
            os.replace(ROOT.parent/'video-audio-fixed.mp4',ROOT.parent/'video.mp4')
            print('Remastered AAC; copied video stream unchanged',flush=True)
            return
        args=['ffmpeg','-hide_banner','-nostdin','-y','-filter_threads','2',
            '-safe','0','-f','concat','-i','images.ffconcat','-i',normalized,
            '-map','0:v:0','-map','1:a:0','-vf','fps=fps=24:round=near,scale=in_range=full:out_range=limited:out_color_matrix=bt709,format=yuv420p,setrange=limited,subtitles=subtitles.ass',
            '-r','24','-fps_mode','cfr','-t',str(timeline['duration']),
            '-c:v','libx264','-preset','medium','-tune','stillimage','-crf','25',
            '-maxrate','850k','-bufsize','1700k','-threads','3',
            '-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709',
            '-color_primaries','bt709','-color_trc','bt709',
            '-c:a','aac','-b:a','96k','-ar','48000','-ac','1',
            '-movflags','+faststart','-metadata','title=Who Stayed After the Murders? | Hinterkaifeck',
            '-metadata','comment=Historical documentary; AI illustrative reconstructions, not evidence photographs; synthetic narration.',
            '../video.mp4']
        with (ROOT/'render.log').open('w') as log:
            subprocess.run(args,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
    print('Rendered',ROOT.parent/'video.mp4',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--audio-only',action='store_true',help='Remaster retained raw narration and copy existing video stream')
    main(parser.parse_args().audio_only)
