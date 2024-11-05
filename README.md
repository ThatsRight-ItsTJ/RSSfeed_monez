# Feed Generator Repository

Private repository that generates RSS feeds for free games, courses and DLC.

## Repository Structure

```
feed-generator-repo/
├── .github/
│   └── workflows/
│       └── generate-feeds.yml    # GitHub Actions workflow
├── public/
│   └── feeds/                    # Generated XML feeds directory
│       └── index.html           # Feed directory page with webhook management
├── main.py                      # Main script
├── config.py                    # Configuration settings
├── feed_generator.py            # Feed generation logic
├── feed_processor.py            # Feed processing logic
├── gamerpower_processor.py      # GamerPower-specific processing
├── webhook_manager.py           # Webhook notification system
├── utils.py                     # Utility functions
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Setup

1. Create a private GitHub repository
2. Clone the repository
3. Install dependencies: `pip install -r requirements.txt`
4. Set up GitHub secrets:
   - `GITHUB_TOKEN`: Personal access token with 'repo' scope

## GitHub Actions

The workflow runs every 4 hours and:
1. Generates RSS feeds
2. Creates redirect versions
3. Compresses XML files
4. Maintains 7-day feed history
5. Pushes changes to repository

## Development

- Feeds are stored in `public/feeds/`
- Each feed has a regular and redirect version
- Webhooks can be configured through `index.html`
- XML files are tracked in git for history
