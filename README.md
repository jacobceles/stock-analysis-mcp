# MCP Server with NSE India Data

This project provides a MCP (Model Context Protocol) server that uses data from the NSE India API. It includes technical indicators and Reddit sentiment analysis for Indian stocks.

## Prerequisites

- Docker
- Docker Compose

## How to run locally

1.  **Set up environment variables:**

    Create a `.env` file in the project root with the following variables:
    
    ```env
    GOOGLE_API_KEY=your_google_api_key
    REDDIT_CLIENT_ID=your_reddit_client_id
    REDDIT_CLIENT_SECRET=your_reddit_client_secret
    REDDIT_USER_AGENT=stock-analysis-mcp/1.0
    LITE_LLM_MODEL=llm_model_name
    LITE_LLM_API_KEY=llm_api_key
    ```
    
    To get Reddit API credentials:
    1. Go to https://www.reddit.com/prefs/apps
    2. Click "Create App" or "Create Another App"
    3. Fill in the form:
       - Name: stock-analysis-mcp (or any name you prefer)
       - App type: Select "script"
       - Description: (optional)
       - About URL: (leave blank)
       - Redirect URI: http://localhost:8000 (or any valid URL)
    4. Click "Create App"
    5. Copy the client ID (under the app name) and client secret

2.  **Build and run the services:**

    ```bash
    docker-compose up --build

    or

    docker-compose -f docker-compose_1.yml up --build
    ```

This will start both the `nseindia` and `mcp` services. The `mcp` service will be available on port `8000`.

## Features

- Technical indicators (MACD, RSI, EMA, etc.)
- Historical stock data from NSE India
- Reddit sentiment analysis for stocks
- Volume-based metrics (OBV, CMF, VWAP)

## Credits

This project uses the following repositories and libraries:

- [stock-nse-india](https://github.com/hi-imcodeman/stock-nse-india) for NSE India data
- [PRAW (Python Reddit API Wrapper)](https://github.com/praw-dev/praw) for Reddit integration
