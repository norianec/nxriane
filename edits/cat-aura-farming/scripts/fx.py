"""Frame-level effects for the CAT AURA FARMING edit (numpy + OpenCV, deterministic)."""
import math
import numpy as np
import cv2

W, H = 1080, 1920


def ease_in_out(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - (1 - u) ** 3


def ease_in(u):
    u = min(max(u, 0.0), 1.0)
    return u ** 3


def rng_for(*keys):
    h = 0
    for k in keys:
        h = (h * 1000003 + int(round(k * 1000))) & 0xFFFFFFFF
    return np.random.default_rng(h)


# ---------------------------------------------------------------- grading

GRADES = {
    # luminance -> colour stops (RGB 0..255)
    "blood": [(0.0, (0, 0, 0)), (0.18, (22, 2, 4)), (0.42, (120, 8, 16)),
              (0.68, (230, 60, 30)), (0.86, (255, 170, 70)), (1.0, (255, 240, 205))],
    "cosmic": [(0.0, (0, 0, 2)), (0.2, (26, 4, 48)), (0.42, (110, 14, 96)),
               (0.62, (215, 30, 70)), (0.82, (255, 150, 60)), (1.0, (255, 244, 220))],
    "void": [(0.0, (0, 0, 0)), (0.3, (18, 10, 12)), (0.6, (90, 60, 62)),
             (0.85, (200, 150, 130)), (1.0, (250, 235, 220))],
}


def grade_image(bgr, grade, mix=0.55, contrast=1.15, sat=1.1):
    img = bgr.astype(np.float32) / 255.0
    # s-curve contrast, crushed blacks
    img = np.clip((img - 0.5) * contrast + 0.5 - 0.03, 0, 1)
    img = img ** 1.12
    lum = img[..., 0] * 0.114 + img[..., 1] * 0.587 + img[..., 2] * 0.299
    stops = GRADES[grade]
    xs = np.array([s[0] for s in stops], np.float32)
    mapped = np.zeros_like(img)
    for c_out, c_rgb in ((0, 2), (1, 1), (2, 0)):  # BGR out, RGB stops
        ys = np.array([s[1][c_rgb] for s in stops], np.float32) / 255.0
        mapped[..., c_out] = np.interp(lum, xs, ys)
    # keep the gold of the eyes: where original is saturated warm, mix less
    b, g, r = img[..., 0], img[..., 1], img[..., 2]
    warm = np.clip((r - b) * 1.4, 0, 1) * np.clip((g - b) * 2.0, 0, 1)
    m = mix * (1 - 0.6 * warm)
    out = img * (1 - m[..., None]) + mapped * m[..., None]
    gray = out.mean(axis=2, keepdims=True)
    out = np.clip(gray + (out - gray) * sat, 0, 1)
    return (out * 255).astype(np.uint8)


# ---------------------------------------------------------------- camera

def cover_affine(sw, sh, zoom, cx, cy, rot, ox, oy):
    """Affine mapping source -> output; (cx, cy) normalised source point lands at
    the output centre (+offset). zoom 1 = cover-fit."""
    s = max(W / sw, H / sh) * zoom
    hw, hh = W / 2 / s, H / 2 / s
    px = min(max(cx * sw, hw), sw - hw) if sw > 2 * hw else sw / 2
    py = min(max(cy * sh, hh), sh - hh) if sh > 2 * hh else sh / 2
    M = cv2.getRotationMatrix2D((px, py), rot, s)
    M[0, 2] += W / 2 + ox - px
    M[1, 2] += H / 2 + oy - py
    return M


def warp(src, M):
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def apply_pt(M, x, y):
    return (M[0, 0] * x + M[0, 1] * y + M[0, 2], M[1, 0] * x + M[1, 1] * y + M[1, 2])


# ---------------------------------------------------------------- static layers

_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_dx, _dy = _xx - W / 2, _yy - H / 2
_rad = np.sqrt(_dx ** 2 + _dy ** 2)
VIGNETTE = (1 - 0.62 * np.clip((_rad / (0.5 * math.hypot(W, H))) ** 2.2, 0, 1)).astype(np.float32)[..., None]

_grain_rng = np.random.default_rng(7)
GRAIN = [(_grain_rng.standard_normal((H // 2, W // 2)).astype(np.float32)) for _ in range(6)]


def grain(frame, t, amt=0.045):
    g = GRAIN[int(t * 24) % len(GRAIN)]
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    return frame + g[..., None] * amt


# ---------------------------------------------------------------- effects

def bloom(frame, thresh=0.62, amt=0.55, radius=18):
    small = cv2.resize(frame, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    hi = np.clip(small - thresh, 0, None) / (1 - thresh)
    hi = cv2.GaussianBlur(hi, (0, 0), radius / 4) + cv2.GaussianBlur(hi, (0, 0), radius) * 0.6
    return frame + cv2.resize(hi, (W, H), interpolation=cv2.INTER_LINEAR) * amt


def chroma(frame, amt):
    if amt < 0.5:
        return frame
    out = frame.copy()
    for ch, k in ((2, 1), (0, -1)):
        s = 1 + k * amt / 900.0
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
        out[..., ch] = cv2.warpAffine(frame[..., ch], M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return out


def zoom_blur(frame, amt):
    if amt < 0.004:
        return frame
    acc = frame * 0.4
    for i, wgt in ((1, 0.3), (2, 0.2), (3, 0.1)):
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + amt * i)
        acc += cv2.warpAffine(frame, M, (W, H), borderMode=cv2.BORDER_REFLECT) * wgt
    return acc


def heat(frame, t, amt):
    if amt < 0.3:
        return frame
    sx = (np.sin(_yy / 23.0 + t * 7.0) + 0.6 * np.sin(_yy / 9.0 - t * 11.0 + _xx / 51.0)) * amt
    sy = (np.cos(_xx / 29.0 + t * 5.0)) * amt * 0.6
    return cv2.remap(frame, _xx + sx, _yy + sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def shockwave(frame, age, strength=1.0, cx=W / 2, cy=H / 2):
    dur = 0.45
    if age < 0 or age > dur:
        return frame
    u = age / dur
    r = 80 + 1500 * ease_out(u)
    width = 90 + 120 * u
    dx, dy = _xx - cx, _yy - cy
    d = np.sqrt(dx * dx + dy * dy) + 1e-3
    prof = np.exp(-((d - r) / width) ** 2) * (1 - u) * 60 * strength
    mx = _xx - dx / d * prof
    my = _yy - dy / d * prof
    out = cv2.remap(frame, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    ring = (np.exp(-((d - r) / (width * 0.35)) ** 2) * (1 - u) * 0.35 * strength)[..., None]
    return out + ring


def _bolt(rng, x0, y0, x1, y1, disp, depth, pts):
    if depth == 0:
        pts.append(((x0, y0), (x1, y1), disp))
        return
    mx = (x0 + x1) / 2 + rng.normal() * disp
    my = (y0 + y1) / 2 + rng.normal() * disp * 0.3
    _bolt(rng, x0, y0, mx, my, disp / 2, depth - 1, pts)
    _bolt(rng, mx, my, x1, y1, disp / 2, depth - 1, pts)
    if depth >= 3 and rng.random() < 0.35:
        ang = math.atan2(y1 - y0, x1 - x0) + rng.normal() * 0.8
        ln = math.hypot(x1 - x0, y1 - y0) * 0.6
        _bolt(rng, mx, my, mx + math.cos(ang) * ln, my + math.sin(ang) * ln, disp / 2, depth - 2, pts)


def lightning_layer(seed_t, color, region="top", n=2):
    rng = rng_for(seed_t, 99)
    lay = np.zeros((H // 2, W // 2, 3), np.float32)
    core = np.zeros((H // 2, W // 2), np.float32)
    for _ in range(n):
        if region == "top":
            side = rng.random() < 0.5
            x0 = rng.uniform(0, W * 0.14) if side else rng.uniform(W * 0.36, W * 0.5)
            y0 = -10
            x1 = x0 + rng.uniform(-60, 60)
            y1 = rng.uniform(H * 0.16, H * 0.32)
        else:
            x0, y0 = rng.uniform(0, W / 2), -10
            x1, y1 = rng.uniform(0, W / 2), H / 2 + 10
        pts = []
        _bolt(rng, x0, y0, x1, y1, 70, 7, pts)
        for (a, b, dsp) in pts:
            th = 2 if dsp > 5 else 1
            cv2.line(core, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])), 1.0, th, cv2.LINE_AA)
    glow = cv2.GaussianBlur(core, (0, 0), 6) * 2.2 + cv2.GaussianBlur(core, (0, 0), 22) * 1.6
    col = np.array(color, np.float32)[::-1] / 255.0
    lay = glow[..., None] * col + core[..., None] * 1.0
    return cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)


def speed_lines(t, amt, color=(1, 1, 1)):
    if amt < 0.05:
        return None
    rng = rng_for(int(t * 15) / 15.0, 5)
    lay = np.zeros((H // 2, W // 2), np.float32)
    cx, cy = W / 4, H / 4
    for _ in range(70):
        a = rng.uniform(0, 2 * math.pi)
        r0 = rng.uniform(260, 420) / 2
        r1 = 1300
        wdt = int(rng.integers(1, 4))
        p0 = (int(cx + math.cos(a) * r0 * 1.6), int(cy + math.sin(a) * r0 * 1.6))
        p1 = (int(cx + math.cos(a) * r1), int(cy + math.sin(a) * r1))
        cv2.line(lay, p0, p1, float(rng.uniform(0.4, 1.0)), wdt, cv2.LINE_AA)
    lay = cv2.resize(lay, (W, H))
    return lay[..., None] * np.array(color, np.float32) * amt


def eye_mask(pts, rad):
    m = np.zeros((H // 4, W // 4), np.float32)
    for (x, y) in pts:
        cv2.ellipse(m, (int(x / 4), int(y / 4)), (max(2, int(rad / 4)), max(1, int(rad / 7))), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), max(1.0, rad / 14))
    return np.clip(cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR) * 1.3, 0, 1)


def eye_glow(frame, pts, amt, color=(255, 190, 80), streak=True, rad=60):
    if amt < 0.02 or not pts:
        return frame
    small = np.zeros((H // 4, W // 4), np.float32)
    streaks = np.zeros((H // 4, W // 4), np.float32)
    for (x, y) in pts:
        if -200 < x < W + 200 and -200 < y < H + 200:
            cv2.circle(small, (int(x / 4), int(y / 4)), max(2, int(rad / 16)), 1.0, -1, cv2.LINE_AA)
            if streak:
                cv2.line(streaks, (int(x / 4) - 160, int(y / 4)), (int(x / 4) + 160, int(y / 4)), 1.0, 1, cv2.LINE_AA)
    g = cv2.GaussianBlur(small, (0, 0), rad / 10) * 1.6 + cv2.GaussianBlur(small, (0, 0), rad / 3) * 0.9
    if streak:
        g += cv2.GaussianBlur(streaks, (0, 0), 1.5) * 0.9 + cv2.GaussianBlur(streaks, (0, 0), 4) * 0.5
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    col = np.array(color[::-1], np.float32) / 255.0
    return frame + g[..., None] * col * amt


class Particles:
    """Deterministic particle fields keyed by shot id."""

    def __init__(self, kind, seed, n):
        rng = np.random.default_rng(seed)
        self.kind = kind
        self.n = n
        self.x = rng.uniform(0, W, n)
        self.y = rng.uniform(0, H, n)
        self.z = rng.uniform(0.2, 1.0, n)
        self.ph = rng.uniform(0, 2 * math.pi, n)
        self.sp = rng.uniform(0.6, 1.4, n)

    def render(self, t, amt=1.0, speed=1.0, color=(255, 110, 40)):
        lay = np.zeros((H // 2, W // 2), np.float32)
        k = self.kind
        if k == "rain":
            for i in range(self.n):
                y = (self.y[i] + t * 2600 * self.sp[i] * speed) % (H + 200) - 100
                x = (self.x[i] + y * 0.12) % W
                ln = 50 * self.z[i] * speed
                cv2.line(lay, (int(x / 2), int(y / 2)), (int((x - ln * 0.12) / 2), int((y - ln) / 2)),
                         float(0.25 + 0.5 * self.z[i]), 1, cv2.LINE_AA)
        elif k == "embers":
            for i in range(self.n):
                y = (self.y[i] - t * 260 * self.sp[i] * speed) % (H + 100) - 50
                x = self.x[i] + math.sin(t * 2 * self.sp[i] + self.ph[i]) * 40
                r = 1 + 2.5 * self.z[i]
                fl = 0.6 + 0.4 * math.sin(t * 9 + self.ph[i])
                cv2.circle(lay, (int(x / 2), int(y / 2)), max(1, int(r / 2 + 0.5)), float(fl), -1, cv2.LINE_AA)
        elif k == "dust":
            for i in range(self.n):
                y = (self.y[i] - t * 25 * self.sp[i] * speed) % H
                x = (self.x[i] + math.sin(t * 0.7 + self.ph[i]) * 30) % W
                cv2.circle(lay, (int(x / 2), int(y / 2)), 1, float(0.35 + 0.4 * self.z[i]), -1, cv2.LINE_AA)
        elif k == "warp":
            cx, cy = W / 2, H * 0.45
            for i in range(self.n):
                zz = ((self.z[i] - t * 0.35 * speed * self.sp[i]) % 1.0) + 0.02
                zp = zz + 0.02 * speed
                ax, ay = (self.x[i] - W / 2) * 1.6, (self.y[i] - H / 2) * 1.2
                p0 = (cx + ax / zz * 0.25, cy + ay / zz * 0.25)
                p1 = (cx + ax / zp * 0.25, cy + ay / zp * 0.25)
                b = float(min(1.0, 0.15 / zz))
                cv2.line(lay, (int(p0[0] / 2), int(p0[1] / 2)), (int(p1[0] / 2), int(p1[1] / 2)), b, 1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 0.8) + cv2.GaussianBlur(lay, (0, 0), 4) * 0.8
        lay = cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)
        col = np.array(color[::-1], np.float32) / 255.0
        return lay[..., None] * col * amt
