"""Storyboard for CAT AURA FARMING, synced to PURR OF DEATH (first 45 s).

Times come from analysis/ (spectrogram reading of the meow glides + low-band onsets).
Phases: mysterious (0-8.1) -> charismatic (8.1-16.5) -> dominant (16.5-31) ->
calm-before (31-33) -> cosmic aura (33-45) -> loops into frame 0.
"""

FPS = 30
NFRAMES = 1351            # 45.033 s: next bass hit lands exactly on the loop restart
DUR = NFRAMES / FPS

# normalised eye positions per still (x, y) for glows / flares
EYES = {
    "00_hero": [(0.333, 0.313), (0.558, 0.281)],
    "01_eyes_dark": [(0.347, 0.293), (0.611, 0.277)],
    "02_eye_macro": [(0.503, 0.488)],
    "03_rooftop_moon": [(0.486, 0.502), (0.538, 0.502)],
    "04_walk_smoke": [(0.295, 0.303), (0.479, 0.299)],
    "05_profile_wind": [(0.712, 0.449)],
    "06_meow_front": [(0.337, 0.463), (0.670, 0.467)],
    "07_meow_side": [(0.451, 0.332)],
    "08_throne": [(0.462, 0.254), (0.535, 0.254)],
    "09_lightning": [(0.358, 0.367), (0.583, 0.359)],
    "10_stare": [(0.292, 0.449), (0.694, 0.441)],
    "11_cosmic_rock": [(0.462, 0.256), (0.576, 0.250)],
    "12_cosmic_aura": [(0.361, 0.434), (0.646, 0.438)],
    "13_cosmic_god": [(0.406, 0.314), (0.5625, 0.3125)],
    "14_eyes_closed": [],
}

# meow glide onsets (s) and their shape
MEOWS = [
    (0.02, "down"), (1.60, "arch"), (2.60, "down"), (3.70, "arch"), (5.85, "arch"), (7.25, "down"),
    (10.15, "arch"), (12.05, "arch"), (14.30, "arch"), (16.25, "arch"),
    (17.90, "down"), (20.25, "arch"), (22.00, "down"), (24.35, "arch"), (26.15, "down"),
    (28.45, "arch"), (30.25, "down"), (31.10, "down"), (32.00, "down"),
    (33.95, "up"), (35.00, "up"), (36.95, "up"), (37.35, "down"), (38.05, "up"), (39.10, "up"),
    (40.40, "down"), (40.95, "down"), (41.45, "down"), (42.15, "up"), (43.15, "up"),
]

# 808 / kick hits from the drop on (s)
BASS = [
    16.54, 17.39, 18.61, 19.41, 20.04, 20.76, 21.60, 22.88, 23.65, 24.06, 24.94, 25.72,
    27.01, 27.78, 28.29, 29.07, 29.81,
    33.07, 33.72, 34.24, 35.26, 35.78, 36.29, 36.82, 37.33, 37.84, 38.35, 38.87, 39.38,
    39.90, 40.41, 40.94, 41.45, 41.96, 42.48, 42.99, 43.50, 44.01, 44.54,
]


def S(t0, img, grade="blood", z=(1.0, 1.1), c0=(0.5, 0.45), c1=None, rot=(0, 0), ease="inout",
      fx=(), mirror=False, dark=None, eye=0.25, mix=0.55):
    return dict(t0=t0, img=img, grade=grade, z=z, c0=c0, c1=c1 or c0, rot=rot, ease=ease,
                fx=set(fx), mirror=mirror, dark=dark, eye=eye, mix=mix)


