# AI Football Hub Uzbekistan

Jonli futbol natijalari, sun'iy intellekt tahlillari va Telegram bildirishnomalari.

| Qism | Texnologiya | Manzil |
| --- | --- | --- |
| Backend | FastAPI + SQLAlchemy (async) + SQLite | http://localhost:8000 ([/docs](http://localhost:8000/docs)) |
| Frontend | Next.js 16 + React 19 + Tailwind 4 | http://localhost:3000 |
| Bot | aiogram 3 | Telegram |

---

## Tez ishga tushirish

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env
```

`.env` faylida **kamida** `ADMIN_TOKEN` ni to'ldiring:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Keyin ishga tushiring:

```bash
.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### 3. Bot (ixtiyoriy)

`.env` da `TELEGRAM_BOT_TOKEN` ni belgilab:

```bash
cd backend
.venv/Scripts/python -m bot.bot
```

---

## Ishlash rejimlari

Loyiha `API_FOOTBALL_KEY` bor-yo'qligiga qarab ikki xil ishlaydi:

**Simulyatsiya rejimi** (kalit yo'q — standart holat)
: O'yinlar avtomatik yaratiladi, belgilangan vaqtda boshlanadi, 90 daqiqa
davom etadi, gollar uriladi va tugaydi. Jadvalda doim 5 ta bo'lajak o'yin
turadi, ya'ni sayt hech qachon bo'sh qolmaydi.

**Real ma'lumot rejimi** (`API_FOOTBALL_KEY` sozlangan)
: [API-Football](https://www.api-football.com/) dan jonli o'yinlar olinadi.
So'rovlar `API_FOOTBALL_POLL_SECONDS` (standart 900s) oralig'ida yuboriladi —
bepul tarifning kunlik 100 so'rov limitiga sig'adi (~96/kun). So'rov
muvaffaqiyatsiz bo'lsa hech narsa o'ylab topilmaydi, oxirgi ma'lum holat
saqlanadi.

### AI: uch qatlamli zaxira

Matn generatsiyasi ketma-ket uch manbadan urinadi:

1. **Gemini API** — `GEMINI_API_KEY` bilan (asosiy yo'l)
2. **Vertex AI** — `GCP_PROJECT_ID` + service account bilan (zaxira)
3. **O'zbekcha shablonlar** — hech biri ishlamasa

Asosiy kalit limitga urilsa, o'chirilsa yoki tarmoq uzilsa so'rov avtomatik
Vertex'ga o'tadi. Foydalanuvchi farqni sezmaydi, log'da esa
`AI manbasi: Vertex AI` qatori chiqadi.

Zaxirani yoqish uchun `.env` da:

```bash
GCP_PROJECT_ID="loyiha-id"
VERTEX_LOCATION="global"
VERTEX_CREDENTIALS_FILE="service-account.json"   # backend/ ga nisbatan yo'l
VERTEX_MODEL=""                                   # bo'sh = GEMINI_MODEL bilan bir xil
```

> **Diqqat:** Vertex'da model nomlari Gemini API'dagidan farq qilishi mumkin
> va regionga bog'liq. Masalan `gemini-3.5-flash-lite` `global` da bor, lekin
> `us-central1` da yo'q. Model topilmasa log'da `404 NOT_FOUND` chiqadi —
> o'shanda `VERTEX_LOCATION` yoki `VERTEX_MODEL` ni o'zgartiring.

---

## Ma'lumot manbai

Uchta rejim, ustuvorlik shu tartibda:

**1. TheSportsDB (standart, bepul).** Nima uchun aynan shu: bepul kalitida
**O'zbekiston Superligasi** bor (liga 4794). Boshqa bepul xizmatlarda
(masalan football-data.org) faqat 12 ta yirik Yevropa ligasi mavjud, bu esa
O'zbekiston auditoriyasi uchun mo'ljallangan saytga to'g'ri kelmaydi.

```bash
SPORTSDB_ENABLED=true
SPORTSDB_API_KEY="3"      # "3" — ochiq sinov kaliti; o'zingiznikini oling
SPORTSDB_LEAGUES="4794,4480,4339,4328,4335"
SPORTSDB_POLL_SECONDS=600
```

Kuzatiladigan ligalar:

| ID | Liga | |
|---|---|---|
| 4794 | O'zbekiston Superligasi | |
| 4480 | UEFA Chempionlar ligasi | |
| 4328 | Angliya Premyer-ligasi | katta beshlik |
| 4335 | Ispaniya La Liga | katta beshlik |
| 4332 | Italiya Seriya A | katta beshlik |
| 4331 | Germaniya Bundesligasi | katta beshlik |
| 4334 | Fransiya Ligue 1 | katta beshlik |
| 4339 | Turkiya Super Ligasi | |

> **Ikkinchi divizionlar bilan adashtirmang.** Qidiruvda ular yuqorida
> chiqishi mumkin: `4676`="Turkish 1 Lig", `4394`="Serie B",
> `4399`="2. Bundesliga", `4401`="Ligue 2".

Mavsumi hali boshlanmagan liga (jadvalda hamma jamoada 0 o'yin) avtomatik
yashiriladi va mavsum boshlanishi bilan o'zi paydo bo'ladi.

### So'rovlar tezligi

Har liga uchun alohida so'rov ketadi (ligasiz `eventsday.php` bepul kalitda
atigi 3 ta o'yin qaytaradi, ya'ni so'rovlarni birlashtirib bo'lmaydi):
8 liga × 3 kun + 8 jadval ≈ 32 so'rov. Bepul tarif daqiqasiga 30 ta beradi,
shuning uchun:

* `SPORTSDB_REQUEST_INTERVAL_MS=2200` — so'rovlar orasidagi tanaffus
* turnir jadvali keshlanadi va **fon vazifasi keshni oldindan to'ldiradi** —
  busiz `/standings/` bir daqiqagacha ochilmasdi

Liga qo'shsangiz `SPORTSDB_POLL_SECONDS` ni ham oshirishni unutmang.

Boshqa liga ID'sini topish:

```bash
curl "https://www.thesportsdb.com/api/v1/json/3/search_all_leagues.php?c=Germany&s=Soccer"
```

Cheklov: bepul tarifda **jonli daqiqama-daqiqa hisob yo'q** (u $9/oy
tarifida). Shuning uchun o'yinlar faqat ikki holatda bo'ladi — boshlanmagan
(NS) yoki tugagan (FT). Soxta "jonli daqiqa" ko'rsatilmaydi.

Turnir jadvali `lookuptable.php` dan, ya'ni **rasmiy** jadval olinadi.
O'yinlardan hisoblab bo'lmaydi: bepul tarifda faqat bir necha kunlik
o'yinlar keladi, mavsum boshidan beri hamma natija bazada yo'q.

**2. API-Football (ixtiyoriy, pullik).** `API_FOOTBALL_KEY` qo'yilsa
TheSportsDB o'rniga shu ishlatiladi — jonli hisob bilan.

**3. Simulyatsiya.** Ikkalasi ham o'chirilgan bo'lsa. Bunda o'yinlar
to'qib chiqariladi, shuning uchun saytning har bir sahifasi tepasida sariq
ogohlantirish chiqadi (`components/SimulationNotice.tsx`). Busiz tashrif
buyuruvchi "Liverpool 1-0 Arsenal" ni bugungi haqiqiy natija deb qabul
qilardi.

Joriy rejimni bilish: `GET /api/v1/meta/` -> `{"data_source": "...", "is_simulated": ...}`

## Sayt nega "bugungi" ko'rinishda qoladi

Ikki mexanizm buni ta'minlaydi:

**O'yin markazi — vaqt oynasi.** Bosh sahifa `/matches/?days=2` ni so'raydi,
ya'ni kecha, bugun va ertangi bahslar. Busiz haftalar oldingi tugagan o'yinlar
ham ro'yxatda turaverardi. Eski o'yinlar bazadan o'chirilmaydi — ular turnir
jadvalida hisobga olinaveradi, shunchaki bosh sahifada ko'rinmaydi.

**Yangiliklar — avtomatik yoziladi.** Simulyator yakunlangan o'yin haqida AI
maqolasi tayyorlaydi (`generate_match_report`). Busiz "Qaynoq Xabarlar" bir
marta yozilgan maqola bilan qotib qolardi. Takrorlanmasligi uchun faqat
oxirgi maqoladan **keyin** tugagan o'yin haqida yoziladi, va maqolalar
`NEWS_MIN_INTERVAL_HOURS` (3 soat) dan tez-tez chiqmaydi.

## Jamoa sahifalari

`/teams/{slug}` — profil, o'yinlar va turnir jadvalidagi o'rni.
`GET /api/v1/teams/` va `/api/v1/teams/{slug}`.

**Slug ikki joyda hisoblanadi va aynan bir xil bo'lishi shart:**
`app/services/teams.py:team_slug` (backend) va `lib/teamSlug.ts` (frontend).
Havolalar frontendda quriladi, sahifa esa backendda shu slug bo'yicha
topiladi — biri o'zgarsa havolalar 404 beradi. Diakritik belgilar lotinga
o'giriladi: `Fenerbahçe` → `fenerbahce`, `Górnik` → `gornik`.

**Profil bosqichma-bosqich yuklanadi.** `lookup_all_teams.php` bepul kalitda
liga ID'sini e'tiborsiz qoldiradi (qaysi liga so'ralmasin, bir xil 24 ta
ingliz jamoasini qaytaradi — tekshirilgan), shuning uchun har jamoa nomi
bo'yicha alohida qidiriladi va natija `teams` jadvalida saqlanadi.
Har qadamda bir nechtasi olinadi.

Shu sababli **sahifa profilsiz ham ishlaydi**: turnir jadvali va o'yin
kartalari barcha jamoalarni havola qiladi, profili hali yuklanmagani
bosilsa 404 chiqmasligi kerak. Bunday holatda sahifa o'yinlardan quriladi,
profil keyinroq qo'shiladi.

Jamoaning ligasi **o'z chempionatidan** olinadi, o'yin ligasidan emas:
Chempionlar ligasidagi o'yin uchun aks holda "Danish Superliga" nomi bilan
`league_id=4480` juftligi chiqib qolardi.

**Tavsiflar o'zbekchaga o'giriladi.** Manba ularni inglizcha beradi; fon
vazifasi Gemini orqali tarjima qiladi va `teams.description_uz` ga yozadi.
Asl matn o'chirilmaydi — tarjima tayyor bo'lguncha (yoki AI ishlamasa)
sayt o'shani ko'rsatadi. API tayyor matnni `description` da qaytaradi va
`description_translated` bilan uning tarjima ekanini bildiradi; sahifada
bu ochiq yoziladi.

## Turnir jadvali

`/standings` sahifasi va `GET /api/v1/standings/` endpointi.

Jadval **alohida saqlanmaydi** — har safar tugagan o'yinlardan qayta
hisoblanadi (`app/services/standings.py`). Shu sababli u hech qachon o'yin
natijalari bilan nomuvofiq bo'lib qolmaydi: admin hisobni tuzatsa yoki
o'yin qayta o'ynalsa, jadval o'zi yangilanadi.

Qoida: g'alaba — 3 ochko, durang — 1. Ochkolar teng bo'lganda gollar farqi,
keyin urilgan gollar, oxirida alifbo tartibi (natija barqaror bo'lishi uchun).
"Forma" ustuni oxirgi 5 o'yin natijasini ko'rsatadi.

## Xavfsizlik

- Barcha **yozish** endpointlari `X-Admin-Token` sarlavhasini talab qiladi:
  `POST /news/`, `POST /matches/{id}/preview`, `/analysis` va butun `/admin/*`.
- `ADMIN_TOKEN` sozlanmagan bo'lsa bu endpointlar umuman ishlamaydi
  (fail-closed, HTTP 503) — standart parol bilan ochiq qolib ketish holati yo'q.
- **O'qish** endpointlari ochiq: `GET /matches/`, `GET /news/`, `/health`.
- `.env` va service account kalitlari `.gitignore` da.

Admin panel: http://localhost:3000/admin — `backend/.env` dagi `ADMIN_TOKEN`
qiymatini kiriting.

---

## Telegram bildirishnomalari

Foydalanuvchi botda sevimli jamoasini tanlaydi:

```
/setteam Pakhtakor
/unsetteam        — o'chirish
/teams            — mavjud jamoalar
```

Shundan keyin o'sha jamoa gol urganda darhol xabar keladi. Xabarlar backend
tomonidan to'g'ridan-to'g'ri Telegram API orqali yuboriladi — bot jarayoni
ishlayotgan bo'lishi shart emas.

---

## Baza migratsiyalari (Alembic)

Sxema **ilova ishga tushganda avtomatik yangilanadi** — alohida buyruq kerak
emas. Eski (Alembicdan oldingi) bazalar birinchi ishga tushishda boshlang'ich
revizyada belgilanadi, ma'lumot yo'qolmaydi.

Modelga o'zgartirish kiritganingizda migratsiya yozing:

```bash
cd backend
.venv/Scripts/python -m alembic revision --autogenerate -m "matches jadvaliga stadion qo'shildi"
```

Yaratilgan faylni **albatta o'qib chiqing** — autogenerate hamma narsani
to'g'ri aniqlamaydi (masalan ustun nomini o'zgartirishni "eskisini o'chir,
yangisini qo'sh" deb tushunadi, bu esa ma'lumotni yo'q qiladi).

Foydali buyruqlar:

```bash
.venv/Scripts/python -m alembic current              # hozirgi revizya
.venv/Scripts/python -m alembic history              # tarix
.venv/Scripts/python -m alembic upgrade head         # qo'lda yangilash
.venv/Scripts/python -m alembic downgrade -1         # bir qadam orqaga
.venv/Scripts/python -m alembic upgrade head --sql   # SQL ni ko'rish (bajarmasdan)
```

`tests/test_migrations.py` modellar va migratsiyalar mos kelishini tekshiradi —
migratsiya yozishni unutsangiz test yiqiladi.

## Testlar

```bash
cd backend
.venv/Scripts/python -m pytest
```

Qamrov: g'alaba ehtimoli (manfiy qiymat va yaxlitlash), vaqt zonasi,
o'yin hayot sikli (NS → LIVE → FT), API xavfsizligi, slug yasash,
gol xabarnomasi.

Frontend:

```bash
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

---

## Docker

```bash
cp backend/.env.example .env     # ADMIN_TOKEN ni to'ldiring
docker compose up --build
```

Bot bilan birga:

```bash
docker compose --profile bot up --build
```

---

## Muhim texnik kelishuvlar

**Vaqt.** Bazada naive UTC saqlanadi, API javobida timezone belgisi bilan
qaytariladi (`app/core/clock.py`). Frontend hamma joyda `Asia/Tashkent`
zonasida ko'rsatadi (`lib/time.ts`) — server va brauzer bir xil natija beradi.

**Baza yo'li.** `DATABASE_URL` bo'sh bo'lsa `backend/futbol.db` (absolyut yo'l)
ishlatiladi. Nisbiy yo'l serverni qayerdan ishga tushirganingizga bog'liq
bo'lib, tasodifan yangi bo'sh baza yaratilishiga olib kelardi.

**SSR.** Sahifalar server komponent sifatida ma'lumotni yuklaydi va tayyor
HTML yuboradi (SEO uchun), keyin klient komponentlar WebSocket orqali jonli
yangilanishlarni ustiga qo'yadi.

**Ehtimollar.** Bitta formula ikki joyda takrorlangan:
`app/services/probability.py` va `lib/probability.ts`. Ularni o'zgartirsangiz
ikkalasini birga o'zgartiring.

**Sxema.** `Base.metadata.create_all` ishlatilmaydi — sxemani faqat Alembic
boshqaradi (`app/core/migrations.py`). `create_all` mavjud jadvalga ustun
qo'shilganini sezmasdi va xato jimgina yashirin qolardi.
