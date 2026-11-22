# Wazzup in amoCRM

Wazzup brings WhatsApp, WhatsApp Business API (WABA), Telegram / Telegram Bot, Instagram*, VK, Avito, MAX, Viber and other channels into amoCRM: chats open from the deal/contact card and from a «Wazzup» (or «WZ») button in the left menu, and new clients become deals. Channels, roles, pipeline/stage for new clients and billing are configured in the Wazzup personal account **https://app.wazzup24.ru/** («Каналы», «Интеграция с CRM», «Подписки»). On the amoCRM side there is only the amoМаркет app (install + «Сохранить»), plus amoCRM's own «Контроль дублей» and «Чаты и мессенджеры» settings. Installing the app requires an amoCRM administrator.

\* Instagram / Meta is labelled extremist and banned in the RF; Wazzup marks it that way in its own docs.

## Setup

### In the vendor dashboard (app.wazzup24.ru)
1. «Каналы»: connect at least one channel first (WhatsApp by QR code, Telegram, etc.). Without a channel the integration cannot be configured. (change)
2. «Интеграция с CRM» → amoCRM → paste the account link (`https://<sub>.amocrm.ru`) → «Продолжить» → «Подключить». An amoCRM tab opens. (change)
3. After authorising in amoCRM (step A1), click «Настроить интеграцию».
4. «Выбрать роли»: pull employees from amoCRM («Обновить данные из CRM» if someone is missing) and give each a role: «Менеджер» (writes only to clients where they are responsible, sees only those chats), «Руководитель» (sees and writes to all), «Контроль качества» (sees all, cannot write). Toggle «Получает новых клиентов» for those who should receive new deals → «Применить» → «Готово». (change)
5. Where deals for new clients go: «Неразобранное» (all Менеджер/Руководитель get a notification; first to accept becomes responsible) or a specific pipeline + stage (Wazzup creates the deal and assigns users with «Получает новых клиентов» in turn). (change)
6. Click «Сохранить» in the top panel. Wazzup then offers a chat test and **sends a test message** through the first added channel. (change)
7. Repeat steps 4–6 for every channel: the integration is configured per channel.
8. Tab «Дополнительно» (applies to all channels) — review each option: (change)
   - «Номера, записанные в CRM с 8, учитываются как +7» — **turn OFF for Uzbekistan/Asian clients**, otherwise numbers typed with a leading 8 are sent to +7 (Russia). Make sellers enter +998… format.
   - «Скрывать номера клиентов в Wazzup у выбранных сотрудников».
   - «Расшифровывать ссылки, отправленные Salesbot, в обычный вид» (turns off click tracking).
   - «Уведомлять «Руководителей» по всем сообщениям».
   - «Отображать виджет Wazzup в левом меню CRM».
   - «Приоритетный канал» (only shown if an employee has several WhatsApp/Telegram channels).

### In amoCRM
A1. In the tab Wazzup opened: choose the account → «Разрешить». (change)
A2. «amoМаркет» → search «Wazzup» → «Установить бесплатно» → «Установить» → «Сохранить». «Сохранить» can look inactive; it still works. (change)
A3. Reload the page; the «WZ»/«Wazzup» button appears in the left menu.
A4. Optional: if keeping only the Wazzup widget, turn off imBox in «Настройки» → «Чаты и мессенджеры» (first toggle). Wazzup and imBox do not sync "no reply needed" marks. (change)
A5. Recommended: «Сделки» → «Настроить» (pipeline settings) → «Контроль дублей» → «Настроить правила» → enable source «WhatsApp и Instagram* для amoCRM», disable sources with limited support, set rules, save. (change)

Old amoCRM interface: the app lives in «Настройки» → «Интеграции» → «Установленные интеграции» → «WhatsApp и Instagram* для amoCRM».

## Side effects to warn about

- **Messages to clients:** saving the integration sends a test message via the first channel. Salesbot steps, triggers and mailings send real messages; a contact with several conversations gets one message per conversation (see table).
- **New leads/contacts:** every new client who writes creates a deal (stage chosen in step 5) or an «Неразобранное» entry. Changing step 5 changes where all future deals land; existing deals are not moved (unverified).
- **Responsible user:** with a fixed stage, deals are distributed in turn among users with «Получает новых клиентов». With «Неразобранное», the first person to accept becomes responsible and all others lose sight of that chat.
- **Role changes = visibility changes:** a «Менеджер» sees only clients they are responsible for. Reassigning the responsible user in amoCRM moves the chat away from the previous manager.
- **Duplicates:** contact merges, unpinning chats («Открепить чат»), disabled webhooks or the old pre-Sept-2020 «Чаты Wazzup» widget create duplicate chats/deals.
- **Billing:** paid per channel per month (Start/Inbox/Pro/Max). Dialog limits (e.g. 50 on Start, 500 on Inbox/Pro) count conversations with at least one outgoing message; at the limit you cannot start new dialogs. Writing first is not allowed on every tariff (e.g. Inbox). WABA: separate subscription plus a balance from which Meta template fees and messages beyond 1,000 free service messages/month per number are auto-deducted.
- **Bans:** mass first messages from a regular WhatsApp number risk a ban by WhatsApp; WABA templates can be blocked by Meta.
- **8 → +7 option:** with it ON, numbers like 8 9x … for Uzbek clients go to Russian numbers.
- **Managers:** role/stage changes take effect for everyone; hiding phone numbers affects the Wazzup mobile apps too.

