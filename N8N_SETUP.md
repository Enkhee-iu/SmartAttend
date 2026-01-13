# N8N Automation Setup Guide
# N8N Automation тохируулах заавар

## N8N Workflow Import

### 1. N8N Instance үүсгэх

N8N-ийг дараах аргуудаар суулгаж болно:

**Option 1: Docker (Recommended)**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Option 2: NPM**
```bash
npm install n8n -g
n8n start
```

**Option 3: N8N Cloud**
- https://n8n.io/cloud дээр бүртгүүлэх

### 2. Workflow Import хийх

1. N8N UI нээх (http://localhost:5678)
2. "Workflows" → "Import from File"
3. `n8n/workflows/attendance.json` файлыг сонгох
4. Workflow import хийх

### 3. Webhook URL авах

1. Import хийсэн workflow-ийг нээх
2. "Webhook" node-ийг сонгох
3. "Execute Workflow" дарж workflow-ийг идэвхжүүлэх
4. Webhook URL-ийг хуулж авах
   - Жишээ: `http://localhost:5678/webhook/attendance`

### 4. Environment Variables тохируулах

`.env` файлд N8N webhook URL нэмэх:

```env
N8N_WEBHOOK_URL="http://localhost:5678/webhook/attendance"
N8N_WEBHOOK_SECRET="your-secret-key-here"  # Optional
```

### 5. Email Configuration (Optional)

Email илгээхийн тулд SMTP тохируулах:

1. N8N workflow-д "Send Email" node-ийг нээх
2. SMTP settings тохируулах:
   - Host: smtp.gmail.com (Gmail)
   - Port: 587
   - User: your-email@gmail.com
   - Password: app password
3. To email хаягийг тохируулах

**Gmail App Password үүсгэх:**
1. Google Account → Security
2. 2-Step Verification идэвхжүүлэх
3. App passwords үүсгэх
4. Password-ийг N8N-д оруулах

## Workflow Structure

```
Webhook (POST /webhook/attendance)
  ↓
Check Event Type (if event === "attendance.created")
  ↓
Extract Data (attendanceId, userId, type, timestamp)
  ↓
Send Email (Notification)
  ↓
Respond to Webhook (Success response)
```

## Customization Options

### 1. Slack Notification нэмэх

1. Slack node нэмэх
2. Slack Webhook URL тохируулах
3. Message формат тохируулах

### 2. Telegram Bot нэмэх

1. Telegram node нэмэх
2. Bot token оруулах
3. Chat ID тохируулах

### 3. Database Logging нэмэх

1. Database node нэмэх (MySQL, PostgreSQL, MongoDB)
2. Connection тохируулах
3. SQL query/Insert тохируулах

### 4. Conditional Logic нэмэх

- `type === "ABSENT"` үед утас дуудах
- `type === "LATE"` үед warning илгээх
- Time-based logic (өдрийн эхэнд/төгсгөлд report)

## Webhook Payload Format

N8N webhook-д ирэх data формат:

```json
{
  "event": "attendance.created",
  "data": {
    "attendanceId": "attendance_id",
    "userId": "user_id",
    "studentId": "STU001",
    "type": "PRESENT",
    "timestamp": "2024-01-13T10:00:00Z"
  },
  "timestamp": "2024-01-13T10:00:00Z",
  "source": "smartattend-api"
}
```

## Testing

### Manual Test:

```bash
curl -X POST http://localhost:5678/webhook/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "event": "attendance.created",
    "data": {
      "attendanceId": "test-id",
      "userId": "test-user",
      "studentId": "STU001",
      "type": "PRESENT",
      "timestamp": "2024-01-13T10:00:00Z"
    }
  }'
```

### Integration Test:

1. SmartAttend системд бүртгэл хийх
2. N8N workflow-ийг execute хийх
3. Email/Notification ирэх эсэхийг шалгах

## Troubleshooting

### Webhook хүлээн авахгүй байна:
- N8N_WEBHOOK_URL зөв эсэхийг шалгах
- Workflow active эсэхийг шалгах
- Firewall/Network settings шалгах

### Email илгээгдэхгүй байна:
- SMTP settings зөв эсэхийг шалгах
- App password зөв эсэхийг шалгах (Gmail)
- N8N logs шалгах

## Additional Resources

- N8N Documentation: https://docs.n8n.io/
- N8N Community: https://community.n8n.io/
- Workflow Examples: https://n8n.io/workflows/
