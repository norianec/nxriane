import sys, json, numpy as np, librosa
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True, duration=46)
hop=256
S = np.abs(librosa.stft(y, n_fft=4096, hop_length=hop))
f = librosa.fft_frequencies(sr=sr, n_fft=4096)
t = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr, hop_length=hop)
# log-frequency representation, 1/8 semitone bins 300-2600Hz
bins = 440*2**((np.arange(-30*8, 30*8)/8 - 0)/12)
sel = (bins>300)&(bins<2600); bins=bins[sel]
L = np.stack([np.interp(bins, f, S[:,i]) for i in range(S.shape[1])],1)
L = np.log1p(L*10)
L = L - np.median(L,axis=1,keepdims=True)  # remove steady notes (horizontal lines)
L = np.maximum(L,0)
# glide score: correlation between frame i and frame i-k shifted by s bins (s != 0) vs unshifted
k=3; score=np.zeros(L.shape[1]); dirn=np.zeros(L.shape[1])
for i in range(k,L.shape[1]):
    a=L[:,i]; b=L[:,i-k]
    base=(a*b).sum()+1e-6
    best=0;bd=0
    for s in range(1,7):
        up=(a[s:]*b[:-s]).sum(); dn=(a[:-s]*b[s:]).sum()
        if up>best: best,bd=up,1
        if dn>best: best,bd=dn,-1
    score[i]=max(0,best-base)/ (np.linalg.norm(a)*np.linalg.norm(b)+1e-6)
    dirn[i]=bd
sm=np.convolve(score,np.ones(5)/5,'same')
pk=librosa.util.peak_pick(sm,pre_max=15,post_max=15,pre_avg=40,post_avg=40,delta=0.03,wait=30)
ev=[]
for p in pk:
    lo=p
    while lo>0 and sm[lo]>sm[p]*0.35: lo-=1
    hi=p
    while hi<len(sm)-1 and sm[hi]>sm[p]*0.35: hi+=1
    d=np.sign(dirn[lo:hi+1].sum())
    ev.append(dict(t=round(float(t[p]),2),start=round(float(t[lo]),2),end=round(float(t[hi]),2),strength=round(float(sm[p]),3),dir='up' if d>0 else 'down'))
for e in ev: print(e)
json.dump(ev,open(sys.argv[2],'w'),indent=0)
