# Claude ilovasiga skill o'rnatish

Bu qo'llanma ITHINK xodimlari uchun. Dasturchi bo'lish shart emas —
terminal ham, `git` ham kerak emas. Taxminan 3 daqiqa vaqt oladi.

Skill — bu Claude'ga qo'shiladigan qo'shimcha malaka. O'rnatgandan keyin
Claude tarmoq sxemasi, tizim diagrammasi, ITHINK hujjatlarini
tayyorlashni va amoCRM sozlashda yordam berishni biladi.

**Kerak bo'ladi:** Claude Pro obunasi va [claude.ai](https://claude.ai)
saytidagi hisob.

---

## 1-qadam — fayllarni yuklab oling

[Releases sahifasini oching](https://github.com/shkholikov/ithink-skills/releases/latest)
va eng yuqoridagi reliz ostidagi **Assets** bo'limidan kerakli `.zip`
fayllarni yuklab oling:

| Fayl | Nima qiladi |
|---|---|
| `topology-creator-skill.zip` | Tarmoq topologiyasi sxemasi — Cisco ikonkalari, VLAN ranglari, port belgilari. Natija: draw.io fayli, uni tahrirlash mumkin |
| `system-diagram-skill.zip` | Tizim va jarayon diagrammasi — SVG, animatsiyali SVG va GIF |
| `ithink-documents-skill.zip` | Mijozlar uchun ITHINK hujjatlari — tijorat taklifi, taqdimot, texnik taklif |
| `amocrm-expert-skill.zip` | amoCRM integratori yordamchisi — vidjetlarni (Wazzup, OnlinePBX, Zadarma), Salesbot va voronkalarni tekshirish va sozlash. Sizning «ha»ingizsiz hech narsani o'zgartirmaydi |

Hammasini yuklab olishingiz mumkin, faqat kerakligini ham.

> Assets ro'yxatida **Source code** (zip va tar.gz) ham turadi — ularni
> yuklab olmang. Bu butun loyihaning nusxasi, skill emas; Claude uni qabul
> qilmaydi. Faqat yuqoridagi `-skill.zip` fayllar kerak.

> `.zip` faylni **ochmang** va **arxivdan chiqarmang**. Claude'ga aynan
> `.zip` ko'rinishida yuklanadi. macOS Safari arxivni avtomatik ochib
> yuborishi mumkin — bunday holda Yuklamalar papkasidagi papkani o'ng
> tugma bilan bosib, "Compress" orqali qayta `.zip` qiling.

## 2-qadam — Claude'ga yuklang

1. [claude.ai](https://claude.ai) saytiga kiring (yoki Claude Desktop ilovasini oching)
2. Chap pastdagi ismingiz ustiga bosing → **Settings**
3. **Capabilities** → **Skills** bo'limiga o'ting
4. **Upload skill** tugmasini bosing
5. 1-qadamda yuklab olgan `.zip` faylni tanlang
6. Har bir skill uchun 4–5-qadamlarni takrorlang

Skill ro'yxatda paydo bo'lganini va yoqilganini tekshiring.

## 3-qadam — ishlayotganini tekshiring

Yangi suhbat oching va shunday yozing:

> Menda 2 ta kommutator, 1 ta router va 10 ta kompyuter bor. Shu tarmoqning
> topologiya sxemasini chizib ber.

Claude kerakli skillni o'zi tanlaydi — nomini aytish shart emas. Javobda
yuklab olish mumkin bo'lgan fayl bo'lishi kerak.

Boshqa misollar:

> Bizning to'lov tizimi qanday ishlashini diagramma qilib ber
>
> Mijoz uchun tijorat taklifi tayyorla — server infratuzilmasini yangilash bo'yicha
>
> (ochiq amoCRM sahifasida) Nega bitimlarga WhatsApp xabarlari kelmay qoldi?

## Barcha skillarni bitta o'rnatishda (Cowork)

Har bir `.zip` ni alohida yuklash o'rniga butun repozitoriyni plagin
sifatida ulash mumkin — barcha skillar birdaniga o'rnatiladi va o'zi
yangilanadi.

1. Claude Desktop → **Cowork** yorlig'i → **Customize**
2. **Plugins** yorlig'i → **+** (Add) → **Add marketplace** → **Add from a repository**
3. `shkholikov/ithink-skills` ni kiriting
4. **Discover** yorlig'ida **ithink** plaginini topib, **Install** ni bosing
5. Yangi versiyalar o'zi kelishi uchun **Sync automatically** ni yoqing

Agar Add marketplace bandi bo'lmasa — 1–2-qadamlardagi `.zip` yuklashdan foydalaning.

## amoCRM-ekspert Chrome'da

Skill **Claude in Chrome** kengaytmasida, to'g'ridan-to'g'ri
`{mijoz}.amocrm.ru` sahifasida ishlash uchun mo'ljallangan.

1. Claude kengaytmasini
   [Chrome Web Store](https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn)
   dan o'rnating va Claude hisobingizga kiring
2. Kengaytma sozlamalarida **Manually approve** (qo'lda tasdiqlash)
   rejimini tanlang — Claude sahifadagi har bir harakatdan oldin ruxsat
   so'raydi. Bu skill qoidalari ustidan ikkinchi himoya
3. `amocrm-expert` skilli (yoki **ithink** plagini) yoqilganini
   tekshiring — hisobdagi skill va plaginlar Chrome yon panelida mavjud
4. Skill ishonchli yoqilishi uchun profilga bitta qator qo'shing:
   claude.ai → **Settings** → **Profile** → «What personal preferences
   should Claude consider in responses?» maydoni:

   > Когда я работаю в amoCRM или в кабинете виджета (Wazzup, OnlinePBX,
   > Zadarma), всегда используй навык amocrm-expert. Отвечай по-русски.

   Claude bu maydonni har bir suhbatda, jumladan Chrome'da ham o'qiydi.
   (Javoblar o'zbekcha bo'lishini istasangiz, oxirgi gapni «Отвечай
   по-узбекски» ga almashtiring.)
5. Mijoz hisobini oching va yon panelda yozing: «Qaysi hisobda ishlayapmiz
   va bu yerda qaysi vidjetlar o'rnatilgan?» Javob «Работаем в аккаунте …»
   bilan boshlansa — skill ulangan.

**Skillni qanday aniq chaqirish mumkin.** Odatda Claude amoCRM haqida gap
ketganda skillni o'zi yoqadi. Yoqmasa — xabarni «Используй навык
amocrm-expert:» so'zlari bilan boshlang, masalan: «Используй навык
amocrm-expert: почему не приходят сообщения из WhatsApp?».

U qanday ishlaydi:

- Avval qaysi mijoz hisobida ekanini aytadi
- O'zi faqat o'qiydi: sozlamalar, vidjetlar, bitimlarni ochib, sababini qidiradi
- Har qanday o'zgarishdan oldin **o'zgarish kartasini** ko'rsatadi: nima
  qilinadi, oqibatlari (Salesbot, triggerlar, mijozlarga xabarlar), kimga
  ta'sir qiladi, qanday qaytariladi
- O'zgarishni faqat sizning aniq «ha»ingizdan keyin qiladi
- Login, parol va kalitlarni o'zingiz kiritasiz — Claude ularni kiritmaydi

## Yangilash

Skill sizning Claude hisobingizda saqlanadi — kompyuterda emas, balki
Anthropic serverida, faqat siz uchun. Shuning uchun uchta narsani bilib
qo'ying:

- **Avtomatik yangilanmaydi.** Biz yangi versiya chiqarsak, sizdagi eski
  nusxa o'zi o'zgarmaydi — qo'lda qayta yuklashingiz kerak.
- **claude.ai va Claude Desktop alohida.** Ikkalasida ishlatmoqchi
  bo'lsangiz, har biriga alohida yuklang.
- **Qaysi versiya turganini bilish uchun** Claude'dan so'rang:
  «topology-creator skillning qaysi versiyasi sizda bor?». Javobni
  [Releases sahifasidagi](https://github.com/shkholikov/ithink-skills/releases/latest)
  raqam bilan solishtiring.

Yangilash tartibi:

1. Yangi `.zip` ni Releases sahifasidan yuklab oling
2. Settings → Capabilities → Skills bo'limida **eski skillni o'chiring**
3. Yangi `.zip` ni yuklang
4. **Yangi suhbat oching.** Claude skillar ro'yxatini suhbat boshlanganda
   o'qiydi, shuning uchun ochiq turgan eski chatda hamon eski versiya
   ishlaydi

---

## Muammolar

**Skill ro'yxatda ko'rinmayapti.** Sahifani yangilang. Claude Desktop'da
ilovani butunlay yopib, qaytadan oching.

**"Invalid skill package" xatosi.** Arxiv noto'g'ri tuzilgan. Ehtimol siz
uni ochib, qayta arxivlagansiz. Releases sahifasidan faylni qaytadan
yuklab oling va o'zgartirmasdan yuklang.

**Claude skillni ishlatmayapti.** To'g'ridan-to'g'ri ayting:
"topology-creator skilldan foydalanib, shu tarmoqni chizib ber".

**Yangi versiya chiqdi.** Settings → Capabilities → Skills bo'limidan
eskisini o'chirib, yangi `.zip` ni yuklang.

Savollar bo'lsa — Shohzod bilan bog'laning yoki
[GitHub'da issue oching](https://github.com/shkholikov/ithink-skills/issues).
