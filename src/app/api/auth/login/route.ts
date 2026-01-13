import { NextRequest, NextResponse } from 'next/server';
import {
  authenticateWithFace,
  authenticateWithVoice,
  initiatePasswordlessAuth,
  verifyPasswordlessCode,
  verifyMFA,
} from '@/lib/auth';
import { prisma } from '@/lib/db';

// POST /api/auth/login - Authenticate user
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { method, image, audio, email, code, userId, mfaCode } = body;

    // Face authentication
    if (method === 'face' && image) {
      const result = await authenticateWithFace(image);

      if (!result.success) {
        return NextResponse.json(
          { error: result.error || 'Face authentication failed' },
          { status: 401 }
        );
      }

      return NextResponse.json({
        success: true,
        token: result.token,
        userId: result.userId,
        method: 'face',
      });
    }

    // Voice authentication
    if (method === 'voice' && audio) {
      const result = await authenticateWithVoice(audio);

      if (!result.success) {
        return NextResponse.json(
          { error: result.error || 'Voice authentication failed' },
          { status: 401 }
        );
      }

      return NextResponse.json({
        success: true,
        token: result.token,
        userId: result.userId,
        method: 'voice',
      });
    }

    // Passwordless authentication - initiate
    if (method === 'passwordless' && email && !code) {
      const result = await initiatePasswordlessAuth(email);

      if (!result.success) {
        return NextResponse.json(
          { error: result.error || 'Failed to initiate authentication' },
          { status: 500 }
        );
      }

      // In production, code should be sent via email/SMS, not returned
      return NextResponse.json({
        success: true,
        message: 'Authentication code sent',
        // Remove code in production!
        code: process.env.NODE_ENV === 'development' ? result.code : undefined,
      });
    }

    // Passwordless authentication - verify
    if (method === 'passwordless' && email && code) {
      const result = await verifyPasswordlessCode(email, code);

      if (!result.success) {
        return NextResponse.json(
          { error: result.error || 'Invalid code' },
          { status: 401 }
        );
      }

      return NextResponse.json({
        success: true,
        token: result.token,
        userId: result.userId,
        method: 'passwordless',
      });
    }

    // MFA verification
    if (method === 'mfa' && userId && mfaCode) {
      const result = await verifyMFA(userId, mfaCode);

      if (!result.success) {
        return NextResponse.json(
          { error: result.error || 'MFA verification failed' },
          { status: 401 }
        );
      }

      return NextResponse.json({
        success: true,
        token: result.token,
        userId,
        method: 'mfa',
      });
    }

    return NextResponse.json(
      {
        error: 'Invalid authentication method or missing parameters',
        supportedMethods: ['face', 'voice', 'passwordless', 'mfa'],
      },
      { status: 400 }
    );
  } catch (error) {
    console.error('Login API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/auth/login - Get authentication status
export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization');
    const token = authHeader?.replace('Bearer ', '');

    if (!token) {
      return NextResponse.json({
        authenticated: false,
        message: 'No token provided',
      });
    }

    const { verifySession } = await import('@/lib/auth');
    const session = await verifySession(token);

    if (!session.valid) {
      return NextResponse.json({
        authenticated: false,
        error: session.error,
      });
    }

    const user = await prisma.user.findUnique({
      where: { id: session.userId },
      select: {
        id: true,
        email: true,
        name: true,
        role: true,
        mfaEnabled: true,
      },
    });

    return NextResponse.json({
      authenticated: true,
      user,
    });
  } catch (error) {
    console.error('Auth status check error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
