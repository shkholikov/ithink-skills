# Palette

`ithink-documents/references/brand.md` allows six colours and says nothing
outside them belongs in a document. A diagram is the one case that genuinely
needs more: its whole job is to make five or six stages distinguishable at a
glance, and five tints of one blue are not distinguishable.

So this skill extends the brand rather than ignoring it, under two rules:

1. **Structure stays brand.** Navy for headings, badges and the zone tab. Blue
   for the zone frame. Body text is ink. Ground is paper. The header carries
   the logo itself. None of that changes.
2. **Stage tints are pale.** Every tone is a near-white fill with a saturated
   border. On paper they read as one family; nothing competes with the navy
   badges or the blue accents.

## Tones

| Tone | Fill | Border | For |
|---|---|---|---|
| `blue` | `#eef4ff` | `#377dff` | The brand tone. Input, context, the first real stage |
| `violet` | `#f2eeff` | `#7c5cff` | Models, inference, anything probabilistic |
| `amber` | `#fff7e8` | `#d99a2b` | Decisions, gates, constraints — a place where flow can stop |
| `rust` | `#fff0ea` | `#d1603d` | Execution and verification: side effects on the real world |
| `green` | `#eaf7f0` | `#2e7d5b` | Accepted, done, the success path |
| `slate` | `#f4f6fa` | 24% navy | Sidecars that observe rather than act |
| `neutral` | `#ffffff` | 20% navy | Things outside the system — a user, an external caller |

`green` and `rust` are the two semantic colours `brand.md` already allows
(`#2e7d5b`, `#b0472f`); rust is lightened to `#d1603d` so a whole node border
in it does not shout. `violet` is the only genuinely new hue, and it exists
because the model deserves to be visually distinct from everything the system
controls.

## Using them

Tone carries meaning. Do not colour a diagram to look varied — a reader who
sees amber twice will look for what those two stages have in common, and being
wrong about that is worse than a monochrome diagram.

Keep to one `green`, and put it at the end. A diagram with three green nodes
has no ending.

Edges default to navy. Give an edge a colour only when it means something: the
green accepted path in `examples/harness.json` earns it, the six arrows above
it do not.