SHOTS = [
    # ---------------- I. MYSTERIOUS: darkness, only the eyes
    S(0.00, "01_eyes_dark", z=(1.18, 1.26), c0=(0.48, 0.30), fx=("dust",), dark=(0.94, 0.78), eye=1.6),
    S(1.60, "03_rooftop_moon", z=(1.0, 1.18), c0=(0.5, 0.42), c1=(0.5, 0.48), fx=("rain",), eye=0.6),
    S(3.70, "05_profile_wind", z=(1.12, 1.22), c0=(0.42, 0.42), c1=(0.52, 0.42), fx=("embers",), eye=0.5),
    S(5.85, "02_eye_macro", z=(1.0, 1.45), c0=(0.5, 0.48), fx=("heat",), eye=0.0, mix=0.45),
    # ---------------- II. CHARISMATIC: slow-motion presence
    S(8.10, "04_walk_smoke", z=(1.0, 1.22), c0=(0.45, 0.42), c1=(0.42, 0.32), fx=("embers", "dust"), eye=0.35),
    S(10.15, "10_stare", z=(1.0, 1.12), c0=(0.5, 0.46), fx=("heat",), eye=0.35),
    S(12.05, "00_hero", z=(1.25, 1.12), c0=(0.48, 0.80), c1=(0.46, 0.33), fx=("dust",), eye=0.35),
    S(14.30, "08_throne", z=(1.0, 1.25), c0=(0.5, 0.45), c1=(0.5, 0.30), fx=("dust",), eye=0.5),
    S(15.30, "02_eye_macro", z=(1.0, 3.2), c0=(0.5, 0.49), ease="in", fx=("heat",), eye=0.0, mix=0.45),
    S(16.25, "06_meow_front", z=(1.45, 1.15), c0=(0.5, 0.48), ease="out", fx=("speed",), eye=0.6),
    # ---------------- III. DOMINANT: the drop, cuts on the 808
    S(16.54, "09_lightning", z=(1.08, 1.0), c0=(0.5, 0.45), fx=("embers", "lightning_bg"), eye=0.6),
    S(17.90, "07_meow_side", z=(1.1, 1.22), c0=(0.6, 0.38), fx=("speed", "embers"), eye=0.9),
    S(18.61, "10_stare", z=(1.2, 1.3), c0=(0.5, 0.45), fx=("heat",), eye=0.5),
    S(19.41, "04_walk_smoke", z=(1.1, 1.2), c0=(0.42, 0.38), fx=("embers",), eye=0.5),
    S(20.25, "03_rooftop_moon", z=(1.6, 2.2), c0=(0.51, 0.50), fx=("rain", "lightning_bg"), eye=0.9),
    S(20.76, "08_throne", z=(1.15, 1.35), c0=(0.5, 0.28), fx=("dust",), eye=0.7),
    S(22.00, "06_meow_front", z=(1.3, 1.2), c0=(0.5, 0.48), mirror=True, fx=("speed",), eye=0.7),
    S(22.88, "05_profile_wind", z=(1.2, 1.3), c0=(0.55, 0.44), fx=("embers",), eye=0.8),
    S(23.65, "09_lightning", z=(1.1, 1.2), c0=(0.5, 0.42), mirror=True, fx=("lightning_bg", "embers"), eye=0.7),
    S(24.35, "10_stare", z=(1.35, 1.5), c0=(0.5, 0.45), fx=("heat",), eye=1.0),
    S(24.94, "00_hero", z=(1.05, 1.15), c0=(0.45, 0.40), fx=("lightning_bg", "dust"), eye=0.6),
    S(26.15, "07_meow_side", z=(1.3, 1.15), c0=(0.62, 0.40), mirror=True, fx=("speed",), eye=0.9),
    S(27.01, "04_walk_smoke", z=(1.25, 1.4), c0=(0.40, 0.30), mirror=True, fx=("embers",), eye=0.6),
    S(27.78, "08_throne", z=(1.6, 1.8), c0=(0.5, 0.25), fx=("dust",), eye=0.9),
    S(28.45, "07_meow_side", z=(1.55, 1.75), c0=(0.68, 0.42), fx=("lightning_bg", "speed"), eye=0.8),
    S(29.07, "09_lightning", z=(1.3, 1.45), c0=(0.48, 0.38), fx=("lightning_bg", "embers"), eye=0.9),
    S(29.81, "10_stare", z=(1.0, 1.08), c0=(0.5, 0.45), fx=("heat",), eye=0.7),
    S(30.25, "06_meow_front", z=(1.2, 1.5), c0=(0.5, 0.47), fx=("speed",), eye=1.0),
    # ---------------- calm before the storm: letterbox, eyes closed
    S(31.00, "14_eyes_closed", grade="void", z=(1.05, 1.22), c0=(0.5, 0.4), fx=("dust", "letterbox"), eye=0.0),
    # ---------------- IV. COSMIC AURA
    S(33.07, "12_cosmic_aura", grade="cosmic", z=(1.0, 1.12), c0=(0.5, 0.45), fx=("warp",), eye=1.0),
    S(33.95, "11_cosmic_rock", grade="cosmic", z=(1.5, 1.0), c0=(0.5, 0.35), ease="out", fx=("warp",), eye=0.8),
    S(35.00, "06_meow_front", grade="cosmic", z=(1.2, 1.3), c0=(0.5, 0.48), fx=("speed", "warp"), eye=1.0),
    S(35.26, "13_cosmic_god", grade="cosmic", z=(1.0, 1.15), c0=(0.5, 0.35), fx=("warp",), eye=0.9),
    S(36.29, "01_eyes_dark", grade="cosmic", z=(1.0, 1.12), c0=(0.5, 0.35), fx=("warp",), eye=0.9),
    S(36.95, "10_stare", grade="cosmic", z=(1.2, 1.4), c0=(0.5, 0.45), fx=("heat",), eye=1.3),
    S(37.33, "02_eye_macro", grade="cosmic", z=(1.4, 2.0), c0=(0.5, 0.49), fx=("warp",), eye=0.0, mix=0.6),
    S(37.84, "12_cosmic_aura", grade="cosmic", z=(1.2, 1.3), c0=(0.5, 0.42), mirror=True, fx=("warp",), eye=1.0),
    S(38.05, "07_meow_side", grade="cosmic", z=(1.05, 1.2), c0=(0.6, 0.38), fx=("speed", "warp"), eye=1.2),
    S(38.35, "11_cosmic_rock", grade="cosmic", z=(1.6, 1.8), c0=(0.52, 0.28), fx=("warp",), eye=1.0),
    S(38.87, "13_cosmic_god", grade="cosmic", z=(1.4, 1.6), c0=(0.48, 0.30), fx=("warp",), eye=1.2),
    S(39.10, "10_stare", grade="cosmic", z=(1.3, 1.2), c0=(0.5, 0.45), mirror=True, fx=("speed",), eye=1.3),
    S(39.38, "00_hero", grade="cosmic", z=(1.05, 1.15), c0=(0.45, 0.4), fx=("warp",), eye=1.0),
    S(39.90, "12_cosmic_aura", grade="cosmic", z=(1.5, 1.7), c0=(0.5, 0.43), fx=("warp",), eye=1.3),
    S(40.40, "06_meow_front", grade="cosmic", z=(1.25, 1.1), c0=(0.5, 0.48), mirror=True, fx=("speed", "lightning_bg"), eye=1.2),
    S(40.94, "09_lightning", grade="cosmic", z=(1.15, 1.3), c0=(0.5, 0.4), fx=("lightning_bg", "warp"), eye=1.2),
    S(41.45, "03_rooftop_moon", grade="cosmic", z=(1.0, 1.25), c0=(0.5, 0.35), fx=("warp",), eye=1.2),
    S(41.96, "13_cosmic_god", grade="cosmic", z=(1.1, 1.25), c0=(0.5, 0.33), fx=("warp",), eye=1.3),
    S(42.15, "12_cosmic_aura", grade="cosmic", z=(1.8, 2.1), c0=(0.5, 0.43), fx=("warp", "speed"), eye=1.5),
    S(42.99, "11_cosmic_rock", grade="cosmic", z=(1.2, 1.35), c0=(0.5, 0.3), fx=("warp",), eye=1.2),
    S(43.15, "07_meow_side", grade="cosmic", z=(1.4, 1.2), c0=(0.62, 0.40), mirror=True, fx=("speed", "warp"), eye=1.5),
    S(43.50, "13_cosmic_god", grade="cosmic", z=(1.2, 1.9), c0=(0.47, 0.32), ease="in", fx=("warp",), eye=1.6),
    # ---------------- outro: dive into the pupil -> black -> frame 0 (loop)
    S(44.01, "02_eye_macro", grade="cosmic", z=(1.0, 9.0), c0=(0.5, 0.50), ease="in", fx=("warp",), eye=0.0, mix=0.6),
]

# extra one-off events: (time, kind, strength)
EVENTS = [
    (16.54, "shockwave", 1.0), (16.54, "flash_white", 1.0), (16.54, "lightning", 1.0),
    (33.07, "shockwave", 1.3), (33.07, "flash_violet", 1.0), (33.07, "lightning", 0.8),
    (20.25, "lightning", 0.8), (24.94, "lightning", 0.7), (28.45, "lightning", 0.8), (29.07, "lightning", 0.6),
    (23.65, "lightning", 0.6), (40.40, "lightning", 0.8), (40.94, "lightning", 0.8),
    # negative flashes on hard meows (phonk staple)
    (22.00, "invert", 1.0), (30.25, "invert", 1.0), (35.00, "invert", 1.0), (39.10, "invert", 1.0),
    (43.15, "invert", 1.0),
    # riser shakes into the drops
    (15.30, "riser", 1.0), (32.20, "riser", 0.8),
]
