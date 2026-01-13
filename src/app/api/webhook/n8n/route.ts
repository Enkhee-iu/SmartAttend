import { NextRequest, NextResponse } from 'next/server';

// POST /api/webhook/n8n - N8N webhook endpoint
// This endpoint receives events from the application and forwards them to N8N
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { event, data } = body;

    // Verify webhook secret if configured
    const webhookSecret = request.headers.get('x-webhook-secret');
    const expectedSecret = process.env.N8N_WEBHOOK_SECRET;

    if (expectedSecret && webhookSecret !== expectedSecret) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // N8N webhook URL from environment
    const n8nWebhookUrl = process.env.N8N_WEBHOOK_URL;

    if (!n8nWebhookUrl) {
      console.warn('N8N_WEBHOOK_URL not configured, skipping webhook call');
      return NextResponse.json({
        success: false,
        message: 'N8N webhook URL not configured',
      });
    }

    // Forward event to N8N
    try {
      const response = await fetch(n8nWebhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Event': event || 'unknown',
        },
        body: JSON.stringify({
          event: event || 'unknown',
          data: data || {},
          timestamp: new Date().toISOString(),
          source: 'smartattend-api',
        }),
      });

      if (!response.ok) {
        console.error(`N8N webhook failed: ${response.status} ${response.statusText}`);
        return NextResponse.json(
          {
            success: false,
            error: `N8N webhook failed: ${response.statusText}`,
          },
          { status: 502 }
        );
      }

      const n8nResponse = await response.json().catch(() => ({}));

      return NextResponse.json({
        success: true,
        message: 'Webhook forwarded to N8N',
        n8nResponse,
      });
    } catch (fetchError) {
      console.error('Error forwarding to N8N:', fetchError);
      return NextResponse.json(
        {
          success: false,
          error: 'Failed to forward webhook to N8N',
          message: fetchError instanceof Error ? fetchError.message : 'Unknown error',
        },
        { status: 502 }
      );
    }
  } catch (error) {
    console.error('N8N webhook API error:', error);
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// GET /api/webhook/n8n - Health check
export async function GET() {
  const n8nWebhookUrl = process.env.N8N_WEBHOOK_URL;

  return NextResponse.json({
    status: 'ok',
    service: 'N8N Webhook API',
    configured: !!n8nWebhookUrl,
    webhookUrl: n8nWebhookUrl ? 'configured' : 'not configured',
  });
}
