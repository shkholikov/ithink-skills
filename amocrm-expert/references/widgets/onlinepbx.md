# OnlinePBX in amoCRM

OnlinePBX is a cloud PBX whose amoCRM widget logs calls (with recordings) into contacts/deals, creates contacts, deals or «Неразобранное» entries from calls, pops up the caller card and lets managers call from the browser (WebRTC widget, top-right phone icon). The widget is installed in amoCRM («amoМаркет» → «Телефония»), but almost all logic — pipelines per external number, what to create on incoming/outgoing/missed, default responsible, recordings, user mapping — is set in the OnlinePBX panel under «Сервисы» → «Интеграция» → amoCRM. Panels: **https://panel.onlinepbx.ru/** (RU) and **https://panel.pbx.uz/** (Uzbekistan); knowledge base: https://kb.onlinepbx.ru/. Requires amoCRM admin rights and OnlinePBX panel access; it will not connect to an amoCRM account with a negative balance.

## Setup

### In amoCRM
1. «amoМаркет» → «Телефония» → onlinePBX → «Установить бесплатно» (old UI: «Настройки» → «Интеграции» → «Телефония»). (change)
2. Tick consent to transfer personal data to onlinePBX → «Установить». (change)
3. In the description window tick both checkboxes at the bottom → «Сохранить». Status must become «Установлено». (change)
4. Create the pipelines you need beforehand: «Сделки» → «Добавить воронку». (change)
5. Make sure only ONE widget from «Телефония» is active, and contacts have no custom field named PHONE — both break the integration.

### In the vendor dashboard (OnlinePBX panel)
1. «Сервисы» → «Интеграция» → amoCRM → «Подключить» → choose amoCRM account → «Разрешить». Tabs «Настройки» and «Пользователи» appear. (change)
2. Tab «Настройки», per pipeline: (change)
   - «Воронка» + «Внешние номера» — which external numbers feed this pipeline. A number not assigned to any pipeline is ignored by the integration; one number → one pipeline; nothing is selected by default.
   - «Входящие»: contacts / deals + contacts / «Неразобранное».
   - «Исходящие»: contacts only / deals + contacts.
   - «Пропущенные»: contacts / deals + contacts / «Неразобранное».
   - «Ответственный по умолчанию» and «Этап воронки для сделки».
   - «Дополнительно»: «Загружать записи разговоров» («Не загружать» / «Весь звонок» / «Только разговор»); «Создавать задачи по пропущенному» (task «Связаться», due in 1 hour); «Указывать ответственного по умолчанию, если нет соответствия»; «Создавать новую сделку, если предыдущая закрыта и успешно реализована» / «… и не реализована»; «Добавлять тег с типом звонка»; «Добавлять название внешнего номера в качестве тега»; «Объединять новые контакты и сделки с существующими».
   - «Сохранить». Changes apply within ~10 minutes.
3. Tab «Пользователи»: map every OnlinePBX user (extension) to an amoCRM user → «Сохранить». (change)
4. Recording itself: «Сервисы» → «Запись разговоров» — paid license («Оплатить запись разговоров»), toggle on/off; optional «Стереозапись». Needs at least one paid user and a connected external number (trunk). (change)
5. Users must be paid and enabled: «Настройка АТС» → «Входящие» (toggle in user list). (change)

## Side effects to warn about

- **New leads/contacts:** «Входящие»/«Пропущенные» = deals + contacts creates a deal on every new caller (spam/wrong numbers too). «Создавать новую сделку, если предыдущая закрыта …» creates a new deal for every repeat caller whose last deal is closed.
- **Pipeline/stage:** new deals go to «Этап воронки для сделки» of the pipeline the called external number belongs to. «Неразобранное» cannot be pointed at a pipeline — it lands in the first stage of the default pipeline.
- **Responsible:** auto-created deals get the user who last talked to the client; changing responsible during the call is not saved. Unique missed calls go to «Ответственный по умолчанию». Without «Указывать ответственного по умолчанию, если нет соответствия», calls of unmapped users are not uploaded at all.
- **Duplicates:** with «Объединять новые контакты и сделки с существующими» OFF, duplicate deals are created when no linked contact/company exists.
- **Tasks:** «Создавать задачи по пропущенному» creates a 1-hour task per missed call (not for unique missed calls sent to «Неразобранное»). Can flood managers.
- **Tags:** call-type tags are overwritten by the last call type; no tags in «Неразобранное».
- **Recording storage:** recordings live at OnlinePBX, not in amoCRM (amoCRM shows a link/player). Kept 1 year, and recording runs only while the license is paid; extension of storage can be bought no earlier than 90 days before the paid period ends.
- **Billing:** recording and stereo recording are paid modules; each user is paid per seat.
- **Blacklist:** numbers in «Чёрный список» are not uploaded to amoCRM (rule active ~10 min after adding).
- **Load:** under heavy traffic calls are queued, ~20 s per call; delays are normal.
- **Managers:** the widget works only in desktop browser (not the amoCRM mobile app/mobile browsers); a second telephony widget breaks calls for everyone.

