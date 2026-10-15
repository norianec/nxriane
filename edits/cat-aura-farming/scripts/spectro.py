import sys, numpy as np, librosa, cv2
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True, duration=48)
S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=2048, hop_length=128, n_mels=160, fmax=8000)
D = librosa.power_to_db(S, ref=np.max)
img = ((D+80)/80).clip(0,1)
img = (img[::-1]*255).astype(np.uint8)
img = cv2.applyColorMap(img, cv2.COLORMAP_MAGMA)
fps = sr/128
for k,(a,b) in enumerate([(0,8),(8,16),(16,24),(24,32),(32,40),(40,48)]):
    seg = img[:, int(a*fps):int(b*fps)]
    seg = cv2.resize(seg, (1600, 480), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((520,1600,3),np.uint8); canvas[:480]=seg
    for s in np.arange(a,b+0.001,0.5):
        x=int((s-a)/(b-a)*1599); 
        cv2.line(canvas,(x,480),(x,490 if s%1 else 500),(255,255,255),1)
        if s%1==0: cv2.putText(canvas,str(int(s)),(x+2,515),cv2.FONT_HERSHEY_SIMPLEX,0.45,(255,255,255),1)
    # freq labels
    for hz in [100,500,1000,2000,4000]:
        m = librosa.hz_to_mel(hz); mm = librosa.hz_to_mel(8000)
        yy = int(480 - m/mm*480); cv2.putText(canvas,f'{hz}',(2,yy),cv2.FONT_HERSHEY_SIMPLEX,0.4,(0,255,0),1)
    cv2.imwrite(f'analysis/spec_{a:02d}_{b:02d}.png', canvas)
