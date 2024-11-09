import fetch from 'node-fetch';

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
    // Get client IP and user agent
    const ip = event.headers['x-forwarded-for'] || event.headers['client-ip'];
    const userAgent = event.headers['user-agent'];

    // Call UnlockContent API
    const response = await fetch(`https://unlockcontent.net/api/v2?${new URLSearchParams({
      ip,
      user_agent: userAgent
    })}`, {
      headers: {
        'Authorization': `Bearer ${process.env.UNLOCK_CONTENT_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'API returned error');
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        success: true,
        offers: data.offers
      })
    };
  } catch (error) {
    console.error('Error fetching offers:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ 
        success: false,
        error: 'Failed to fetch offers' 
      })
    };
  }
}