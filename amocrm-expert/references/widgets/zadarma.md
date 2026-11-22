# Zadarma in amoCRM

Zadarma is a cloud PBX (free PBX, virtual numbers in many countries) with an official, free integration that logs calls and recordings into amoCRM cards, creates contacts/deals/tasks from calls, shows an incoming-call notification with the contact, routes known callers to their responsible manager, and offers a WebRTC web phone in the bottom-left corner of amoCRM. The integration is switched on from the Zadarma personal account **https://my.zadarma.com/** («Настройки» → «Интеграции и API»), authorised in amoCRM, and then configured in the widget settings (extension per user, WebRTC, default responsible, creation rules); extra routing options sit back in Zadarma. **Caveat:** Zadarma's current official instruction (URL `crm-amo`) names only **Kommo** (the international amoCRM); that the same flow and labels apply to a Russian-domain account `*.amocrm.ru` is (unverified) — check that a Zadarma widget appears in the client's «amoМаркет» → «Телефония» before promising anything.

## Setup

### In the vendor dashboard (my.zadarma.com)
1. PBX ready: extensions (1 to 50, one per employee) in «Моя АТС» → «Внутренние номера»; each extension has a device (softphone / IP phone) or forwarding. (change)
2. Recording if needed: in the extension settings «Запись разговоров в облако» (Zadarma FAQ says recording is on by default on PBX extensions). (change)
3. Default incoming scenario «без нажатия» in «Моя АТС» → «Входящие звонки и голосовое меню». (change)
4. «Настройки» → «Интеграции и API» → block «Интеграции» → «Все интеграции» → Kommo/amoCRM tile → «Включить». (change)
5. Stay logged in to my.zadarma.com **in the same browser** where amoCRM is open — the integration requires it.
6. After the widget is installed: «Настройки» → «Интеграции и API» → the CRM block → make this account the main one and set options: (change)
   - «Добавлять виртуальный номер в тег» — tag with the dialled virtual number.
   - «Направление звонков на ответственного» — known callers bypass the voice menu and ring the responsible user's extension.
   - «Возвращение звонка в АТС, если ответственный не доступен» — back to the voice menu after 15 s without answer.
   - «Отображение имени клиента на IP-телефоне» — overrides «Имя номера» from «Настройки» → «Виртуальные номера».
   - «Входящие SMS в интеграции» — SMS from a saved number appears in the card feed.
   - Pipeline for new leads (default or custom).
   - With call tracking: fields Source url, Source, Source type.

### In amoCRM
A1. In the window that opens after «Включить»: choose the account → «Разрешить». (change)
A2. Widget settings: give each amoCRM user a three-digit Zadarma extension. (change)
A3. «Использовать WebRTC» — needed for calls in the browser. (change)
A4. Default responsible user — receives missed calls from new clients. (change)
A5. Block of call / contact / task / deal settings for incoming, outgoing and missed calls (official page shows these only on a screenshot; exact labels unverified) → «Установить». (change)
A6. Test: open a card → click the phone number → «Позвонить»; allow microphone/audio in the browser prompt on the first call.

## Side effects to warn about

- **New leads/contacts:** per the official text, contacts and deals are created automatically for incoming and outgoing calls and deals for missed calls when enabled — every unknown caller (spam included) becomes a deal.
- **Pipeline:** the pipeline for new leads is chosen in Zadarma (step 6); changing it affects all future calls only (unverified for existing deals).
- **Responsible:** missed calls from new clients → default responsible. «Направление звонков на ответственного» changes live call routing: known clients skip the IVR; if the responsible user is absent they wait 15 s before falling back (if the return option is on).
- **Duplicates:** two active telephony widgets in amoCRM, or contacts with numbers in different formats, can create duplicate contacts/deals (unverified for Zadarma specifically; general amoCRM behaviour).
- **Tasks:** task creation for missed calls can flood managers (exact rules unverified).
- **Recording storage:** stored in Zadarma's encrypted cloud, not in amoCRM; free storage 200 MB (more is paid); after recording is disabled, recordings are deleted from the cloud after 180 days. Advise clients to download important recordings. What happens when storage is full is not documented (unverified).
- **Billing:** integration and basic PBX are free; calls are charged by Zadarma tariffs, numbers and extra storage are paid.
- **Managers:** each extension should use either the web phone or the Zadarma mobile app, not both; if a manager is not logged in to my.zadarma.com in that browser, their browser calls fail.

