# Skills

Agent skills kept with this repository. Nothing in this folder is part of the website:
the deploy workflow leaves `skill/` out of what it publishes.

## unslop

`unslop/` is a copy of the **unslop** skill by Damir Sokolovsky ([@heydamir](https://x.com/heydamir)),
which audits AI-looking UI and fixes it pass by pass.

- Source: https://github.com/heydamir/unslop (folder `skills/unslop`)
- Copied at commit `620163eedb3529d9cd23a3994ed8d287d06f760d` (15 November 2026), unmodified
- Licence: CC BY 4.0, see `unslop/LICENSE`. Keep this credit and the link if the folder is shared.

Start with `unslop/SKILL.md`. To use it in Claude Code, copy `unslop/` into `.claude/skills/`
(or install the plugin from the source repository); for Codex, copy it into `.agents/skills/`.
The snapshot and story-video scripts need Playwright, and the video also needs ffmpeg.
