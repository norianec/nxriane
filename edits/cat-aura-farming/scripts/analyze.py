import sys, json, numpy as np, librosa
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True, duration=48)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
print('tempo', tempo)
print('beats', np.round(beats,3).tolist())
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=256))
f = librosa.fft_frequencies(sr=sr, n_fft=2048)
t = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=256)
def band(lo,hi):
    e = S[(f>=lo)&(f<hi)].sum(0); return e/ (e.max()+1e-9)
low=band(20,120); mid=band(400,2500); hi=band(5000,11000)
rms = librosa.feature.rms(y=y, hop_length=256)[0]
def onsets(e, delta):
    env = np.maximum(0, np.diff(e, prepend=e[0]))
    pk = librosa.util.peak_pick(env, pre_max=6, post_max=6, pre_avg=20, post_avg=20, delta=delta, wait=20)
    return [(round(float(t[i]),3), round(float(env[i]),3)) for i in pk]
out = dict(tempo=float(np.atleast_1d(tempo)[0]), beats=beats.tolist(), low=onsets(low,0.08), mid=onsets(mid,0.06), hi=onsets(hi,0.06))
# per-second loudness
sec = [round(float(rms[(t>=s)&(t<s+1)].mean()),4) for s in range(48)]
out['rms_per_sec']=sec
print('low onsets', out['low']); print('mid onsets', out['mid']); print('rms/sec', sec)
json.dump(out, open(sys.argv[2],'w'))
