# SmartAttend System Architecture
# Оюутны AI таних системийн бүтэц

Энэхүү систем нь зурагт заасан requirements-уудыг ашиглан бүтээгдсэн бөгөөд доорх бүтцийг агуулна:

## 1. CI/CD Бүтэц (CI/CD Structure)

### GitHub Actions Workflow
```
.github/
  └── workflows/
      ├── ci.yml          # Lint + Build + Preview
      └── cd.yml          # Production Deployment
```

**CI Pipeline (Lint + Build + Preview):**
- **Lint**: ESLint ашиглан code quality шалгах
- **Build**: Next.js production build
- **Preview**: Vercel preview deployment

**CD Pipeline (Production):**
- **Production Deployment**: Main branch дээр automataar deploy

### Файлууд:
- `eslint.config.mjs` - ESLint тохиргоо
- `package.json` - Build scripts (`lint`, `build`, `start`)
- `.github/workflows/ci.yml` - CI workflow
- `.github/workflows/cd.yml` - CD workflow

## 2. AI Бүтэц (AI Structure)

### Face Recognition (Нүүр таних)
```
src/app/api/ai/
  └── face/
      └── route.ts        # Face recognition API endpoint

components/
  └── FaceCamera.tsx      # Camera component for face capture

lib/
  └── ai.ts               # AI service functions
```

**Ажиллах механизм:**
1. Камерын компонент (`FaceCamera.tsx`) нүүрний зураг авах
2. `/api/ai/face` endpoint руу илгээх
3. AI service (`lib/ai.ts`) таних
4. Үр дүнг буцаах

## 3. Automation - N8N Integration

### N8N Workflow
```
n8n/
  └── workflows/
      └── attendance.json # Attendance automation workflow

src/app/api/webhook/
  └── n8n/
      └── route.ts        # N8N webhook endpoint
```

**Ажиллах механизм:**
1. Attendance бүртгэл хийгдсэн үед webhook trigger
2. N8N workflow ажиллаж эхлэх
3. Automation хийгдэх (email, notification, гэх мэт)

## 4. Database Бүтэц (SQL/Prisma)

### Prisma Schema
```
prisma/
  ├── schema.prisma       # Database schema definition
  └── seed.ts             # Seed data

lib/
  └── db.ts               # Database connection & utilities
```

**Хэрэглээ:**
- Prisma ORM ашиглах
- SQL database (PostgreSQL/MySQL)
- Type-safe database access

## 5. Back-end API Structure (Next.js API Routes)

### API Endpoints
```
src/app/api/
  ├── ai/
  │   └── face/
  │       └── route.ts          # AI face recognition
  ├── attendance/
  │   └── route.ts              # Attendance recording
  ├── auth/
  │   └── login/
  │       └── route.ts          # Authentication
  ├── reports/
  │   └── route.ts              # Reports generation
  └── webhook/
      └── n8n/
          └── route.ts          # N8N integration
```

**API-ууд:**
- `/api/ai/face` - Нүүр таних
- `/api/attendance` - Бүртгэл хийх
- `/api/auth/login` - Нэвтрэх
- `/api/reports` - Тайлан гаргах
- `/api/webhook/n8n` - N8N automation

## 6. Authentication Бүтэц

### Auth Structure
```
src/app/(auth)/
  ├── login/
  │   └── page.tsx        # Login page
  └── register/
      └── page.tsx        # Register page

lib/
  └── auth.ts             # Authentication utilities
```

**Аутентикацийн төрлүүд (Requirements-оос):**
1. **Face/Voice Login** - AI ашиглан нэвтрэх
2. **MFA (2FA)** - Two-factor authentication
3. **Passwordless Auth** - Нууц үггүй нэвтрэх

## 7. Front-end Structure

### Pages & Components
```
src/app/
  ├── (auth)/             # Authentication routes
  ├── dashboard/          # Dashboard page
  ├── api/                # API routes
  ├── layout.tsx          # Root layout
  └── page.tsx            # Home page

components/
  ├── FaceCamera.tsx      # Camera component
  └── ui/                 # UI components
```

## 8. Testing Structure

```
tests/
  ├── api.test.ts         # API tests
  ├── attendance.test.ts  # Attendance tests
  └── auth.test.ts        # Auth tests
```

## 9. Configuration Files

```
├── next.config.ts        # Next.js configuration
├── tsconfig.json         # TypeScript configuration
├── eslint.config.mjs     # ESLint configuration
├── postcss.config.mjs    # PostCSS configuration
└── package.json          # Dependencies & scripts
```

## System Flow (Системийн урсгал)

### Attendance Recording Process:
1. **Camera Capture** → `FaceCamera.tsx` компонент камерын зураг авах
2. **Face Recognition** → `/api/ai/face` endpoint AI таних
3. **Attendance Record** → `/api/attendance` endpoint бүртгэл хийх
4. **Database Save** → Prisma ашиглан database-д хадгалах
5. **N8N Trigger** → `/api/webhook/n8n` endpoint automation trigger
6. **Automation** → N8N workflow ажиллаж (email, notification, гэх мэт)

## Technology Stack Summary

- **Framework**: Next.js 16 (App Router)
- **Database**: SQL (Prisma ORM)
- **AI**: Face Recognition API
- **Automation**: N8N
- **CI/CD**: GitHub Actions + Vercel
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Testing**: Jest/Vitest

## Requirements Compliance

✅ **CI**: Preview, Lint, Build (MUST)
✅ **CD**: Production Deployment (MUST)
✅ **AI**: Face Recognition (ONE OR MORE)
✅ **Automation**: N8N (MUST)
✅ **Database**: SQL (MUST)
✅ **Back-end**: Next.js API (MUST)
✅ **Authentication**: Face/Voice login, MFA, Passwordless (MUST)
