import { NextRequest, NextResponse } from 'next/server';
import { createAttendance, getAttendanceByUserId, getAttendanceByDateRange, checkDuplicateAttendance } from '@/lib/db';
import { verifySession } from '@/lib/auth';

// POST /api/attendance - Record attendance
export async function POST(request: NextRequest) {
  try {
    // Verify authentication
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');

    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const session = await verifySession(token);
    if (!session.valid || !session.userId) {
      return NextResponse.json(
        { error: session.error || 'Invalid session' },
        { status: 401 }
      );
    }

    const body = await request.json();
    const { studentId, type, recognizedBy, location, notes, metadata, course, skipDuplicateCheck } = body;

    // Validate required fields
    if (!recognizedBy || !['FACE', 'VOICE', 'MANUAL'].includes(recognizedBy)) {
      return NextResponse.json(
        { error: 'Valid recognition type is required (FACE, VOICE, or MANUAL)' },
        { status: 400 }
      );
    }

    // Давхардал шалгах (хэрэв skipDuplicateCheck байхгүй бол)
    if (!skipDuplicateCheck && (type === 'PRESENT' || !type)) {
      const duplicateCheck = await checkDuplicateAttendance(
        session.userId,
        course || (metadata && typeof metadata === 'object' && 'course' in metadata ? metadata.course : undefined),
        60 // 1 цагийн дотор давхардал шалгах
      );

      if (duplicateCheck.isDuplicate && duplicateCheck.existingAttendance) {
        return NextResponse.json(
          {
            success: false,
            error: 'Давхардсан бүртгэл',
            message: 'Та энэ өдөр/цагт аль хэдийн бүртгэгдсэн байна.',
            existingAttendance: {
              id: duplicateCheck.existingAttendance.id,
              timestamp: duplicateCheck.existingAttendance.timestamp,
              location: duplicateCheck.existingAttendance.location,
            },
            isDuplicate: true,
          },
          { status: 409 } // Conflict status
        );
      }
    }

    // Create attendance record
    const attendance = await createAttendance({
      userId: session.userId,
      studentId: studentId || undefined,
      type: type || 'PRESENT',
      recognizedBy: recognizedBy as 'FACE' | 'VOICE' | 'MANUAL',
      location: location || undefined,
      notes: notes || undefined,
      metadata: {
        ...(metadata || {}),
        ...(course ? { course } : {}),
      },
    });

    // Trigger N8N webhook (async, don't wait for response)
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}/api/webhook/n8n`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event: 'attendance.created',
        data: {
          attendanceId: attendance.id,
          userId: attendance.userId,
          studentId: attendance.studentId,
          type: attendance.type,
          timestamp: attendance.timestamp,
        },
      }),
    }).catch((error) => {
      console.error('N8N webhook error:', error);
    });

    return NextResponse.json({
      success: true,
      attendance: {
        id: attendance.id,
        userId: attendance.userId,
        studentId: attendance.studentId,
        type: attendance.type,
        recognizedBy: attendance.recognizedBy,
        location: attendance.location,
        timestamp: attendance.timestamp,
      },
    });
  } catch (error) {
    console.error('Attendance API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/attendance - Get attendance records
export async function GET(request: NextRequest) {
  try {
    // Verify authentication
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');

    if (!token) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    const session = await verifySession(token);
    if (!session.valid || !session.userId) {
      return NextResponse.json(
        { error: session.error || 'Invalid session' },
        { status: 401 }
      );
    }

    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId') || session.userId;
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    const limit = parseInt(searchParams.get('limit') || '50');

    let attendances;

    if (startDate && endDate) {
      // Get attendance by date range
      attendances = await getAttendanceByDateRange(
        new Date(startDate),
        new Date(endDate)
      );
    } else {
      // Get attendance by user ID
      attendances = await getAttendanceByUserId(userId, limit);
    }

    return NextResponse.json({
      success: true,
      count: attendances.length,
      attendances,
    });
  } catch (error) {
    console.error('Attendance GET API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
