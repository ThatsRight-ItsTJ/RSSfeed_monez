<content>import { createClient } from '@libsql/client';

const client = createClient({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN
});

export async function handler(event) {
  // Validate API key
  const apiKey = event.headers['x-api-key'];
  if (!apiKey || apiKey !== process.env.OFFERS_API_KEY) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: 'Invalid API key' })
    };
  }

  try {
    // Get the latest 10 items
    const result = await client.execute({
      sql: 'SELECT title, created_at, feed_type, item_hash FROM feeds ORDER BY created_at DESC LIMIT 10'
    });

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        items: result.rows,
        total: result.rows.length
      })
    };
  } catch (error) {
    console.error('Monitor error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
}</content>