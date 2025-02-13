# AI Content Creation Agency

An AI-powered agency that analyzes YouTube trends, generates content ideas, and provides data-driven insights using the Agency Swarm framework.

## Features

- **Content Management**: Generate and manage AI-focused content
- **YouTube Analytics**: Analyze channels, videos, and competitor performance
- **Trend Analysis**: Track and analyze AI industry trends
- **Sentiment Analysis**: Analyze YouTube comments and engagement
- **Content Generation**: Create AI-focused content ideas and scripts

## Prerequisites

- Python 3.8+
- OpenAI API key
- YouTube Data API key
- Tavily API key

## Setup

1. **Create Virtual Environment**
```bash
# Create a new virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r content_creation_agency/requirements.txt
```

3. **API Keys Setup**

You'll need to obtain the following API keys:

- **OpenAI API Key**: 
  - Visit [OpenAI Platform](https://platform.openai.com/)
  - Create an account or log in
  - Go to API section
  - Create a new API key

- **YouTube Data API Key**:
  - Visit [Google Cloud Console](https://console.cloud.google.com/)
  - Create a new project
  - Enable YouTube Data API v3
  - Create credentials (API key)

- **Tavily API Key**:
  - Visit [Tavily AI](https://tavily.com/)
  - Sign up for an account
  - Get your API key from the dashboard

4. **Environment Setup**

Create a `.env` file in the `content_creation_agency` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
DEFAULT_CHANNEL_ID=your_channel_id_here  # Your YouTube Channel ID (required for channel analysis)
```

To find your YouTube Channel ID:
1. Go to your YouTube channel
2. Right-click anywhere on the page and select "View Page Source"
3. Press Ctrl+F (or Cmd+F on Mac) and search for "channelId"
4. Look for a string that starts with "UC" (e.g., UCbmCqH_WOUviDUsV83qloZQ)

Alternatively:
1. Go to your channel's URL
2. If it's in the format: youtube.com/channel/UC..., the part after "channel/" is your Channel ID
3. If you have a custom URL (e.g., youtube.com/@username), you'll need to use the page source method above

Note: The DEFAULT_CHANNEL_ID is required for:
- Channel analytics and statistics
- Video performance tracking
- Comment sentiment analysis of your channel's videos
- Competitor analysis relative to your channel

## Project Structure

```
content_creation_agency/
├── content_manager/         # Content management agent
│   ├── tools/              # Content generation tools
│   └── instructions.md     # Agent instructions
├── youtube_analyzer/       # YouTube analysis agent
│   ├── tools/             # YouTube analytics tools
│   └── instructions.md    # Agent instructions
├── trend_analyzer/        # Trend analysis agent
│   ├── tools/            # Trend analysis tools
│   └── instructions.md   # Agent instructions
├── agency.py             # Main agency configuration
├── app.py               # Application entry point
├── requirements.txt     # Project dependencies
└── agency_manifesto.md  # Agency guidelines
```

## Running the Agency

1. **Terminal Demo Mode**
```bash
python content_creation_agency/agency.py
```

2. **Using Individual Tools**

You can test individual tools directly:

```bash
# Test YouTube Channel Analytics
python content_creation_agency/youtube_analyzer/tools/ChannelAnalytics.py

# Test Trend Analysis
python content_creation_agency/trend_analyzer/tools/TrendAnalyzer.py
```

## Usage Examples

1. **Analyze YouTube Channel**
```
Analyze the YouTube channel @example
```

2. **Get Trend Analysis**
```
What are the current trends in AI technology?
```

3. **Generate Content Ideas**
```
Generate video ideas about machine learning
```

## Important Notes

1. **API Rate Limits**: Be mindful of API rate limits, especially for YouTube Data API
2. **Environment Variables**: Never commit your `.env` file to version control
3. **Virtual Environment**: Always use the virtual environment when running the project
4. **Language Settings**: The tools are configured for global/English results by default

## Troubleshooting

1. **API Key Issues**
   - Verify API keys are correctly set in `.env`
   - Check API key permissions and quotas
   - Ensure `.env` file is in the correct location

2. **Dependencies**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Common Errors**
   - `ModuleNotFoundError`: Activate virtual environment
   - `KeyError`: Check `.env` file configuration
   - `QuotaExceededError`: Check API usage limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 