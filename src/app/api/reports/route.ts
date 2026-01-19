export async function GET() {
  return new Response(
    JSON.stringify({
      success: false,
      error: 'Reports API is not implemented yet.',
    }),
    {
      status: 501,
      headers: {
        'Content-Type': 'application/json',
      },
    },
  );
}
