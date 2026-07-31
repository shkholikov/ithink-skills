# ithink-skills

Skills for [Claude](https://claude.ai) — each top-level folder is one skill, ready
to drop into `~/.claude/skills/` or upload to claude.ai.

## Skills

| Skill | What it does |
|---|---|
| [**topology-creator**](topology-creator) | Turns a described network into an editable **draw.io** diagram — Cisco icons, zone boxes, interface labels on both ends of every link, colour-coded VLANs, obstacle-avoiding link routing, and a generated legend page. |

![topology-creator output](topology-creator/examples/small-office.png)

## Install

### Claude Code

```bash
git clone https://github.com/shkholikov/ithink-skills
cp -R ithink-skills/topology-creator ~/.claude/skills/
```

Restart Claude Code. Each skill folder is self-contained — copy only the ones you
want.

### Claude Desktop / web / mobile

Download a skill's `.zip` from
[Releases](https://github.com/shkholikov/ithink-skills/releases) and upload it at
**Settings → Capabilities → Skills**.

Or build one yourself from a clone:

```bash
cd ithink-skills && zip -r topology-creator-skill.zip topology-creator
```

## Design rules

Every skill here follows the same constraints, so they all behave the same way
wherever Claude runs them:

- **Stdlib only.** No `pip install`. Skills must run unchanged inside Claude's
  sandbox on Desktop and mobile, where nothing can be installed.
- **Self-contained folder.** Assets live with the skill and are embedded into
  output, so generated files have no missing dependencies.
- **Tested.** Each skill ships a test suite runnable with plain `python3`.
- **Fails loudly on bad input, never on cosmetics.** A wrong device id is a hard
  error; an unrecognised icon degrades to a placeholder and a warning.

## Licence

Code is MIT licensed — see [LICENSE](LICENSE).

Bundled third-party assets are **not** covered by it. `topology-creator` ships
icons derived from the **Cisco Network Topology Icon** library, which remain the
property of Cisco Systems, Inc.; see
[topology-creator/README.md](topology-creator/README.md#licence-and-attribution).
