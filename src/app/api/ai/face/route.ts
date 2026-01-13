import { NextRequest, NextResponse } from 'next/server';
import { recognizeFace, registerFace } from '@/lib/ai';
import { prisma, findUserByFaceId } from '@/lib/db';

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
