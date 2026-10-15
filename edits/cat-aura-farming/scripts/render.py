"""Render CAT AURA FARMING (1080x1920, 30 fps) from stills + timeline.

usage:
  python3 render.py preview 0.0 16.6 33.1          # PNG frames into out/preview/
  python3 render.py video [--workers 4] [--draft]  # out/cat_aura_farming.mp4
"""
import math
import os
import subprocess
import sys
from multiprocessing import Pool

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx  # noqa: E402
import timeline as tl  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STILLS = os.path.join(ROOT, "assets", "stills")
OUT = os.path.join(ROOT, "out")
AUDIO = os.path.join(ROOT, "assets", "purr_of_death.wav")
W, H, FPS = fx.W, fx.H, tl.FPS

FALLBACK = {"14_eyes_closed": "01_eyes_dark", "05_profile_wind": "07_meow_side", "07_meow_side": "00_hero"}

_cache = {}
_particles = {}


def still_name(name):
    while not os.path.exists(os.path.join(STILLS, name + ".png")):
        name = FALLBACK[name]
    return name


def graded(name, grade, mirror, mix):
    key = (name, grade, mirror, mix)
    if key not in _cache:
        img = cv2.imread(os.path.join(STILLS, name + ".png"), cv2.IMREAD_COLOR)
        if mirror:
            img = img[:, ::-1].copy()
        _cache[key] = fx.grade_image(img, grade, mix=mix)
    return _cache[key]


def particles(kind, idx):
    key = (kind, idx)
    if key not in _particles:
        n = {"rain": 260, "embers": 110, "dust": 160, "warp": 260}[kind]
        _particles[key] = fx.Particles(kind, 1000 + idx * 17 + len(kind), n)
    return _particles[key]


def shot_at(t):
    idx = 0
    for i, s in enumerate(tl.SHOTS):
        if s["t0"] <= t + 1e-6:
            idx = i
    s = tl.SHOTS[idx]
    t1 = tl.SHOTS[idx + 1]["t0"] if idx + 1 < len(tl.SHOTS) else tl.DUR
    return idx, s, t1


def decay(age, tau):
    return math.exp(-age / tau) if age >= 0 else 0.0


def phase(t):
    if t < 16.5:
        return "intro"
    if t < 31.0:
        return "dominant"
    if t < 33.07:
        return "calm"
    return "cosmic"


def impulses(t, shot, shot_t0):
    """Sum of all time-based impulses at time t."""
    imp = dict(punch=0.0, shake=0.0, rgb=0.0, red=0.0, white=0.0, violet=0.0, zblur=0.0,
               flare=0.0, speed=0.0, light=0.0, light_seed=None, invert=False, shock=None, heat=0.0)
    for b in tl.BASS:
        age = t - b
        if 0 <= age < 1.0:
            k = 1.15 if b >= 33 else 1.0
            imp["punch"] += 0.075 * k * decay(age, 0.10)
            imp["shake"] += 14 * k * decay(age, 0.13)
            imp["rgb"] += 9 * k * decay(age, 0.11)
            imp["zblur"] += 0.010 * k * decay(age, 0.07)
            if b >= 33:
                imp["violet"] += 0.10 * decay(age, 0.06)
            else:
                imp["red"] += 0.12 * decay(age, 0.06)
            if "lightning_bg" in shot["fx"] and age < 0.3 and b >= shot_t0 - 1e-3:
                fl = [1, 0.25, 0.9, 0.5, 0.15, 0.6, 0.2, 0.05, 0.0][min(8, int(age * FPS))]
                if fl * 0.8 > imp["light"]:
                    imp["light"], imp["light_seed"] = fl * 0.8, b
    for m, shape in tl.MEOWS:
        age = t - m
        if 0 <= age < 1.5:
            ph = phase(m)
            big = 1.0 if shape != "down" else 0.8
            imp["flare"] += big * (1.2 if ph != "intro" else 1.0) * decay(age, 0.32)
            imp["punch"] += (0.035 if ph == "intro" else 0.055) * decay(age, 0.2)
            imp["rgb"] += (3 if ph == "intro" else 7) * decay(age, 0.18)
            imp["speed"] += decay(age, 0.28) if "speed" in shot["fx"] else 0.0
            if ph == "intro":
                imp["shake"] += 3 * decay(age, 0.2)
    for (e, kind, st) in tl.EVENTS:
        age = t - e
        if age < 0:
            continue
        if kind == "shockwave" and age < 0.5:
            imp["shock"] = (age, st)
        elif kind == "flash_white":
            imp["white"] += st * decay(age, 0.18)
        elif kind == "flash_violet":
            imp["violet"] += st * 0.9 * decay(age, 0.2)
        elif kind == "lightning" and age < 0.35:
            fl = [1, 0.3, 1, 0.7, 0.2, 0.8, 0.4, 0.1, 0.5, 0.1, 0.0][min(10, int(age * FPS))]
            if fl * st > imp["light"]:
                imp["light"], imp["light_seed"] = fl * st, e
        elif kind == "invert" and age < 2.5 / FPS:
            imp["invert"] = True
        elif kind == "riser":
            end = 16.25 if e < 20 else 33.07
            if t < end:
                u = (t - e) / (end - e)
                r = fx.ease_in(u)
                imp["shake"] += 16 * r * st
                imp["rgb"] += 14 * r * st
                imp["zblur"] += 0.012 * r * st
                imp["heat"] += 5 * r * st
    return imp


