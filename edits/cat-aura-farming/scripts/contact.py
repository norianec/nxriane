import sys, glob, os, cv2, numpy as np
fs = sorted(glob.glob(sys.argv[1]))
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 7
tw, th = 270, 480
rows = (len(fs) + cols - 1) // cols
sheet = np.zeros((rows * (th + 24), cols * tw, 3), np.uint8)
for i, f in enumerate(fs):
    im = cv2.resize(cv2.imread(f), (tw, th), interpolation=cv2.INTER_AREA)
    r, c = divmod(i, cols)
    sheet[r*(th+24):r*(th+24)+th, c*tw:(c+1)*tw] = im
    cv2.putText(sheet, os.path.basename(f)[2:-4], (c*tw+4, r*(th+24)+th+17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
cv2.imwrite(sys.argv[2], sheet, [cv2.IMWRITE_JPEG_QUALITY, 82])
