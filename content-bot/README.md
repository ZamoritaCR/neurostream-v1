# Dopamine.watch Content Automation Bot

Automated content generation and publishing system for dopamine.watch blog.

## Features

- **Auto-generates blog posts** using GPT-4
- **Publishes directly** to GreenGeeks via FTP
- **Updates blog homepage** automatically
- **Social media posting** (Twitter, LinkedIn, Facebook)
- **Programmatic SEO** landing pages
- **A/B testing** for headlines and CTAs
- **Analytics tracking** and reporting
- **Site monitoring** and health checks
- **Scheduled posting** (Mon/Thu 9am)

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Test the bot

```bash
python main.py test
```

### 4. Generate a post

```bash
python main.py generate
```

## Commands

### Main Bot

```bash
# Generate and publish a new post
python main.py generate

# Generate without publishing (dry run)
python main.py generate --dry-run

# Save locally without FTP upload
python main.py generate --no-publish

# Generate multiple posts
python main.py generate --count 3

# Generate topic ideas only
python main.py topics --count 10

# Run on schedule (Mon & Thu at 9am)
python main.py schedule

# Test configuration
python main.py test
```

### Social Media

```bash
# Test social media posting
python social_media.py
```

### Analytics

```bash
# Generate performance report
python analytics_dashboard.py
```

### A/B Testing

```bash
# Generate headline variants and report
python ab_testing.py
```

### RSS Feed

```bash
# Generate and upload RSS feed
python generate_rss.py
```

### SEO Audit

```bash
# Run full SEO audit
python seo_audit.py

# Print SEO checklist
python seo_audit.py --checklist
```

### Site Monitoring

```bash
# Run health check
python monitor.py

# Get uptime report
python monitor.py --report

# Check specific URL
python monitor.py --url https://dopamine.watch/blog/
```

## File Structure

```
content-bot/
├── main.py              # Main bot orchestrator
├── generator.py         # Content generation (GPT-4)
├── publisher.py         # FTP publishing
├── social_media.py      # Social media automation
├── analytics_dashboard.py   # Custom analytics
├── ab_testing.py        # A/B testing framework
├── generate_rss.py      # RSS feed generator
├── seo_audit.py         # SEO optimization checker
├── monitor.py           # Site health monitoring
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── README.md            # This file
├── LAUNCH_CHECKLIST.md  # Launch checklist
├── templates/
│   └── newsletter_template.html
├── output/              # Generated content
│   └── posts/
└── logs/                # Activity logs
    ├── analytics/
    ├── ab_tests/
    ├── monitoring/
    └── social/
```

## Deployment

### Option 1: Railway (Recommended for 24/7)

```bash
# Create Procfile
echo "worker: python main.py schedule" > Procfile

# Deploy
railway init
railway up

# Set environment variables in Railway dashboard
```

### Option 2: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add scheduled runs (Mon & Thu at 9am)
0 9 * * 1,4 cd /path/to/content-bot && python main.py generate

# Add hourly health check
0 * * * * cd /path/to/content-bot && python monitor.py
```

### Option 3: Local Background

```bash
# Run in background
nohup python main.py schedule &
```

## Environment Variables

### Required

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 |
| `FTP_HOST` | FTP server hostname |
| `FTP_USER` | FTP username |
| `FTP_PASSWORD` | FTP password |

### Optional - Social Media

| Variable | Description |
|----------|-------------|
| `TWITTER_API_KEY` | Twitter API key |
| `TWITTER_API_SECRET` | Twitter API secret |
| `TWITTER_ACCESS_TOKEN` | Twitter access token |
| `TWITTER_ACCESS_SECRET` | Twitter access secret |
| `LINKEDIN_TOKEN` | LinkedIn API token |
| `FACEBOOK_PAGE_TOKEN` | Facebook Page access token |

**Note:** Social media posting will log content even without API keys configured.

## Maintenance

- Bot logs all operations in `logs/` directory
- Failed posts are logged for review
- Manual override always available
- Check `LAUNCH_CHECKLIST.md` for launch tasks

## Troubleshooting

### OpenAI API errors

- Check API key is valid
- Verify you have credits remaining
- Check rate limits

### FTP connection fails

- Verify credentials in `.env`
- Check firewall/network access
- Try connecting manually first

### Social media not posting

- API keys are optional - posts will be logged
- Check API credentials are valid
- Review platform-specific rate limits

## Support

Built with for neurodivergent brains by dopamine.watch

For issues, check the main project repository.
