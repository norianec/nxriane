import sys, numpy as np, librosa, cv2
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True, duration=48)
hop=64
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=4096, hop_length=hop, n_mels=200, fmin=250, fmax=3000)
D = librosa.power_to_db(S, ref=np.max); img=((D+70)/70).clip(0,1)
img=cv2.applyColorMap((img[::-1]*255).astype(np.uint8), cv2.COLORMAP_MAGMA)
fps=sr/hop
for a in range(0,48,8):
    b=a+8; seg=cv2.resize(img[:,int(a*fps):int(b*fps)],(1600,300))
    c=np.zeros((330,1600,3),np.uint8); c[:300]=seg
    for i in range(0,81):
        s=a+i*0.1; x=int(i/80*1599)
        cv2.line(c,(x,300),(x,305 if i%5 else (312 if i%10 else 318)),(255,255,255),1)
        if i%5==0: cv2.putText(c,f'{s:.1f}' if i%10==0 else '.5',(x+2,328),cv2.FONT_HERSHEY_SIMPLEX,0.35,(255,255,255),1)
        if i%10==0: cv2.line(c,(x,0),(x,300),(0,255,0),1)
    cv2.imwrite(f'analysis/zoom_{a:02d}.png',c)
