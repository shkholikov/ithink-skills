# Diagnosing a widget

Read-only order of checks for any widget that "does not work". Go top to bottom
and stop at the first check that explains the symptom; then confirm it with one
more observation before proposing a fix. Each step names what to look at, never
what to change.

1. **Exact symptom.** What is missing, since when, for everyone or one manager,
   one channel or all. Open one concrete example (a chat, a call, a deal) and
   look at its event feed.
2. **Widget status in amoCRM.** Настройки → Интеграции: is it installed and
   enabled, any red error, «требуется авторизация», expired trial or licence.
   Open its settings screen and read every field.
3. **Account plan.** Some widgets and Salesbot features need a minimum amoCRM
   tariff; an expired account stops integrations (writes fail before reads).
4. **Vendor side.** Open the vendor's dashboard: channel or line status, balance
   and payment, the connection to this exact amoCRM account (subdomain), error
   logs, recent events. A balance at zero or a channel in «отключён» explains
   most messenger and telephony outages.
5. **Users and rights.** The widget's technical user exists and is active; the
   affected manager is mapped in the widget (extension, channel access); amoCRM
   rights let them see the pipeline where the records land.
6. **Routing.** Source → pipeline / stage / responsible mapping in the widget,
   «Неразобранное» enabled or not, duplicate control settings. Messages that
   «don't arrive» often arrive in another pipeline, in Неразобранное, or attach
   to an older duplicate contact — search by phone before concluding.
7. **Automation interference.** Digital Pipeline triggers and Salesbots on the
   landing stage: something may move, close or reassign the deal right after it
   arrives.
8. **Browser.** For UI-only problems (widget panel missing, click-to-call dead,
   softphone not loading): page reload, another browser profile, blocked
   third-party cookies, microphone permission, extensions. Ask him to try; do not
   change browser settings yourself.

When the cause is found, write it as: Симптом → Причина → Доказательство (what
you saw, where) → Предлагаемое исправление (then a change card).

If nothing explains it, say so, list what you checked, and suggest what to ask
the vendor's support with the evidence collected.