def render_shot(t, idx, s, t1, imp):
    name = still_name(s["img"])
    src = graded(name, s["grade"], s["mirror"], s["mix"])
    sh, sw = src.shape[:2]
    u = (t - s["t0"]) / max(1e-3, t1 - s["t0"])
    e = {"inout": fx.ease_in_out, "in": fx.ease_in, "out": fx.ease_out}[s["ease"]](u)
    z = s["z"][0] + (s["z"][1] - s["z"][0]) * e
    cx = s["c0"][0] + (s["c1"][0] - s["c0"][0]) * e
    cy = s["c0"][1] + (s["c1"][1] - s["c0"][1]) * e
    rot = s["rot"][0] + (s["rot"][1] - s["rot"][0]) * e
    z *= 1 + imp["punch"]
    a = imp["shake"]
    ox = a * (math.sin(t * 53.1) + 0.7 * math.sin(t * 87.3 + 1.3)) / 1.7
    oy = a * (math.sin(t * 47.9 + 2.1) + 0.7 * math.sin(t * 71.7)) / 1.7
    rot += a * 0.05 * math.sin(t * 39.0)
    M = fx.cover_affine(sw, sh, z, cx, cy, rot, ox, oy)
    frame = fx.warp(src, M).astype(np.float32) / 255.0

    # eyes in frame coordinates
    eyes = []
    for (ex, ey) in tl.EYES.get(name, []):
        if s["mirror"]:
            ex = 1 - ex
        eyes.append(fx.apply_pt(M, ex * sw, ey * sh))

    heat_amt = (2.2 if "heat" in s["fx"] else 0) + imp["heat"]
    frame = fx.heat(frame, t, heat_amt)

    if s["dark"] is not None:
        d = s["dark"][0] + (s["dark"][1] - s["dark"][0]) * fx.ease_in_out(u)
        frame *= (1 - d * (1 - fx.eye_mask(eyes, 46 * z))[..., None])

    cosmic = s["grade"] == "cosmic"
    # particles
    for kind in ("rain", "embers", "dust", "warp"):
        if kind in s["fx"]:
            col = {"rain": (255, 70, 60), "embers": (255, 120, 40), "dust": (255, 200, 170),
                   "warp": (200, 150, 255)}[kind]
            spd = 1.0 + (6 * imp["punch"] if kind == "warp" else 0)
            amt = {"rain": 0.55, "embers": 0.9, "dust": 0.45, "warp": 0.75}[kind]
            frame += particles(kind, idx).render(t - s["t0"], amt=amt, speed=spd, color=col)

    # lightning
    if imp["light"] > 0.02 and imp["light_seed"] is not None:
        col = (190, 90, 255) if cosmic or t >= 33 else (255, 40, 50)
        frame = 1 - (1 - np.clip(frame, 0, 1)) * (1 - np.clip(fx.lightning_layer(imp["light_seed"], col, n=3) * imp["light"], 0, 1))
        frame += (np.array(col[::-1], np.float32) / 255.0) * 0.08 * imp["light"]

    # eyes: base glow + meow flares (anamorphic streak)
    eamt = s["eye"] * (0.35 + imp["flare"])
    ecol = (255, 205, 120) if not cosmic else (255, 215, 150)
    frame = fx.eye_glow(frame, eyes, eamt, color=ecol, streak=imp["flare"] > 0.25, rad=70 * max(1.0, z))

    sp = fx.speed_lines(t, min(1.0, imp["speed"]) * 0.55)
    if sp is not None:
        frame = frame + sp
    return frame


