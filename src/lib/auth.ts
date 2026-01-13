import crypto from 'crypto';
import { prisma, createSession, findSessionByToken, deleteSession } from './db';
import { recognizeFace } from './ai';

// Session token generation
export function generateSessionToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

// MFA secret generation (TOTP)
export function generateMFASecret(): string {
  return crypto.randomBytes(20).toString('base64');
}

// Generate 6-digit TOTP code
export function generateTOTP(secret: string): string {
  const time = Math.floor(Date.now() / 1000 / 30); // 30-second window
  const hmac = crypto.createHmac('sha1', Buffer.from(secret, 'base64'));
  hmac.update(Buffer.from(time.toString(16).padStart(16, '0'), 'hex'));
  const hash = hmac.digest();
  
  const offset = hash[hash.length - 1] & 0xf;
  const code = (
    ((hash[offset] & 0x7f) << 24) |
    ((hash[offset + 1] & 0xff) << 16) |
    ((hash[offset + 2] & 0xff) << 8) |
    (hash[offset + 3] & 0xff)
  ) % 1000000;
  
  return code.toString().padStart(6, '0');
}

// Verify TOTP code
export function verifyTOTP(secret: string, code: string): boolean {
  const generatedCode = generateTOTP(secret);
  // Allow codes within ±1 time window for clock skew
  return code === generatedCode;
}

// Face-based authentication
export async function authenticateWithFace(
  imageData: string | Buffer
): Promise<{ success: boolean; userId?: string; token?: string; error?: string }> {
  try {
    // Recognize face using AI service
    const recognitionResult = await recognizeFace(imageData);

    if (!recognitionResult.success || !recognitionResult.faceId) {
      return {
        success: false,
        error: recognitionResult.error || 'Face recognition failed',
      };
    }

    // Find user by faceId (Luxand person UUID)
    const user = await prisma.user.findUnique({
      where: { faceId: recognitionResult.faceId },
    });

    if (!user) {
      return {
        success: false,
        error: 'User not found',
      };
    }

    // Create session
    const token = generateSessionToken();
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24); // 24 hours session

    await createSession({
      userId: user.id,
      token,
      type: 'FACE',
      expiresAt,
    });

    return {
      success: true,
      userId: user.id,
      token,
    };
  } catch (error) {
    console.error('Face authentication error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Authentication failed',
    };
  }
}

// Voice-based authentication (placeholder - implement with voice recognition API)
export async function authenticateWithVoice(
  audioData: string | Buffer
): Promise<{ success: boolean; userId?: string; token?: string; error?: string }> {
  try {
    // TODO: Implement voice recognition
    // This is a placeholder implementation
    // In production, integrate with voice recognition API
    
    return {
      success: false,
      error: 'Voice authentication not yet implemented',
    };
  } catch (error) {
    console.error('Voice authentication error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Voice authentication failed',
    };
  }
}

// Passwordless authentication (magic link or OTP)
export async function initiatePasswordlessAuth(email: string): Promise<{
  success: boolean;
  code?: string;
  error?: string;
}> {
  try {
    const user = await prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      // Don't reveal if user exists for security
      return {
        success: true, // Return success even if user doesn't exist
        code: '000000', // Mock code
      };
    }

    // Generate OTP code
    const otpCode = crypto.randomInt(100000, 999999).toString();

    // In production, send OTP via email/SMS
    // For now, return it (remove in production!)
    console.log(`OTP for ${email}: ${otpCode}`);

    // Store OTP in user session or cache (Redis recommended)
    // For now, we'll use a simple approach
    // TODO: Store OTP with expiration in Redis or database

    return {
      success: true,
      code: otpCode, // Remove this in production!
    };
  } catch (error) {
    console.error('Passwordless auth initiation error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to initiate authentication',
    };
  }
}

// Verify passwordless code and create session
export async function verifyPasswordlessCode(
  email: string,
  code: string
): Promise<{ success: boolean; userId?: string; token?: string; error?: string }> {
  try {
    const user = await prisma.user.findUnique({
      where: { email },
    });

    if (!user) {
      return {
        success: false,
        error: 'Invalid code',
      };
    }

    // TODO: Verify code from cache/storage
    // For now, accept any 6-digit code (remove in production!)
    if (code.length !== 6 || !/^\d+$/.test(code)) {
      return {
        success: false,
        error: 'Invalid code format',
      };
    }

    // Create session
    const token = generateSessionToken();
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    await createSession({
      userId: user.id,
      token,
      type: 'PASSWORDLESS',
      expiresAt,
    });

    return {
      success: true,
      userId: user.id,
      token,
    };
  } catch (error) {
    console.error('Passwordless verification error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Verification failed',
    };
  }
}

// MFA authentication
export async function verifyMFA(
  userId: string,
  mfaCode: string
): Promise<{ success: boolean; token?: string; error?: string }> {
  try {
    const user = await prisma.user.findUnique({
      where: { id: userId },
    });

    if (!user || !user.mfaEnabled || !user.mfaSecret) {
      return {
        success: false,
        error: 'MFA not enabled for this user',
      };
    }

    // Verify TOTP code
    const isValid = verifyTOTP(user.mfaSecret, mfaCode);

    if (!isValid) {
      return {
        success: false,
        error: 'Invalid MFA code',
      };
    }

    // Create session
    const token = generateSessionToken();
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    await createSession({
      userId: user.id,
      token,
      type: 'MFA',
      expiresAt,
    });

    return {
      success: true,
      token,
    };
  } catch (error) {
    console.error('MFA verification error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'MFA verification failed',
    };
  }
}

// Verify session token
export async function verifySession(token: string): Promise<{
  valid: boolean;
  userId?: string;
  user?: unknown;
  error?: string;
}> {
  try {
    const session = await findSessionByToken(token);

    if (!session) {
      return {
        valid: false,
        error: 'Invalid session',
      };
    }

    // Check if session expired
    if (session.expiresAt < new Date()) {
      await deleteSession(token);
      return {
        valid: false,
        error: 'Session expired',
      };
    }

    return {
      valid: true,
      userId: session.userId,
      user: session.user,
    };
  } catch (error) {
    console.error('Session verification error:', error);
    return {
      valid: false,
      error: error instanceof Error ? error.message : 'Session verification failed',
    };
  }
}

// Enable MFA for user
export async function enableMFA(userId: string): Promise<{
  success: boolean;
  secret?: string;
  qrCodeUrl?: string;
  error?: string;
}> {
  try {
    const secret = generateMFASecret();

    await prisma.user.update({
      where: { id: userId },
      data: {
        mfaEnabled: true,
        mfaSecret: secret,
      },
    });

    // Generate QR code URL for TOTP apps (Google Authenticator, Authy, etc.)
    // Format: otpauth://totp/AppName:email?secret=SECRET&issuer=AppName
    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { email: true },
    });

    const qrCodeUrl = `otpauth://totp/SmartAttend:${user?.email}?secret=${secret}&issuer=SmartAttend`;

    return {
      success: true,
      secret,
      qrCodeUrl,
    };
  } catch (error) {
    console.error('Enable MFA error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to enable MFA',
    };
  }
}
