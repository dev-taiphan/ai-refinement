# ai-factory: Claude Code plugins

A Claude Code marketplace with two plugins.

| Plugin | Commands | What it does |
|---|---|---|
| [`kaiz`](plugins/kaiz) | `/kaiz:analyze` | Analyses a local ticket (`.issues/<n>/ticket.md`) against your codebase and writes a cited set of design documents. Markdown only, no scripts. |
| [`kaiz-factory`](plugins/kaiz-factory) | `/kaiz-factory:init`, `/kaiz-factory:factory` | Builds GitHub issues labeled `factory` into pull requests with a pipeline of Claude subagents. Needs `gh` and Python. |

**Hướng dẫn tiếng Việt đầy đủ (cài đặt và sử dụng): [HUONG-DAN.md](HUONG-DAN.md).**

Works in the Claude Code terminal, the VS Code extension and local sessions of
the Claude Code desktop app. Not in cloud or WSL sessions.

## Install

```
/plugin marketplace add <owner>/<repo>        # or ./path/to/ai-factory-plugin
/plugin install kaiz@ai-factory
/plugin install kaiz-factory@ai-factory
```

Install only the plugin you need. To try one for a session without installing:
`claude --plugin-dir ./plugins/kaiz`.

## Layout

```
.claude-plugin/marketplace.json   lists both plugins
plugins/kaiz/           ticket analysis: agents/, skills/analyze/
plugins/kaiz-factory/   pipeline: agents/, skills/factory/, skills/init/, templates/factory/
```

Each plugin folder is self-contained, with its own manifest, icon, README and
LICENSE, so either can be submitted to a plugin directory on its own. `kaiz` holds
only Markdown, JSON and an image, which is what the Anthropic directory accepts
from organizations that aren't verified; `kaiz-factory` ships scripts and so
can't be listed there.

## License

GPL-3.0-only, see `LICENSE`.