def letterbox_amt(t):
    if 31.0 <= t < 33.07:
        return fx.ease_out((t - 31.0) / 0.35)
    return 0.0


def render_frame(n):
    t = n / FPS
    idx, s, t1 = shot_at(t)
    imp = impulses(t, s, s["t0"])
    frame = render_shot(t, idx, s, t1, imp)

    if imp["shock"] is not None:
        frame = fx.shockwave(frame, imp["shock"][0], imp["shock"][1])
    frame = fx.zoom_blur(frame, imp["zblur"])
    frame = fx.chroma(frame, imp["rgb"])
    ph = phase(t)
    frame = fx.bloom(frame, amt={"intro": 0.45, "dominant": 0.55, "calm": 0.35, "cosmic": 0.75}[ph])

    # flashes
    frame = frame * (1 - min(0.9, imp["white"])) + min(0.9, imp["white"])
    if imp["red"] > 0:
        frame = frame + np.array([0.05, 0.02, 0.55], np.float32) * imp["red"]
    if imp["violet"] > 0:
        a = min(0.85, imp["violet"])
        frame = frame * (1 - a * 0.6) + np.array([1.0, 0.45, 0.85], np.float32) * a * 0.6

    frame = frame * fx.VIGNETTE
    frame = fx.grain(frame, t, 0.04)
    frame = np.clip(frame, 0, 1)
    if imp["invert"]:
        inv = 1 - frame
        frame = np.clip(inv * np.array([0.85, 0.9, 1.0], np.float32), 0, 1)

    lb = letterbox_amt(t)
    if lb > 0:
        bh = int(250 * lb)
        frame[:bh] = 0
        frame[H - bh:] = 0

    # outro dive: last shot's pupil goes black, then crossfade into frame 0 for a seamless loop
    if t >= 44.55:
        k = fx.ease_in((t - 44.55) / 0.30)
        frame = frame * (1 - min(1.0, k))
    if t >= 44.80:
        w = fx.ease_in_out((t - 44.80) / (tl.DUR - 44.80))
        frame = frame * (1 - w) + render_frame_zero() * w
    return (frame * 255 + 0.5).astype(np.uint8)


_f0 = None


def render_frame_zero():
    global _f0
    if _f0 is None:
        _f0 = render_frame(0).astype(np.float32) / 255.0
    return _f0


def worker(args):
    a, b, path, draft = args
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if draft else "slow",
           "-crf", "22" if draft else "12", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(a, b):
        p.stdin.write(render_frame(n).tobytes())
    p.stdin.close()
    p.wait()
    return path


def main():
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1]
    if mode == "preview":
        os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
        for ts in sys.argv[2:]:
            n = int(round(float(ts) * FPS))
            cv2.imwrite(os.path.join(OUT, "preview", f"f_{float(ts):06.2f}.jpg"), render_frame(n), [cv2.IMWRITE_JPEG_QUALITY, 85])
        return
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    draft = "--draft" in sys.argv
    segdir = os.path.join(OUT, "segments")
    os.makedirs(segdir, exist_ok=True)
    N = tl.NFRAMES
    chunks = 16
    bounds = [round(i * N / chunks) for i in range(chunks + 1)]
    jobs = [(bounds[i], bounds[i + 1], os.path.join(segdir, f"seg_{i:02d}.mp4"), draft) for i in range(chunks)]
    with Pool(workers) as pool:
        paths = pool.map(worker, jobs)
    lst = os.path.join(segdir, "list.txt")
    with open(lst, "w") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    silent = os.path.join(segdir, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    final = os.path.join(OUT, "cat_aura_farming_draft.mp4" if draft else "cat_aura_farming.mp4")
    dur = f"{tl.DUR:.4f}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", AUDIO, "-map", "0:v", "-map", "1:a",
                    "-t", dur, "-c:v", "copy", "-af", f"afade=t=out:st={tl.DUR - 0.03:.4f}:d=0.03",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", final], check=True)
    print(final)


if __name__ == "__main__":
    main()
