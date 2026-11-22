# Change card

Show this card, in Russian, before every change. Fill every line; a line that
truly does not apply says «нет» — an empty line hides whether you checked.

```
**Изменение** <⚠ if heightened risk>
Аккаунт: <subdomain>.amocrm.ru  |  или сервис: <vendor dashboard>
Что сделаю: <exact action, exact names: which deal / field / widget / setting, old value → new value>
Где: <menu path as on screen>
Последствия: <concrete triggers, Salesbots, widget actions, messages, new leads, notifications this will set off — or «нет, проверил: …»>
Кого затронет: <clients / managers / the whole account / only this record>
Откат: <how to undo, or «необратимо»>
Риск: низкий | средний | ⚠ высокий
Делаю? (да / нет)
```

Rules:

- **Exact values.** «Изменю этап» is not a card; «Сделка «Ремонт офиса» (#12345): этап «Переговоры» → «Счёт выставлен»» is.
- **Last line is the question.** End with «Делаю? (да / нет)» and stop there.
- **Bulk changes** list the count and the filter that selects them, plus the first few names: «23 сделки в воронке «Продажи», этап «Новая заявка», старше 30 дней: …».
- **Unknown side effect.** If you could not check a trigger (no access to that screen, a vendor black box), say so in «Последствия» rather than writing «нет».

## Example: moving a deal

```
**Изменение**
Аккаунт: stroyplus.amocrm.ru
Что сделаю: сделка «Ремонт офиса» (#12345): этап «Переговоры» → «Счёт выставлен»
Где: карточка сделки → поле этапа
Последствия: на этапе «Счёт выставлен» стоит Salesbot «Отправка счёта» — он сразу отправит клиенту в WhatsApp (Wazzup) шаблон со ссылкой на оплату; также создастся задача «Проверить оплату» на ответственного (триггер Digital Pipeline)
Кого затронет: клиент получит сообщение; менеджер Азиз получит задачу
Откат: этап вернуть можно, но отправленное сообщение не отзывается
Риск: средний — сообщение клиенту
Делаю? (да / нет)
```

## Example: reconnecting a Wazzup channel ⚠

```
**Изменение** ⚠
Аккаунт: сервис Wazzup (кабинет клиента stroyplus)
Что сделаю: канал WhatsApp +998 ** *** ** 45 — «Переподключить» (новый QR-код)
Где: Wazzup → Каналы → канал → Переподключить
Последствия: пока канал не подключён заново, входящие из WhatsApp не попадут в amoCRM; после подключения Wazzup подтянет пропущенные сообщения за период, который он хранит (проверим после); новые сделки не создаются заново по уже существующим чатам
Кого затронет: все менеджеры, работающие с WhatsApp в этом аккаунте
Откат: необратимо в смысле отключения — QR сканирует владелец телефона, это нужно сделать сразу
Риск: ⚠ высокий — канал будет недоступен до сканирования QR
Делаю? (да / нет)
```

## Example: editing a Salesbot ⚠

```
**Изменение** ⚠
Аккаунт: stroyplus.amocrm.ru
Что сделаю: Salesbot «Приветствие» — текст первого сообщения: «Здравствуйте!» → «Здравствуйте! Это компания СтройПлюс, …»
Где: Сделки → Настроить → этап «Новая заявка» → Salesbot «Приветствие» → редактор
Последствия: новый текст получат все новые входящие клиенты с момента сохранения; уже запущенные боты не меняются; другие этапы не затронуты
Кого затронет: все новые клиенты из мессенджеров
Откат: вернуть старый текст (сохраню его здесь: «Здравствуйте!»)
Риск: ⚠ высокий — затрагивает всех новых клиентов
Делаю? (да / нет)
```
