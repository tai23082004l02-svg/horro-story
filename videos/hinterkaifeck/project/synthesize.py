"""Generate real Kokoro audio and token timestamps. Run with the Kokoro venv."""
import json
import os
import re
from pathlib import Path

os.environ.setdefault('HF_HOME', '/workspace/.cache/huggingface')
os.environ.setdefault('XDG_CACHE_HOME', '/workspace/.cache')
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
os.environ.setdefault('OMP_NUM_THREADS', '2')
import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
SR = 24000
PRONUNCIATIONS = {
    'Hinterkaifeck': 'hˌɪntɚkˈaɪfɛk',
    'Cazilia': 'tsɛtsˈiliə',
    'Cilli': 'tsˈɪli',
    'Groebern': 'ɡɹˈɜɹbɚn',
    'Hofner': 'hˈɔfnɚ',
    'Schlittenbauer': 'ʃlˈɪtənbaʊɚ',
    'Poell': 'pˈɛl',
    'Sigl': 'zˈiɡəl',
}

def main():
    torch.set_num_threads(2)
    chapters = json.loads((ROOT / 'narrative.json').read_text())
    cache = ROOT / 'assets' / 'voice-segments'
    cache.mkdir(parents=True, exist_ok=True)
    pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M', device='cpu')
    pieces, tokens, chapter_times = [], [], []
    offset = 0.0
    for chapter in chapters:
        chapter_start = offset
        wavpath = cache / f"{chapter['id']}.flac"
        metapath = cache / f"{chapter['id']}.json"
        if wavpath.exists() and metapath.exists():
            audio, sr = sf.read(wavpath, dtype='float32')
            assert sr == SR
            local_tokens = json.loads(metapath.read_text())
        else:
            text = chapter['text']
            for name, phonemes in PRONUNCIATIONS.items():
                text = re.sub(r'\b' + re.escape(name) + r'\b', lambda m: f'[{m[0]}](/{phonemes}/)', text)
            local_pieces, local_tokens = [], []
            local_offset = 0.0
            for result in pipeline(text, voice='am_michael', speed=1.07):
                samples = result.audio.numpy()
                assert np.isfinite(samples).all() and len(samples) > 0
                duration = len(samples) / SR
                for token in result.tokens or []:
                    item = {'text': token.text, 'whitespace': token.whitespace}
                    if token.start_ts is not None and token.end_ts is not None:
                        item.update(start=local_offset + max(0, token.start_ts), end=local_offset + min(duration, token.end_ts))
                    local_tokens.append(item)
                local_pieces.extend([samples, np.zeros(int(0.18*SR), dtype=np.float32)])
                local_offset += duration + 0.18
            audio = np.concatenate(local_pieces)
            sf.write(wavpath, audio, SR, subtype='PCM_16')
            metapath.write_text(json.dumps(local_tokens, indent=2))
        pieces.append(audio)
        for token in local_tokens:
            item = dict(token, chapter=chapter['id'])
            if 'start' in item:
                item['start'] += offset
                item['end'] += offset
            tokens.append(item)
        offset += len(audio) / SR
        chapter_times.append({'id':chapter['id'], 'name':chapter['name'], 'start':chapter_start, 'end':offset})
        pieces.append(np.zeros(int(0.42*SR),dtype=np.float32))
        offset += 0.42
        print(chapter['id'], round(offset, 2), flush=True)
    result = np.concatenate(pieces)
    sf.write(ROOT / 'assets' / 'narration-raw.flac', result, SR, subtype='PCM_16')
    (ROOT / 'tokens.json').write_text(json.dumps(tokens, indent=2))
    (ROOT / 'chapters.json').write_text(json.dumps(chapter_times, indent=2))
    (ROOT / 'pronunciations.json').write_text(json.dumps(PRONUNCIATIONS,ensure_ascii=False,indent=2))
    print('DONE', len(result)/SR, 'seconds', flush=True)

if __name__ == '__main__':
    main()