## Failure → cause → check → fix

| Failure | Cause | Check (read-only) | Fix |
|---|---|---|---|
| Messages not arriving in amoCRM at all | Channel not «Активен» (e.g. «Не авторизирован», «Открыт в другом месте», «Не оплачена подписка», «Не в подписке») | Channel status in app.wazzup24.ru → «Каналы» | «Авторизоваться» / rescan QR («Использовать тут») / «Подписки» → «Продлить» or add to «Каналы подписки». (risky: paying) |
| Manager doesn't see chat in a deal | Role «Менеджер» and they are not the responsible user; or channel has no integration configured | Responsible user on the deal; role in «Выбрать роли» for that channel | Reassign responsible or give «Руководитель». (change; affects visibility) |
| New deals land in wrong pipeline/stage | Step 5 setting for that channel | «Интеграция с CRM» → channel → new-client destination | Change pipeline/stage, «Сохранить». (risky: sends test message, affects all new deals) |
| Wrong / same responsible every time | «Получает новых клиентов» on wrong users; «Неразобранное» first-accept race | Roles list and toggles | Adjust toggles → «Применить». (change) |
| Duplicate contacts/deals | Contact merges, unpinned chats, disabled webhooks, old widget, «Контроль дублей» off | amoМаркет → «Web Hooks»: is there an `integrations.wazzup24.com` hook with «Включить» button? «Настройки» → «Интеграции»: is «Чаты Wazzup» (old) present? | Enable webhook; delete old widget (risky); turn on «Контроль дублей» (change); merge contacts via «Списки» → «Контакты» → «объединить», never delete; merge deals keeping earliest «Дата создания». Recurring: send examples to Wazzup support, don't merge. |
| Salesbot sends several messages to one contact | Several amoCRM conversations for one chat (each click on number → «whatsappWZ» creates one) | Count items under «whatsappWZ» → «Открепить чат» menu | Use Salesbot step «Сообщение Wazzup»; or unpin extra conversations (risky: unpinning can cause duplicates) |
| Grey window instead of chats | App not saved after install; third-party cookies blocked | Does app.wazzup24.ru work in same browser? | amoМаркет → «Установленные» → Wazzup → «Сохранить»; allow third-party cookies («Сторонние файлы cookie») in browser |
| No Wazzup button in left menu | App not saved; option «Отображать виджет Wazzup в левом меню CRM» off; UI not refreshed | «Дополнительно» tab option; amoМаркет «Установленные» | «Сохранить» app, reload; then change timezone in «Настройки» → «Общие настройки», save, reload, set it back (risky: briefly affects task/report times) |
| Message goes to a Russian number | «Номера … с 8, учитываются как +7» ON | «Дополнительно» tab | Turn OFF (change); fix numbers to +998 format |
| Cannot write to new clients | Dialog limit reached («Превышен лимит диалогов») or tariff without first-message | Channel status; «Счетчик» tab in channel card | Change tariff (risky: billing) or wait for the 1st of the month |
| WhatsApp number banned | Spam reports, mass mailing, emulators | Channel status; WhatsApp app on phone | Client taps «Запросить проверку» in WhatsApp, one request; after restore, warm up 24 h (10–15 active chats) before reconnecting by QR. Never use emulators. |
| WABA «Забанен» / «Закончились деньги» / «На модерации» | Meta ban / empty WABA balance / Meta verification | Channel status | Ban: Wazzup support; balance: «Подписки» → ⋮ → «Пополнить баланс подписки» (risky: payment, client does it) |
| «Заблокирован» | Technical block | Channel status | Wazzup support |

## Real cases

Cases from ITHINK's own work, newest first:

- (none yet)

## Sources

- https://wazzup24.ru/help/amocrm/snachala-podkljuchite-integraciju-2/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/zatem-nastrojte-integraciju/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/dopolnitelno-dobejte-melkie-no-vazhnye-nastrojki-dlya-raboty-integracii-2/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/wazzup-chats-for-amocrm-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/how-to-get-rid-of-duplicates-in-amocrm/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/blank-screen-in-amocrm-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/the-wazzup-button-on-the-left-panel-of-amocrm-is-not-displayed-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/amocrm/salesbot-sends-multiple-messages-to-one-contact-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/how-to-use/channels-statuses-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/how-to-use/bans-in-whatsapp-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/payment/price-plans-ru/ — checked 2026-11-22
- https://wazzup24.ru/help/payment/whatsapp-business-api-charging/ — checked 2026-11-22
- https://www.amocrm.ru/support/incoming_leads/kontrol-dublej/ (amoCRM official) — checked 2026-11-22

Not confirmed in official docs: whether changing the new-client stage moves existing deals (assumed not); exact behaviour when the WABA balance hits zero beyond the «Закончились деньги» status; Uzbekistan-specific pricing (prices above are RUB from wazzup24.ru).
