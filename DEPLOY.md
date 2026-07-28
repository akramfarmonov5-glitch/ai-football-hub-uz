# Deploy: Neon + Render + Vercel

Uch qism: baza (Neon), backend (Render), frontend (Vercel).
Tartib muhim — har biri oldingisining manzilini talab qiladi.

---

## 1. Neon (PostgreSQL)

1. [neon.tech](https://neon.tech) da loyiha yarating (bepul tarif yetarli)
2. Region: **Frankfurt** yoki **Europe** — Render bilan bir mintaqada bo'lsa
   so'rovlar tezroq bo'ladi
3. "Connection string" ni nusxalang. U shunday ko'rinishda bo'ladi:

```
postgresql://user:parol@ep-xxx-yyy.eu-central-1.aws.neon.tech/neondb?sslmode=require
```

Satrni **o'zgartirmasdan** nusxalang — `sslmode` va `channel_binding`
parametrlari kod tomonidan to'g'ri ishlanadi (`app/core/database.py`).

> Migratsiyalar ilova ishga tushganda avtomatik qo'llanadi — qo'lda hech
> narsa qilish shart emas.

---

## 2. Render (backend)

Repozitoriyda `render.yaml` bor, shuning uchun Blueprint orqali:

1. Render → **New +** → **Blueprint** → `ai-football-hub-uz` repozitoriysini tanlang
2. Render `render.yaml` ni o'qib servisni o'zi sozlaydi
3. Quyidagi maxfiy qiymatlarni **qo'lda** kiriting (ular repoda yo'q):

| O'zgaruvchi | Qiymat |
|---|---|
| `DATABASE_URL` | Neon ulanish satri (1-qadamdan) |
| `BACKEND_CORS_ORIGINS` | `["https://SIZNING-DOMEN.vercel.app"]` |
| `PUBLIC_SITE_URL` | `https://SIZNING-DOMEN.vercel.app` |
| `GEMINI_API_KEY` | Gemini kaliti (ixtiyoriy) |
| `TELEGRAM_BOT_TOKEN` | Bot tokeni (ixtiyoriy) |

`ADMIN_TOKEN` va `SECRET_KEY` Render tomonidan avtomatik yaratiladi —
`ADMIN_TOKEN` ni admin panelga kirish uchun panel'dan ko'chirib oling.

> **Vercel domeni hali yo'q.** Avval bo'sh qiymat bilan deploy qiling,
> Vercel domeni ma'lum bo'lgach `BACKEND_CORS_ORIGINS` va `PUBLIC_SITE_URL`
> ni yangilang. Busiz brauzer CORS xatosi beradi.

Deploy tugagach tekshiring:

```bash
curl https://futbol-backend.onrender.com/health
```

Kutilgan javob: `{"status":"ok","database":"ok",...}`

### Bepul tarif haqida

Render bepul tarifida servis 15 daqiqa faoliyatsizlikdan keyin **uxlaydi**.
Birinchi so'rov 30-50 soniya kutadi. Bu fon vazifasini ham to'xtatadi —
ma'lumot faqat kimdir saytga kirganda yangilanadi.

---

## 3. Vercel (frontend)

1. Vercel → **Add New** → **Project** → shu repozitoriyni import qiling
2. **Root Directory**: `frontend` (muhim — aks holda build topilmaydi)
3. Framework: Next.js (o'zi aniqlaydi)
4. Environment Variables:

| O'zgaruvchi | Qiymat |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://futbol-backend.onrender.com` |
| `NEXT_PUBLIC_WS_URL` | `wss://futbol-backend.onrender.com/ws` |
| `NEXT_PUBLIC_SITE_URL` | `https://SIZNING-DOMEN.vercel.app` |
| `NEXT_PUBLIC_TELEGRAM_BOT_URL` | `https://t.me/bot_nomi` (ixtiyoriy) |

> `wss://` — `ws://` emas. HTTPS sahifadan himoyalanmagan WebSocket'ga
> ulanib bo'lmaydi, brauzer bloklaydi.

> Bu qiymatlar build paytida kodga joylashadi. O'zgartirsangiz **qayta
> deploy** qilish kerak.

---

## 4. Domenlar aniq bo'lgach

Render'ga qaytib `BACKEND_CORS_ORIGINS` va `PUBLIC_SITE_URL` ni haqiqiy
Vercel domeni bilan yangilang, so'ng servisni qayta ishga tushiring.

Tekshirish:

```bash
# Sayt ochiladimi va kontent HTML ichidami (SEO)
curl -s https://SIZNING-DOMEN.vercel.app | grep -c "O&#x27;yin Markazi"

# Metadata to'g'ri domenni ko'rsatyaptimi
curl -s https://SIZNING-DOMEN.vercel.app | grep canonical

# Sitemap
curl -s https://SIZNING-DOMEN.vercel.app/sitemap.xml | head -5
```

---

## Nimalar avtomatik

* **Migratsiyalar** — ilova ishga tushganda (`app/core/migrations.py`)
* **Ma'lumot sinxronizatsiyasi** — 10 daqiqada bir (TheSportsDB)
* **AI tarjimalar, o'yinoldi tahlillari, yangiliklar** — fon vazifasida
* **CI** — har push'da testlar, build va Docker image'lari tekshiriladi

## Nimalarga e'tibor kerak

* **TheSportsDB kaliti `"3"`** — ochiq sinov kaliti, hammaga umumiy.
  Cheklanib qolsa [thesportsdb.com](https://www.thesportsdb.com) dan
  o'zingizniki oling va `SPORTSDB_API_KEY` ni yangilang.
* **Neon bepul tarifi** bir muddat faoliyatsizlikdan keyin bazani uxlatadi.
  `pool_pre_ping` yoqilgan, shuning uchun ilova o'zi qayta ulanadi.
* **Baza zaxirasi** — Neon bepul tarifida cheklangan. Muhim ma'lumot
  paydo bo'lgach zaxira rejasini o'ylash kerak.
