# Environment Variables Setup Guide
# .env файл тохируулах заавар

## Алхам 1: .env файл үүсгэх

`.env.example` файлыг хуулж `.env` гэж нэрлэнэ үү:

```bash
cp .env.example .env
```

Эсвэл Windows PowerShell дээр:
```powershell
Copy-Item .env.example .env
```

## Алхам 2: Бодит утгуудыг оруулах

`.env` файлыг нээж, доорх утгуудыг өөрийн системд тохируулна уу:

### ШААРДЛАГАТАЙ (MUST):

1. **DATABASE_URL**
   - PostgreSQL database connection string (Prisma connection pooling)
   - Format: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE?schema=public`
   - Жишээ: `postgresql://postgres:mypassword@localhost:5432/smartattend?schema=public`

2. **DIRECT_URL**
   - Direct database connection URL (Prisma connection pooling-д ашиглана)
   - Ихэвчлэн DATABASE_URL-тай ижил байна
   - Format: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE?schema=public`
   - Жишээ: `postgresql://postgres:mypassword@localhost:5432/smartattend?schema=public`

### СОНГОХ (OPTIONAL):

2. **LUXAND_API_TOKEN** (Recommended)
   - Luxand Cloud API token for face recognition
   - Sign up at https://luxand.cloud/ to get your API token
   - Хэрэв тохируулаагүй бол `AI_API_KEY` ашиглана (backward compatibility)
   - Хэрэв хоёулаа тохируулаагүй бол mock mode ажиллана

3. **AI_API_KEY** (Legacy - use LUXAND_API_TOKEN instead)
   - AI Face Recognition API key (fallback for LUXAND_API_TOKEN)
   - Хэрэв `LUXAND_API_TOKEN` байхгүй бол энийг ашиглана

4. **LUXAND_COLLECTION** (Optional)
   - Luxand collection name for organizing persons
   - Хэрэв тохируулаагүй бол collection ашиглахгүй

5. **N8N_WEBHOOK_URL**
   - N8N webhook URL
   - Attendance бүртгэл хийгдсэн үед N8N workflow trigger хийхэд ашиглана

6. **N8N_WEBHOOK_SECRET**
   - N8N webhook security secret
   - Webhook security-д ашиглана

7. **NEXT_PUBLIC_API_URL**
   - Public API URL
   - Default: `http://localhost:3000`
   - Production-д өөрийн domain URL-аа оруулна

## Жишээ .env файл:

```env
# Database (ШААРДЛАГАТАЙ)
DATABASE_URL="postgresql://postgres:password123@localhost:5432/smartattend?schema=public"
DIRECT_URL="postgresql://postgres:password123@localhost:5432/smartattend?schema=public"

# AI Configuration (СОНГОХ)
# AI_API_KEY="sk-1234567890abcdef"
# AI_FACE_API_URL="https://api.your-ai-service.com/face/recognize"

# N8N Configuration (СОНГОХ)
# N8N_WEBHOOK_URL="https://n8n.yourdomain.com/webhook/attendance"
# N8N_WEBHOOK_SECRET="your-secret-key-here"

# Next.js Configuration
NEXT_PUBLIC_API_URL="http://localhost:3000"
```

## Анхааруулга:

- ⚠️ `.env` файлыг хэзээ ч git-д commit хийхгүй!
- ⚠️ Production environment-д бодит API keys, passwords ашиглана
- ⚠️ Development-д mock mode ашиглах боломжтой (AI_API_KEY тохируулахгүй)

## Database Setup:

1. PostgreSQL database үүсгэх:
```sql
CREATE DATABASE smartattend;
```

2. Prisma migrate ажиллуулах:
```bash
npm run db:migrate
```

3. Prisma client generate:
```bash
npm run db:generate
```