## Failure → cause → check → fix

| Failure | Cause | Check (read-only) | Fix |
|---|---|---|---|
| Calls not logged in amoCRM | User has no extension in widget; integration not «Включить»-ed or not the main account; widget not installed on this amoCRM account | Widget settings (extension per user); my.zadarma.com «Настройки» → «Интеграции и API» status | Assign extension (change); re-enable/authorise integration (risky: re-authorisation may reset settings, unverified) |
| Recordings missing in card | «Запись разговоров в облако» off on the extension; storage full; deleted 180 days after recording disabled | Extension settings; storage usage in my.zadarma.com; «Моя АТС» → «Статистика и графики» has the recording? | Enable recording (change); buy storage (risky: billing, client decides) |
| Click-to-call does nothing / no audio | WebRTC off; not logged in to my.zadarma.com in this browser; microphone blocked | «Использовать WebRTC» state; open my.zadarma.com in same browser; site permissions | Enable WebRTC (change); log in; allow microphone |
| Incoming call doesn't reach manager | No device/forwarding on extension; web phone and mobile app both used | Extension settings in «Моя АТС» → «Внутренние номера» | Configure one device or forwarding (change) |
| Known client goes to IVR instead of manager | Responsible unavailable or didn't answer in 15 s; routing option off | Options in «Интеграции и API» block | Enable «Направление звонков на ответственного» (change; changes live routing) |
| Wrong responsible on new deals | Default responsible set to wrong user; extension mapped to wrong user | Widget: default responsible + extension mapping | Correct mapping (change) |
| Leads land in wrong pipeline | Pipeline selection in Zadarma options | «Интеграции и API» → CRM block | Change pipeline (change; affects all new calls) |
| Duplicates | Second telephony widget; number format mismatch (unverified) | «amoМаркет» → «Установленные» → telephony widgets | Disable the extra widget (risky: may be someone's working telephony) |
| Client name not shown on phone | Option off, or device without support | «Отображение имени клиента на IP-телефоне» | Enable option (change) |
| Widget missing / unauthorised | Integration disabled in Zadarma; amoCRM authorisation revoked; widget not available for `*.amocrm.ru` (unverified) | «amoМаркет» → «Телефония»: is Zadarma listed/installed? my.zadarma.com integration state | Re-enable and «Разрешить» as amoCRM admin (change); if no widget exists for the RU domain, use a connector (ApiMonster/Albato — third-party) |

## Real cases

Cases from ITHINK's own work, newest first:

- (none yet)

## Sources

- https://zadarma.com/ru/support/instructions/crm-amo/ (official; text describes Kommo) — checked 2026-11-22
- https://zadarma.com/en/support/instructions/crm-amo/ (official; title «Integration of Zadarma PBX and Kommo») — checked 2026-11-22
- https://zadarma.com/ru/support/instructions/kommo/ — checked 2026-11-22
- https://zadarma.com/en/support/faq/pbx/how-to-record-calls/ — checked 2026-11-22
- https://www.amocrm.ru/support/starting_work/phones/ (amoCRM official: recordings stored by provider) — checked 2026-11-22
- https://apimonster.ru/connector/bundle/amocrm/zadarma (third-party connector, supplementary) — checked 2026-11-22

Not confirmed in official docs: availability and labels of the Zadarma widget on `*.amocrm.ru` (unverified); exact names of the contact/deal/task creation settings (screenshot only); task rules for missed calls; behaviour when cloud storage is full; any Zadarma–Novofon split for Russian clients (unverified, not researched in official docs).
