# Side effects in amoCRM

What a change can set off beyond the field you touch. Before a change card, go
through every section that applies to the change and name what you find in the
account map; «нет» is an answer only after you looked.

## Moving a deal between stages

- **Digital Pipeline triggers** on the target stage run on entry: send a message
  or email, create a task, change the responsible user, set a field, add or
  remove tags, call a webhook, move to another stage, start a widget action.
  Triggers can also fire on leaving the previous stage. A trigger set "for all
  deals" also hits deals moved by hand.
- **Salesbot** attached to the target stage starts for that deal and can message
  the client in their messenger immediately.
- **Required fields** on the stage (Настройки полей → обязательные для этапа)
  block the move or open a dialog — read it, do not fill it by guess.
- **«Успешно реализовано» / «Закрыто и не реализовано»** close the deal: open
  tasks remain, loss reason may be required, reports and sales plan change.
- **Widgets** (telephony, messengers, document generators, 1C/payment) may act
  on a stage: issue an invoice, send a document, sync to 1C.

## Editing a deal, contact or company

- Changing the **responsible user** may trigger notifications and distribution
  rules, and moves the record out of other users' sight if rights are restricted.
- Changing a **phone or email** affects which incoming calls and messages attach
  to this contact, and duplicate control.
- **Merging** duplicates is not reversible from the UI.
- **Tags and fields** can be conditions for triggers and Salesbots elsewhere.

## Messages and calls

- Anything sent through a messenger, email or SMS widget reaches the client and
  cannot be recalled.
- Paid channels (WhatsApp templates outside the 24-hour window, SMS) cost money
  per message.
- Starting a call through click-to-call rings the client.

## Widgets and integrations

- **Installing** a widget grants it access to the account's data (read the
  permissions screen) and may create fields, pipelines, sources or a technical
  user.
- **Disabling or uninstalling** stops its flow at once: messages or calls stop
  arriving, triggers that use it break silently, and some widgets delete their
  settings on uninstall.
- **Re-authorising** a widget or reconnecting a channel interrupts the flow until
  finished; a QR scan or SMS step needs the phone's owner.
- **Changing the source → pipeline mapping** changes where new leads land and who
  they go to, from now on; existing deals stay.
- **Vendor-side changes** (channel settings, call routing, IVR, recording) act
  outside amoCRM; amoCRM shows no trace until the next event.

## Salesbot and Digital Pipeline edits

- A change applies to every future run in that pipeline; deals already passing
  through a bot keep the old version or break mid-run depending on the step.
- Deleting a stage that has deals forces moving them.
- Turning a trigger off can silently break a chain other triggers depend on.

## Users and rights

- Rights changes take effect immediately for that user and group.
- Deactivating a user frees a paid seat but leaves their deals with them until
  reassigned.
- Plan limits: seats, pipelines, fields and Salesbot steps depend on the tariff;
  a change may hit a limit or require a paid upgrade.

## Bulk actions

- A list action applies to every selected record, including those beyond the
  current screen if «выбрать все» is used — state the exact count.
- Bulk stage changes fire the stage's triggers and Salesbots for each deal.
- Bulk deletes go to the trash only for a limited time, if at all — treat as
  irreversible.
- Import can create duplicates and fire triggers on the target stage.
