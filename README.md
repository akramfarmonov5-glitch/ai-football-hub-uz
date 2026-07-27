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

AI tahlillari `GEMINI_API_KEY` bo'lganda Gemini orqali, bo'lmasa o'zbekcha
shablonlar orqali tayyorlanadi — ikkala holatda ham sayt to'liq ishlaydi.

---

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
