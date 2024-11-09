import fetch from 'node-fetch';

const API_BASE_URL = 'https://unlockcontent.net/api/v2';

export async function handler(event) {
  // Validate API key
  const apiKey = event.headers['x-api-key'];
  if (!apiKey || apiKey !== process.env.OFFERS_API_KEY) {
    return {
      statusCode: 401,
      body: JSON.stringify({ error: 'Invalid API key' })
    };
  }

  // Get offer ID from query parameters
  const { offerId } = event.queryStringParameters;
  if (!offerId) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Offer ID is required' })
    };
  }

  try {
    // Check offer completion status
    const response = await fetch(`${API_BASE_URL}/offers/${offerId}/status`, {
      headers: {
        'X-API-Key': process.env.OFFERS_API_KEY,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }

    const data = await response.json();

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        success: true,
        completed: data.completed
      })
    };
  } catch (error) {
    console.error('Error verifying offer:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        success: false,
        error: 'Failed to verify offer completion'
      })
    };
  }
}