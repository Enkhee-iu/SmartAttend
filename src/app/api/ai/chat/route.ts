import { NextRequest, NextResponse } from 'next/server';
import { chatWithAI, ChatMessage } from '@/lib/ai';

// POST /api/ai/chat - Chat with AI chatbot
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversationHistory = [] } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Validate conversation history format
    const history: ChatMessage[] = Array.isArray(conversationHistory)
      ? conversationHistory.filter(
          (msg: unknown) =>
            typeof msg === 'object' &&
            msg !== null &&
            'role' in msg &&
            'content' in msg &&
            (msg.role === 'user' || msg.role === 'assistant' || msg.role === 'system')
        )
      : [];

    // Call chatbot
    const result = await chatWithAI(message, history);

    if (!result.success) {
      return NextResponse.json(
        {
          success: false,
          error: result.error || 'Chat failed',
        },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: result.message,
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/ai/chat - Health check
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    service: 'AI Chatbot API (GROQ)',
    configured: !!process.env.GROQ_API_KEY,
    model: process.env.GROQ_MODEL || 'llama-3.1-70b-versatile',
  });
}
