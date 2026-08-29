# Icons

98 icons from [Lucide](https://lucide.dev), ISC licensed — see
`assets/LICENSE-lucide`. They are stored as one minified map in
`assets/icons.json` (19 KB) rather than 98 files, and drawn as line art tinted
to the node's tone.

Reference one by name:

```json
{"id": "store", "label": "Postgres", "icon": "database", "tone": "blue"}
```

An unknown name stops the build and prints the available set. Nothing renders
as a blank box.

## Available

**Flow and process** — `workflow`, `git-branch`, `route`, `split`, `merge`, `repeat`, `refresh-cw`, `arrow-right-left`, `send`, `zap`, `play`, `timer`, `hourglass`
**Data and storage** — `database`, `hard-drive`, `folder`, `file-text`, `files`, `layers`, `boxes`, `box`, `package`, `container`, `table`
**Compute and network** — `server`, `cpu`, `cloud`, `network`, `router`, `wifi`, `globe`, `webhook`, `terminal`, `code`, `plug`, `link`, `share-2`
**People and identity** — `user`, `users`, `fingerprint`, `scan`, `key`, `lock`, `lock-keyhole`, `shield`, `shield-check`
**Checks and outcomes** — `check`, `check-check`, `x`, `list-checks`, `clipboard-check`, `file-check`, `scale`, `flag`, `star`
**Watching** — `activity`, `eye`, `gauge`, `search`, `filter`, `bug`, `triangle-alert`, `info`, `circle-help`, `trending-up`, `chart-column`, `chart-pie`
**Interface and comms** — `monitor`, `smartphone`, `printer`, `image`, `mail`, `message-square`, `bell`, `calendar`, `map-pin`, `qr-code`
**Money** — `credit-card`, `shopping-cart`, `receipt`, `banknote`, `wallet`
**Intelligence** — `brain`, `bot`, `sparkles`, `flask-conical`
**Misc** — `target`, `crosshair`, `clock`, `history`, `settings`, `sliders-horizontal`, `wrench`, `building`, `book-open`, `square-stack`
**Ungrouped** — `download`, `upload`

## Adding one

Lucide has about 1500 icons; these are the ones a system diagram reaches for.
To add another, fetch it and re-pack:

```bash
curl -o /tmp/new.svg https://cdn.jsdelivr.net/npm/lucide-static@1.37.0/icons/NAME.svg
```

Then append its inner markup to `assets/icons.json` under that name, keeping
the file minified and sorted. Icons must stay stroke-based with no `fill`, so
that tinting works — a filled icon ignores the tone and prints as a black blob.