## Failure → cause → check → fix

| Failure | Cause | Check (read-only) | Fix |
|---|---|---|---|
| Calls not logged in amoCRM | External number not in any pipeline; no entity for the number and auto-creation off; unmapped user without default-responsible option; number blacklisted; queue | OnlinePBX panel «Звонки» → column «Загружен в»; open call log → «Результат» status («Звонок не загружен», «Нет информации», «Звонок загружается») | Assign number to pipeline / enable creation / map user (change); single call: «Загрузить звонок в amoCRM» (change) |
| Calls logged but recordings missing | «Загружать записи разговоров» = «Не загружать»; recording license expired/off; recording older than 1 year | «Настройки» tab → «Дополнительно»; «Сервисы» → «Запись разговоров» status/date | Set «Весь звонок» or «Только разговор» (change); pay license (risky: billing, client decides) |
| Call duration looks wrong | «Весь звонок» counts ringing/hold | «Загружать записи разговоров» value | Switch to «Только разговор» (change) |
| Duplicate deals/contacts | «Объединять новые контакты и сделки с существующими» off; two telephony widgets; custom PHONE field | Settings tab; «amoМаркет» → «Установленные» → other telephony widgets; contact fields | Enable merge option (change); disable second widget (risky: may be another team's telephony) |
| Wrong responsible user | Last speaker rule; wrong mapping in «Пользователи»; default responsible | «Пользователи» tab mapping; call log | Fix mapping or default responsible (change) |
| Deals in wrong pipeline/stage | Number bound to another pipeline; «Неразобранное» goes to default pipeline | «Настройки» tab: «Воронка»/«Внешние номера»/«Этап воронки для сделки» | Rebind number / change stage (change; affects all future calls) |
| Widget (phone icon) not shown | Cache; user not paid/enabled; integration disconnected; mapping missing; app not saved; extensions | User toggle in «Настройка АТС» → «Входящие»; «Сервисы» → «Интеграция» status; «Пользователи» tab | Ctrl+F5; «amoМаркет» → «Установленные» → onlinePBX → tick both boxes → «Сохранить» (change); disable ad blockers/VPN; mirror: add `.z1.` to the amoCRM domain; last resort reinstall widget «Отключить» → install (risky) |
| Incoming calls don't ring in widget | «Не беспокоить» on (red); user not in incoming logic; several amoCRM tabs | Widget icon colour; incoming call settings | Turn off «Не беспокоить»; add user to incoming route (change); work in one tab, remove `&compact=yes` from URL |
| Click-to-call / outgoing fails | Operator balance; no default external number; outgoing rules; mapping; microphone blocked | Balance; «Настройка АТС» → «Исходящие» default number; browser site permissions | Set default number/rules (change); allow microphone for the amoCRM site |
| Call popup / notification missing | Multiple amoCRM tabs (only active tab gets it) | Count open tabs | Use one tab; open new tabs via context menu «Открыть новую вкладку» |
| Transfer to mobile fails on outgoing call | Known limitation for unconditional transfer | — | Put the mobile in a group and transfer to the group (change) |
| Integration won't connect | amoCRM account balance negative; not admin | amoCRM account status / user rights | Client pays amoCRM; connect as admin |
| «Неразобранное» empty though enabled | No default responsible set | «Ответственный по умолчанию» | Set it (change) |

Browser: OnlinePBX recommends Google Chrome; developer/beta browser builds are not supported. Support: support@onlinepbx.ru; Uzbekistan support@onlinepbx.uz, +998 78 113-26-50, Telegram @onpbxuz_bot.

## Real cases

Cases from ITHINK's own work, newest first:

- (none yet)

## Sources

- https://kb.onlinepbx.ru/amotsrm-amocrm-kommo (main official amoCRM article) — checked 2026-11-22
- https://kb.onlinepbx.ru/integratsii-s-crm-i-drugimi-servisami — checked 2026-11-22
- https://kb.onlinepbx.ru/zapis-razgovorov — checked 2026-11-22
- https://onlinepbx.ru/call_recording — checked 2026-11-22
- https://onlinepbx.ru/integration — checked 2026-11-22
- https://onlinepbx.ru/support — checked 2026-11-22
- https://pbx.uz/support — checked 2026-11-22
- https://www.amocrm.ru/support/starting_work/phones/ (amoCRM official: recordings are stored by the provider) — checked 2026-11-22

Not confirmed in official docs: whether panel.pbx.uz menus are identical to panel.onlinepbx.ru (unverified); exact widget name shown in amoМаркет (assumed «onlinePBX») (unverified); whether the amoCRM-side recording link stops working after the 1-year retention (unverified, likely).
