# ITHINK company details

The facts that identify ITHINK on a document. Copy them verbatim — these are
legal and contact details, not copy to be reworded, shortened or translated.

Anything marked **not supplied** is genuinely unknown. Ask for it rather than
inventing a plausible value; a wrong bank account or tax number on a sent
document is the most expensive kind of mistake this skill can make.

## Legal and contact

| Field | Value |
|---|---|
| Legal name | ООО «ITHINK TECH» |
| Short name in copy | ITHINK |
| Phone | +998 (95) 171-71-01 |
| Email | info@ithink.uz |
| Website | www.ithink.uz |
| Legal address | *not supplied* |

In Uzbek-language documents the legal form is written **MChJ**, so
ООО «ITHINK TECH» becomes «ITHINK TECH» MChJ. The brand name itself stays in
Latin capitals in both languages — never transliterate it to «Айтинк».

Write the phone exactly as above, including the brackets. Email and website
are lowercase and never carry `https://`.

## Payment requisites

An invoice (счёт на оплату / hisob-faktura) cannot be paid without these, and
none of them are on file yet:

| Field | Value |
|---|---|
| ИНН | *not supplied* |
| Банк | *not supplied* |
| Расчётный счёт | *not supplied* |
| МФО | *not supplied* |
| ОКЭД | *not supplied* |
| VAT status (плательщик НДС) | *not supplied* |

Until these are supplied, keep them in the document as `@@REQ_INN@@`,
`@@REQ_BANK@@`, `@@REQ_ACCOUNT@@`, `@@REQ_MFO@@`. The build script fails on an
unresolved `@@…@@` placeholder, which is the point: an invoice with a blank
расчётный счёт cannot be built by accident. Never substitute a dash, a blank
line or a specimen number to get a build through.

The VAT line matters even when the answer is no. If ITHINK is not a VAT payer,
say so explicitly on the invoice (`Без НДС`) — silence reads as an omission to
the client's accountant and the document comes back.

## Signatory

| Field | Value |
|---|---|
| Name | *not supplied* |
| Position | *not supplied* |

## Where these belong in a document

- **Invoice** — issuer block top right: legal name, phone, email, website. The
  payment requisites go in their own section next to the total, where the payer
  looks, not in the header.
- **Commercial offer, presentation, one-pager** — footer contacts only: phone,
  email, website. An offer is not a payment document; requisites on one make it
  look like a bill before the client has agreed to anything.
- **Every document** — the short name ITHINK in body copy, the legal name only
  where the document has legal force.
