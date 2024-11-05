import { createClient } from '@libsql/client';

const client = createClient({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN
});

function sanitizeDescription(description) {
  return description
    .replace(/<[^>]*>/g, '')
    .replace(/Original content at:.*$/m, '')
    .replace(/Source:.*$/m, '')
    .trim();
}

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
    const { hash } = event.queryStringParameters;
    
    if (!hash) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Hash parameter is required' })
      };
    }

    const result = await client.execute({
      sql: 'SELECT title, link, description, image_url, feed_type FROM feeds WHERE item_hash = ?',
      args: [hash]
    });

    if (result.rows.length === 0) {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'Content not found' })
      };
    }

    const item = result.rows[0];
    const content_class = item.feed_type || 'Content';

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: item.title,
        description: sanitizeDescription(item.description),
        image_url: item.image_url,
        content_class,
        redirect_url: item.link
      })
    };
  } catch (error) {
    console.error('Search error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
}