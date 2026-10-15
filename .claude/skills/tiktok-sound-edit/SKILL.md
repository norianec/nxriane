---
name: tiktok-sound-edit
description: >
  Orchestrator for turning one of the artist's original sounds into vertical TikTok/Reels/Shorts
  edits built to push the sound (beat-synced edits, lyric/kinetic-type videos, visualizers, teaser
  hooks). Use when the user gives a track (mp3/wav/video) and wants short-form edits, a release
  campaign, or several variants to A/B test. Routes to music-to-video / hyperframes / remotion /
  motion-graphics / brand skills.
---

# TikTok sound edit — orchestrator

Goal: get people to **use the sound**, not just watch the video. Every decision serves that.

## 0. Token discipline
Long sessions: run `/caveman` (lite or full) for terse replies. Use `/caveman-compress` on
big brief/memory files. Never compress code, lyrics, or timestamps.

## 1. Brand kit first (once per artist)
Create/read `brand/BRAND.md` at repo root: artist name, handle, 2–3 hex colors, 1 display font
+ 1 text font, logo/wordmark path, mood words, banned looks. If missing, build it with
`brand-guidelines` + `theme-factory` and ask max 3 questions. All edits reuse this kit so the
feed is recognisable in 1 frame (personal branding = repetition).

## 2. Analyse the track
- Find BPM, downbeats, drop, and the **best 7–15 s section** (usually hook/drop). `music-to-video`
  and `hyperframes-audio` cover beat grids.
- Export 3 candidate cut points: hook, pre-drop→drop, outro-loop.

## 3. Pick formats (make ≥3 variants per sound)
| Format | Skill | When |
|---|---|---|
| Beat-synced edit (user clips/photos cut on beats) | `music-to-video` | have footage |
| Lyric / kinetic typography | `music-to-video` + `motion-graphics` | vocals with a quotable line |
| Visualizer / loop | `hyperframes-animation` or `remotion-create` | instrumental |
| Captioned performance / talking clip | `embedded-captions` or `remotion-captions` | artist on camera |
| Teaser "POV / wait for the drop" text overlay | `motion-graphics` | pre-release |

Default engine: **HyperFrames** (HTML→MP4, agent-native). Use **Remotion** when React is
preferred or programmatic batch renders are needed (`remotion-render`).

## 4. Short-form rules (hard constraints)
- 1080×1920, 30 fps (60 for fast motion), H.264, -14 LUFS-ish loudness, file < 287 MB.
- Safe zones: keep text out of top ~150 px, bottom ~420 px, right ~140 px (TikTok UI).
- Hook in the **first 0.5–1 s**: motion or text on frame 1, no fade-in from black.
- Cut on beats/downbeats; hard visual change on the drop.
- Loopable: last frame flows into first; total 7–20 s for pure sound promos.
- On-screen text ≤ 7 words per beat, high contrast, brand fonts.
- One clear call to action in caption, e.g. "use this sound for your ___".

## 5. Deliver
Per sound, output to `out/<sound-slug>/`: `v1-hook.mp4`, `v2-lyric.mp4`, `v3-visualizer.mp4`,
plus `captions.md` (3 caption options, 3–5 niche hashtags, suggested posting order).
Render, then inspect a few frames (first frame, drop frame, last frame) before calling it done.

## 6. Iterate
Post variants over several days; keep the format that gets the most **sound uses/saves**,
and remake it for the next sound. Note results in `brand/RESULTS.md`.
