# Backend API Documentation
# SmartAttend System - API Endpoints

## Бүтэц (Structure)

```
src/app/api/
├── ai/
│   └── face/
│       └── route.ts          # Face Recognition API
├── attendance/
│   └── route.ts              # Attendance Management API
├── auth/
│   ├── login/
│   │   └── route.ts          # Authentication API
│   └── register/
│       └── route.ts          # User Registration API
├── reports/
│   └── route.ts              # Reports API
└── webhook/
    └── n8n/
        └── route.ts          # N8N Automation Webhook
```

## API Endpoints

### 1. AI Face Recognition API

**Endpoint:** `POST /api/ai/face`

**Функц:**
- Нүүр таних (Face Recognition)
- Нүүр бүртгэх (Face Registration)

**Request:**
```json
{
  "image": "base64_image_data",
  "action": "register",  // optional: "register" or recognition
  "userId": "user_id"    // required for registration
}
```

**Response (Recognition):**
```json
{
  "success": true,
  "userId": "user_id",
  "user": {
    "id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "role": "STUDENT"
  },
  "confidence": 0.95,
  "faceId": "luxand_person_uuid"
}
```

**Response (Registration):**
```json
{
  "success": true,
  "faceId": "luxand_person_uuid",
  "message": "Face registered successfully"
}
```

**Health Check:** `GET /api/ai/face`
```json
{
  "status": "ok",
  "service": "Face Recognition API"
}
```

---

### 2. Authentication API

**Endpoint:** `POST /api/auth/login`

**Функц:**
- Face Authentication (Нүүр таних)
- Voice Authentication (Дуу таних)
- Passwordless Authentication (Нууц үггүй)
- MFA Verification (2FA)

**Request (Face):**
```json
{
  "method": "face",
  "image": "base64_image_data"
}
```

**Request (Passwordless - Initiate):**
```json
{
  "method": "passwordless",
  "email": "user@example.com"
}
```

**Request (Passwordless - Verify):**
```json
{
  "method": "passwordless",
  "email": "user@example.com",
  "code": "123456"
}
```

**Request (MFA):**
```json
{
  "method": "mfa",
  "userId": "user_id",
  "mfaCode": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "token": "session_token",
  "userId": "user_id",
  "method": "face"
}
```

**Auth Status:** `GET /api/auth/login`
- Headers: `Authorization: Bearer <token>`

---

### 3. User Registration API

**Endpoint:** `POST /api/auth/register`

**Функц:**
- Шинэ хэрэглэгч бүртгэх

**Request:**
```json
{
  "name": "User Name",
  "email": "user@example.com",
  "role": "STUDENT"  // STUDENT, TEACHER, ADMIN
}
```

**Response:**
```json
{
  "success": true,
  "userId": "user_id",
  "user": {
    "id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "role": "STUDENT"
  }
}
```

---

### 4. Attendance API

**Endpoint:** `POST /api/attendance`

**Функц:**
- Бүртгэл хийх (Record Attendance)

**Headers:**
```
Authorization: Bearer <session_token>
```

**Request:**
```json
{
  "studentId": "STU001",  // optional
  "type": "PRESENT",      // PRESENT, ABSENT, LATE, EXCUSED
  "recognizedBy": "FACE", // FACE, VOICE, MANUAL
  "location": "Room 101", // optional
  "notes": "Notes",       // optional
  "metadata": {}          // optional
}
```

**Response:**
```json
{
  "success": true,
  "attendance": {
    "id": "attendance_id",
    "userId": "user_id",
    "studentId": "STU001",
    "type": "PRESENT",
    "recognizedBy": "FACE",
    "location": "Room 101",
    "timestamp": "2024-01-13T10:00:00Z",
    "user": {
      "id": "user_id",
      "name": "User Name",
      "email": "user@example.com",
      "role": "STUDENT"
    }
  }
}
```

**Get Attendance:** `GET /api/attendance`

**Query Parameters:**
- `userId` - User ID (optional, defaults to authenticated user)
- `startDate` - Start date (optional)
- `endDate` - End date (optional)
- `limit` - Limit results (optional, default: 50)

**Response:**
```json
{
  "success": true,
  "count": 10,
  "attendances": [...]
}
```

---

### 5. Reports API

**Endpoint:** `GET /api/reports`

**Функц:**
- Тайлан гаргах (Generate Reports)

*Note: Implementation pending*

---

### 6. N8N Webhook API

**Endpoint:** `POST /api/webhook/n8n`

**Функц:**
- N8N automation-д event илгээх
- Attendance бүртгэл хийгдсэн үед автоматаар trigger хийх

**Request:**
```json
{
  "event": "attendance.created",
  "data": {
    "attendanceId": "attendance_id",
    "userId": "user_id",
    "studentId": "STU001",
    "type": "PRESENT",
    "timestamp": "2024-01-13T10:00:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Webhook forwarded to N8N",
  "n8nResponse": {}
}
```

**Health Check:** `GET /api/webhook/n8n`
```json
{
  "status": "ok",
  "service": "N8N Webhook API",
  "configured": true,
  "webhookUrl": "configured"
}
```

---

## Libraries (src/lib/)

### `src/lib/ai.ts`
- `recognizeFace()` - Luxand Cloud API ашиглан нүүр таних
- `registerFace()` - Luxand Cloud API ашиглан нүүр бүртгэх
- `addFaceToPerson()` - Нэмэлт нүүр нэмэх (илүү нарийвчлал)

### `src/lib/auth.ts`
- `authenticateWithFace()` - Face authentication
- `authenticateWithVoice()` - Voice authentication
- `initiatePasswordlessAuth()` - Passwordless auth эхлүүлэх
- `verifyPasswordlessCode()` - Passwordless code баталгаажуулах
- `verifyMFA()` - MFA verification
- `verifySession()` - Session token баталгаажуулах
- `generateSessionToken()` - Session token үүсгэх
- `enableMFA()` - MFA идэвхжүүлэх

### `src/lib/db.ts`
- `prisma` - Prisma client instance
- `connectDB()` / `disconnectDB()` - Database connection
- `findUserByEmail()` / `findUserByFaceId()` - User operations
- `createAttendance()` - Attendance үүсгэх
- `getAttendanceByUserId()` / `getAttendanceByDateRange()` - Attendance queries
- `createSession()` / `findSessionByToken()` - Session operations

---

## Authentication Flow

1. **Face Login:**
   ```
   Client → POST /api/auth/login (face) 
   → AI Recognition (Luxand)
   → Find User by faceId
   → Create Session
   → Return Token
   ```

2. **Attendance Recording:**
   ```
   Client → POST /api/attendance (with token)
   → Verify Session
   → Create Attendance Record
   → Trigger N8N Webhook (async)
   → Return Attendance Data
   ```

---

## Technology Stack

- **Framework:** Next.js 16 (App Router)
- **API:** Next.js API Routes
- **Database:** PostgreSQL + Prisma ORM
- **AI:** Luxand Cloud API (Face Recognition)
- **Authentication:** Custom Session-based (Face/Voice/MFA/Passwordless)
- **Automation:** N8N Webhooks

---

## Error Responses

**Standard Error Format:**
```json
{
  "error": "Error message",
  "message": "Detailed error message"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error
- `502` - Bad Gateway (N8N webhook failed)
