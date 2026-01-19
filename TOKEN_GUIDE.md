# 🔑 Token-ууд - Одоо ямар token авах шаардлагатай вэ?

## 📊 Одоогийн байдал

### ✅ Байгаа token-ууд:
- ✅ `DATABASE_URL` - Neon PostgreSQL (байна)
- ✅ `DIRECT_URL` - Local fallback (засах шаардлагатай)

### ⚠️ Байхгүй token-ууд (Optional):
- ⚠️ `LUXAND_API_TOKEN` - Face Recognition (mock mode ажиллана)
- ⚠️ `GROQ_API_KEY` - Chatbot (mock mode ажиллана)
- ⚠️ `N8N_WEBHOOK_URL` - Automation (алгасна)
- ⚠️ `N8N_WEBHOOK_SECRET` - Automation security (optional)

---

## 🎯 Одоо ямар token авах шаардлагатай вэ?

### ❌ ШААРДЛАГАТАЙ БАЙХГҮЙ

**Одоо application ажиллаж байна:**
- ✅ Database холбогдсон
- ✅ Mock Face Recognition ажиллана
- ✅ Mock Chatbot ажиллана
- ✅ Бүх функцүүд ажиллана

### ✅ СОНГОХ (Optional - илүү сайн ажиллахын тулд)

| Token | Яагаад хэрэгтэй вэ? | Хэрхэн авах вэ? | Ажиллах эсэх (байхгүй бол) |
|-------|---------------------|-----------------|---------------------------|
| **LUXAND_API_TOKEN** | Бодит Face Recognition | https://luxand.cloud/ → API Keys | ✅ Mock mode ажиллана |
| **GROQ_API_KEY** | Бодит AI Chatbot (хурдан) | https://console.groq.com/ → API Keys | ✅ Mock chatbot ажиллана |
| **N8N_WEBHOOK_URL** | Automation trigger | N8N instance → Webhook URL | ✅ Алгасна (error гарахгүй) |

---

## 🔍 Дэлгэрэнгүй тайлбар

### 1. LUXAND_API_TOKEN (Face Recognition)

**Одоогийн байдал:**
- ✅ Mock mode ажиллана
- ✅ Development-д хангалттай
- ⚠️ Бодит face recognition хийхгүй

**Хэрэв token авбал:**
- ✅ Бодит face recognition ажиллана
- ✅ Production-д бодит AI ашиглана

**Хэрхэн авах:**
1. https://luxand.cloud/ дээр бүртгүүлэх
2. Dashboard → API Keys
3. Token үүсгэх
4. `.env` файлд оруулах:
```env
LUXAND_API_TOKEN="your-token-here"
```

**Дүгнэлт:** Одоо хэрэггүй, дараа нь нэмж болно ✅

---

### 2. GROQ_API_KEY (Chatbot)

**Одоогийн байдал:**
- ✅ Mock chatbot ажиллана
- ✅ Keyword-based responses
- ⚠️ Бодит AI chatbot биш

**Хэрэв token авбал:**
- ✅ GROQ API ашиглана (хурдан, хямд)
- ✅ Llama 3.1-70b-versatile model ашиглана
- ✅ Бодит AI responses

**Хэрхэн авах:**
1. https://console.groq.com/ дээр бүртгүүлэх
2. API Keys → Create API Key
3. Token авах
4. `.env` файлд оруулах:
```env
GROQ_API_KEY="gsk_..."
GROQ_MODEL="llama-3.1-70b-versatile"  # Optional, default model
```

**Дүгнэлт:** Одоо хэрэггүй, дараа нь нэмж болно ✅

---

### 3. N8N_WEBHOOK_URL (Automation)

**Одоогийн байдал:**
- ✅ Webhook алгасна
- ✅ Error гарахгүй
- ⚠️ Automation хийхгүй

**Хэрэв token авбал:**
- ✅ N8N workflow trigger хийх
- ✅ Email, notification илгээх

**Дүгнэлт:** Одоо хэрэггүй, дараа нь нэмж болно ✅

---

## ✅ Дүгнэлт

### Одоо token авах шаардлагатай эсэх:

| Асуулт | Хариулт |
|--------|---------|
| **Application ажиллах уу?** | ✅ **ТИЙМ** - Бүх функцүүд ажиллана |
| **Token-ууд шаардлагатай юу?** | ❌ **ҮГҮЙ** - Одоо хэрэггүй |
| **Mock mode ажиллах уу?** | ✅ **ТИЙМ** - Development-д хангалттай |

### Хэзээ token авах вэ?

**Development-д:**
- ❌ Token хэрэггүй
- ✅ Mock mode хангалттай

**Production-д (дараа нь):**
- ✅ `LUXAND_API_TOKEN` - Бодит face recognition
- ✅ `GROQ_API_KEY` - Бодит chatbot (хурдан, хямд)
- ✅ `N8N_WEBHOOK_URL` - Automation

---

## 🎯 Одоогийн зөвлөмж

### Одоо юу хийх вэ:

1. ✅ **Application ажиллуулах** - Token-уудгүйгээр ажиллана
2. ✅ **Development хийх** - Mock mode хангалттай
3. ⚠️ **Token-уудыг дараа нь нэмэх** - Production-д хэрэгтэй

### Хэрэв илүү сайн ажиллуулахыг хүсвэл:

**Хамгийн чухал:**
1. `LUXAND_API_TOKEN` - Бодит face recognition
2. `GROQ_API_KEY` - Бодит chatbot (хурдан, хямд)

**Сонгох:**
3. `N8N_WEBHOOK_URL` - Automation

---

## 📝 Жишээ .env файл (Одоогийн байдал)

```env
# Database (ШААРДЛАГАТАЙ - аль хэдийн байна)
DATABASE_URL="postgresql://neondb_owner:****@ep-green-math-ahcje23v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
DIRECT_URL="postgresql://user:password@localhost:5432/smartattend?schema=public"

# AI (СОНГОХ - байхгүй бол mock mode)
# LUXAND_API_TOKEN="your-luxand-token"
# GROQ_API_KEY="gsk_your-groq-key"
# GROQ_MODEL="llama-3.1-70b-versatile"  # Optional

# N8N (СОНГОХ - байхгүй бол алгасна)
# N8N_WEBHOOK_URL="https://your-n8n.com/webhook"
# N8N_WEBHOOK_SECRET="your-secret"

# Next.js
NEXT_PUBLIC_API_URL="http://localhost:3000"
```

---

## 🎉 Дүгнэлт

**Одоо token авах шаардлагатай эсэх:**
- ❌ **ШААРДЛАГАТАЙ БАЙХГҮЙ**
- ✅ **Application ажиллана** - Token-уудгүйгээр
- ✅ **Mock mode хангалттай** - Development-д

**Дараа нь token авах:**
- Production-д бодит AI ашиглах үед
- Илүү сайн функцүүд хэрэгтэй бол

---

**💡 Зөвлөмж:** Одоо token-уудгүйгээр development хийж, дараа нь production-д token-уудыг нэмэх.
