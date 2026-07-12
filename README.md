# 🔷 NexusPanel

یک پنل مدیریت مدرن و سریع برای مدیریت کاربران و سرویس‌ها، با **داشبورد مدیریتی فارسی**، **ربات مدیریت تلگرام** و قابلیت ساخت لینک‌های اختصاصی با محدودیت ترافیک، سرعت و آی‌پی.

> Fork شده از X4G با بازنویسی کامل (Clean Room Implementation) — بدون شباهت کد به پروژه اصلی

---

## ✨ ویژگی‌ها

- 🔌 **VLESS Relay** روی WebSocket با حداکثر throughput
- 🌐 **XHTTP Transport** با دو حالت packet-up و stream-up (موتور تطبیقی AIMD)
- 📊 **داشبورد مدیریتی فارسی** (آمار، نمودار، لاگ، مدیریت لینک‌ها)
- 🔗 **لینک‌های نامحدود** با محدودیت ترافیک (KB/MB/GB)
- 🚦 **محدودیت سرعت** (Bandwidth Throttling) با الگوی Token Bucket
- ✅ فعال/غیرفعال‌سازی لحظه‌ای هر لینک
- 🗂 **گروه‌های ساب** — چند کانفیگ در یک لینک ساب
- 🤖 **ربات مدیریت تلگرام** (اختیاری)
- 💾 ذخیره‌سازی دائمی با Volume

---

## 🚀 Deploy روی Railway

### ۱. Clone (یا Fork) این ریپازیتوری

```bash
git clone https://github.com/YOUR_USER/NexusPanel.git
```

### ۲. Deploy روی Railway

1. وارد [Railway.app](https://railway.app/) شوید
2. **New Project → Deploy from GitHub repo**
3. ریپازیتوری NexusPanel را انتخاب کنید
4. Railway به صورت خودکار Deploy می‌کند

### ۳. تنظیم دامنه

حتماً یک **Public Domain** از تنظیمات Railway فعال کنید تا متغیر `RAILWAY_PUBLIC_DOMAIN` مقداردهی شود.

### ۴. Volume (دائمی)

برای ذخیره دائمی اطلاعات (کانفیگ‌ها، آمار)، یک **Volume** بسازید و روی مسیر `/data` متصل کنید.

### ۵. متغیرهای محیطی (اختیاری)

| متغیر | توضیح | پیش‌فرض |
|-------|-------|---------|
| `DATA_DIR` | مسیر ذخیره داده‌ها | `/data` |
| `SECRET_KEY` | کلید امنیتی (اختیاری) | خودکار ساخته می‌شود |
| `TELEGRAM_BOT_TOKEN` | توکن ربات تلگرام | — |
| `TELEGRAM_ADMIN_IDS` | آیدی عددی ادمین‌ها (با کاما جدا) | — |

---

## 📱 استفاده

پس از Deploy:

1. به **https://your-app.up.railway.app/** بروید
2. رمز پیش‌فرض: **NEXUSKING**
3. از داشبورد لینک‌های VLESS بسازید و استفاده کنید

### کانفیگ‌های پشتیبانی‌شده

- `vless-ws` — VLESS روی WebSocket
- `xhttp-packet-up` — XHTTP Packet-Up
- `xhttp-stream-up` — XHTTP Stream-Up

---

## 📄 لایسنس

MIT