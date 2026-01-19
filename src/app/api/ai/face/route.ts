import { NextRequest, NextResponse } from 'next/server';
import { recognizeFace, registerFace } from '@/lib/ai';
import { prisma, findUserByFaceId, createAttendance, checkDuplicateAttendance } from '@/lib/db';

// POST /api/ai/face - Recognize face or register face
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { image, action, userId } = body;

    if (!image) {
      return NextResponse.json(
        { error: 'Image data is required' },
        { status: 400 }
      );
    }

    // Handle registration
    if (action === 'register' && userId) {
      const result = await registerFace(userId, image);

      if (!result.success || !result.faceId) {
        return NextResponse.json(
          { error: result.error || 'Face registration failed' },
          { status: 500 }
        );
      }

      // Update user with faceId
      await prisma.user.update({
        where: { id: userId },
        data: { faceId: result.faceId },
      });

      return NextResponse.json({
        success: true,
        faceId: result.faceId,
        message: 'Face registered successfully',
      });
    }

    // Handle recognition
    const recognitionResult = await recognizeFace(image);

    if (!recognitionResult.success) {
      return NextResponse.json(
        {
          success: false,
          error: recognitionResult.error || 'Face recognition failed',
        },
        { status: 400 }
      );
    }

    // Find user by faceId
    if (recognitionResult.faceId) {
      const user = await findUserByFaceId(recognitionResult.faceId);

      if (user) {
        // Автомат бүртгэл: Хэрэв autoRegister байвал attendance үүсгэх
        const { autoRegister, course, location } = body;
        let attendance = null;
        let isDuplicate = false;

        if (autoRegister === true) {
          // Давхардал шалгах
          const duplicateCheck = await checkDuplicateAttendance(
            user.id,
            course,
            60 // 1 цагийн дотор давхардал шалгах
          );

          if (duplicateCheck.isDuplicate) {
            isDuplicate = true;
            attendance = duplicateCheck.existingAttendance;
          } else {
            // Attendance үүсгэх
            try {
              attendance = await createAttendance({
                userId: user.id,
                studentId: user.role === 'STUDENT' ? user.id : undefined,
                type: 'PRESENT',
                recognizedBy: 'FACE',
                location: location || 'Face Recognition',
                metadata: {
                  course: course || null,
                  confidence: recognitionResult.confidence,
                  faceId: recognitionResult.faceId,
                  autoRegistered: true,
                },
              });
            } catch (error) {
              console.error('Auto attendance creation error:', error);
              // Attendance үүсгэхэд алдаа гарвал user мэдээллийг буцаах
            }
          }
        }

        return NextResponse.json({
          success: true,
          userId: user.id,
          user: {
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role,
          },
          confidence: recognitionResult.confidence,
          faceId: recognitionResult.faceId,
          attendance: attendance
            ? {
                id: attendance.id,
                timestamp: attendance.timestamp,
                isDuplicate,
              }
            : null,
          isDuplicate,
        });
      }
    }

    return NextResponse.json({
      success: false,
      error: 'Face not recognized',
      confidence: recognitionResult.confidence,
    });
  } catch (error) {
    console.error('Face API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/ai/face - Health check
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    service: 'Face Recognition API',
  });
}
