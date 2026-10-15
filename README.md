# nxriane — TikTok sound edit toolkit (Claude Code skills)

Skills in `.claude/skills/` load automatically in Claude Code when you open this repo.
Entry point: **`/tiktok-sound-edit`**. Give it your track and it routes to the rest.

| Group | Skills | Source (commit) | License |
|---|---|---|---|
| Orchestrator | `tiktok-sound-edit` | written for this repo | — |
| HyperFrames (HTML→video, beat sync, captions, motion design) | `music-to-video`, `motion-graphics`, `embedded-captions`, `hyperframes*`, `general-video`, `slideshow`, `media-use`, `talking-head-recut`, `remotion-to-hyperframes`, … | heygen-com/hyperframes @0e9f380 | Apache-2.0 (`licenses/`) |
| Remotion (React video) | `remotion-create`, `-best-practices`, `-captions`, `-multimedia`, `-render`, `-studio`, `-markup`, `-docs` | remotion-dev/skills @7ba4dcf | see repo; Remotion itself needs a company license for teams > 3 |
| Tokens | `caveman`, `caveman-compress`, `caveman-stats` | JuliusBrussee/caveman @d262ab3 | MIT (`licenses/`) |
| Branding / design | `brand-guidelines`, `theme-factory`, `canvas-design`, `frontend-design`, `algorithmic-art`, `skill-creator` | anthropics/skills @dbd4588 | per-skill `LICENSE.txt` |

Requirements: Node 22+, FFmpeg, Chromium (HyperFrames & Remotion render headless).

Update: re-clone the source repos and copy the skill folders over.
