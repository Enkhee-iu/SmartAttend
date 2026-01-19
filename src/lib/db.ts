import { PrismaClient, Prisma } from '@prisma/client';

// PrismaClient instance - singleton pattern
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

// Database connection helper
export async function connectDB() {
  try {
    await prisma.$connect();
    console.log('Database connected successfully');
  } catch (error) {
    console.error('Database connection error:', error);
    throw error;
  }
}

// Database disconnect helper
export async function disconnectDB() {
  await prisma.$disconnect();
}

// Helper functions for common database operations

// User operations
export async function findUserByEmail(email: string) {
  return prisma.user.findUnique({
    where: { email },
    include: { attendances: { take: 10, orderBy: { timestamp: 'desc' } } },
  });
}

export async function findUserByFaceId(faceId: string) {
  return prisma.user.findUnique({
    where: { faceId },
  });
}

export async function findUserByVoiceId(voiceId: string) {
  return prisma.user.findUnique({
    where: { voiceId },
  });
}

// Attendance operations
export async function createAttendance(data: {
  userId: string;
  studentId?: string;
  type?: 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED';
  recognizedBy: 'FACE' | 'VOICE' | 'MANUAL';
  location?: string;
  notes?: string;
  metadata?: Prisma.InputJsonValue;
}) {
  return prisma.attendance.create({
    data: {
      userId: data.userId,
      studentId: data.studentId,
      type: data.type || 'PRESENT',
      recognizedBy: data.recognizedBy,
      location: data.location,
      notes: data.notes,
      metadata: data.metadata,
    },
    include: {
      user: {
        select: {
          id: true,
          name: true,
          email: true,
          role: true,
        },
      },
    },
  });
}

export async function getAttendanceByUserId(userId: string, limit = 50) {
  return prisma.attendance.findMany({
    where: { userId },
    orderBy: { timestamp: 'desc' },
    take: limit,
    include: {
      user: {
        select: {
          id: true,
          name: true,
          email: true,
        },
      },
    },
  });
}

export async function getAttendanceByDateRange(startDate: Date, endDate: Date) {
  return prisma.attendance.findMany({
    where: {
      timestamp: {
        gte: startDate,
        lte: endDate,
      },
    },
    orderBy: { timestamp: 'desc' },
    include: {
      user: {
        select: {
          id: true,
          name: true,
          email: true,
          role: true,
        },
      },
    },
  });
}

// Check for duplicate attendance - нэг оюутан нэг өдөр/цаг дээр олон удаа бүртгэхээс сэргийлэх
export async function checkDuplicateAttendance(
  userId: string,
  course?: string,
  timeWindowMinutes: number = 60 // Default: 1 цагийн дотор давхардал шалгах
) {
  const now = new Date();
  const timeWindowStart = new Date(now.getTime() - timeWindowMinutes * 60 * 1000);

  // Бүх attendance-ийг авч, дараа нь filter хийх (JSON field query нь нарийн байдаг)
  const recentAttendances = await prisma.attendance.findMany({
    where: {
      userId,
      timestamp: {
        gte: timeWindowStart,
        lte: now,
      },
      type: 'PRESENT', // Зөвхөн "Ирсэн" бүртгэлүүдийг шалгах
    },
    orderBy: { timestamp: 'desc' },
  });

  // Хэрэв course байвал metadata-д шалгах
  let existingAttendance = null;
  if (course) {
    existingAttendance = recentAttendances.find((att) => {
      if (att.metadata && typeof att.metadata === 'object' && 'course' in att.metadata) {
        return att.metadata.course === course;
      }
      return false;
    });
  } else {
    // Course байхгүй бол эхний attendance-ийг авна
    existingAttendance = recentAttendances[0] || null;
  }

  return {
    isDuplicate: !!existingAttendance,
    existingAttendance,
  };
}

// Session operations
export async function createSession(data: {
  userId: string;
  token: string;
  type: 'FACE' | 'VOICE' | 'MFA' | 'PASSWORDLESS';
  expiresAt: Date;
}) {
  return prisma.session.create({
    data,
  });
}

export async function findSessionByToken(token: string) {
  return prisma.session.findUnique({
    where: { token },
    include: { user: true },
  });
}

export async function deleteSession(token: string) {
  return prisma.session.delete({
    where: { token },
  });
}

export async function deleteExpiredSessions() {
  return prisma.session.deleteMany({
    where: {
      expiresAt: {
        lt: new Date(),
      },
    },
  });
}
