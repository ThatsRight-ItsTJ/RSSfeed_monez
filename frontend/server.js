import express from 'express';
import { createClient } from '@libsql/client';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;

// Initialize Turso client
const client = createClient({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN
});

// API key validation middleware
function validateApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey || apiKey !== process.env.OFFERS_API_KEY) {
    return res.status(401).json({ error: 'Invalid API key' });
  }
  
  next();
}

// Serve static files
app.use(express.static(path.join(__dirname)));

// Search endpoint with API key validation
app.get('/api/search', validateApiKey, async (req, res) => {
  try {
    const { hash } = req.query;
    
    if (!hash) {
      return res.status(400).json({ error: 'Hash parameter is required' });
    }

    const result = await client.execute({
      sql: 'SELECT title, link, description, image_url, feed_type FROM feeds WHERE item_hash = ?',
      args: [hash]
    });

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Content not found' });
    }

    const item = result.rows[0];
    const content_class = item.feed_type || 'Content';

    res.json({
      title: item.title,
      description: sanitizeDescription(item.description),
      image_url: item.image_url,
      content_class,
      redirect_url: item.link
    });
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

function sanitizeDescription(description) {
  // Remove any XML/HTML tags and source information
  return description
    .replace(/<[^>]*>/g, '')  // Remove XML/HTML tags
    .replace(/Original content at:.*$/m, '')  // Remove source information
    .replace(/Source:.*$/m, '')  // Remove alternative source format
    .trim();
}

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});