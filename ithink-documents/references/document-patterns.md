# Document patterns

Four document types. Each has a job, a reader, and a structure that has
already survived contact with clients. Deviate when a specific deal calls for
it, but start here.

---

## 1. Commercial offer (Коммерческое предложение / Kommersiya taklifi)

**Reader:** the owner or the person who signs. Often not technical.
**Job:** make the price feel like a consequence of scope rather than a number
that appeared from nowhere.

```
Cover              client name, document type, date, validity, ITHINK logo
Problem            2–4 sentences in the client's own words, from their briefing
What we build      modules as a table: module · what it does · what it replaces
Scope boundary     what is explicitly NOT included — this prevents the
                   argument that happens in month two
Price              per module, then total. One row highlighted if there is a
                   recommended package
Timeline           phases with weeks, not dates. Dates age; weeks do not
Terms              payment schedule, warranty period, what support costs after
Why ITHINK         3–4 lines maximum, at the end. Never at the start
Contacts           name, phone, Telegram, email
```

The price table is the page they photograph and send to a partner, so it has
to survive being read alone: every row self-explanatory, no abbreviations
defined elsewhere in the document.

State validity explicitly ("valid until X"), and put a phase breakdown next to
any total above roughly 50 million soʻm — a large number without structure
invites a haggle, the same number as four phases invites a conversation about
scope.

---

## 2. Product presentation (Taqdimot)

**Reader:** a room, sometimes on a projector, sometimes forwarded as a PDF.
**Job:** make the product concrete before anyone asks the price.

```
Cover              product name, one-line promise
The problem        one screen, in numbers the client recognises
The product        what it is, in one sentence a non-technical reader repeats
Screens            actual UI, 4–8 of them, each with one caption explaining
                   the moment — not a feature list
How it works       one diagram, no more
Results            what changes for the business, quantified where honest
Next step          what happens if they say yes today
```

Built as a scrolling document rather than slides. It reads well on a phone,
survives being forwarded, and prints to PDF without a slide tool. One idea per
section, and the caption under a screenshot carries the argument — nobody reads
a bulleted feature list under an image.

---

## 3. Technical proposal

**Reader:** the client's IT person, whose job in the meeting is to find the
flaw. Being unimpressed is how they demonstrate value.
**Job:** answer the objection before it is raised.

```
Cover
Architecture       one diagram; components, data flow, trust boundaries
Stack              table: layer · choice · why this and not the obvious alternative
Integrations       what connects to what, with the protocol and the direction
Data               what is stored, where it lives, who can reach it, retention
Security           auth, transport, secrets, backups, and what happens on breach
Deployment         environments, CI, rollback, monitoring
Timeline           phases with deliverables, and what blocks each phase
Team               roles and time allocation
Assumptions        what must be true for the estimate to hold
```

The "why this and not the alternative" column is the whole document. A stack
table without it reads as a list of preferences; with it, it reads as
engineering judgement.

The Assumptions section is what protects the timeline later. Write it as if
it will be quoted back.

---

## 4. One-pager / capability sheet

**Reader:** someone who met ITHINK once and needs to explain it to a colleague.
**Job:** be forwardable.

```
Header             logo, one-line positioning
What we do         3–4 service areas, one line each
Selected work      3 projects: client, what was built, one outcome
How we work        4 short lines — process, not philosophy
Contacts
```

Strictly one page. It exists to be attached to an email, so if it does not fit,
cut a project rather than shrinking the type.

---

## Rules that apply to all four

**Tables over paragraphs** for anything comparable — scope, price, stack,
timeline. A client scans a table and reads a paragraph only if forced.

**Every page carries the client's name.** Documents get printed, separated and
passed around; a loose page with no context gets thrown away.

**Never open with ITHINK.** Open with the client's problem. Credentials go at
the end, after the reader already wants the thing.

**Numbers need a source or they need cutting.** This is the one failure that
does lasting damage.

**Ask the language before writing** — Russian and Uzbek are both normal here,
and it depends on the client, not on the document type.
