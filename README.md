# Stock Analysis MCP Server

This project provides an MCP (Model Context Protocol) server and an ADK-based agent platform for performing advanced technical analysis and Reddit sentiment analysis on Global stocks (India, USA, etc.) using `yfinance`.

## Features

- **OHLC Candlestick Charts**: Generates professional candlestick plots using `finplot` for better technical visualization.
- **Technical Indicators**: MACD, RSI, EMA, Stochastic Oscillator, Ichimoku Cloud, etc.
- **Global Stock Data**: Integrated with `yfinance` to support NSE, NYSE, NASDAQ, etc.
- **Reddit Sentiment Analysis**: Extracts recent stock news and discussions from Reddit.
- **Volume Metrics**: On-Balance Volume (OBV), Chaikin Money Flow (CMF), VWAP.
- **ADK Integration**: A built-in agent that leverages LiteLLM to interpret data, generate technical plots, and provide trading insights.
- **Parallel Testing**: Automated test suite with `pytest-xdist` for fast parallel execution.

## Project Structure

The project is organized into logical sub-packages for better maintainability:

- **`stock_analysis_mcp/api/`**: Service entry points (MCP and ADK servers).
- **`stock_analysis_mcp/services/`**: Core business logic, `yfinance` integration, and indicator calculations.
- **`stock_analysis_mcp/core/`**: Shared configurations, constants, and logging setup.
- **`stock_analysis_mcp/agent/`**: LLM agent definitions, prompts, and specialized tools.

## Architecture

The project is structured as a suite of microservices:
1. **MCP Server**: The backend FastMCP server handling standard tools and API integrations (`mcp.dockerfile`).
2. **ADK Service**: The intelligent agent interface (`adk.dockerfile`) capable of complex reasoning and plotting.
3. **yfinance**: External library for fetching historical and real-time market data.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [uv](https://docs.astral.sh/uv/) (Python package manager for Python 3.14)

## Local Development Setup

We use VS Code's integrated Tasks to streamline development workflows. You can run these commands from the command palette (`CMD+Shift+P` -> `Tasks: Run Task`).

1. **Set up the environment:**
   Create a `.env` file in the project root. Some features require specific keys. You can find a sample in `.env.sample`.

   **Required for the ADK Agent (LLM routing):**
   - `LITE_LLM_MODEL`: The LiteLLM model string (e.g., `gemini/gemini-2.5-flash`).
   - `LITE_LLM_API_KEY`: The API key for the respective model.

   **Optional (Required ONLY for Reddit Sentiment Analysis):**
   - `REDDIT_CLIENT_ID`: Your Reddit App client ID.
   - `REDDIT_CLIENT_SECRET`: Your Reddit App client secret.
   *To get Reddit API credentials, visit [Reddit Apps](https://www.reddit.com/prefs/apps) and create a "script" application.*

   **Optional Configuration Variables:**
   - `HOST`: Host address for the servers (defaults to `127.0.0.1`).
   - `PORT`: Port for the ADK web interface (defaults to `8080`).
   - `MCP_URL`: Target URL for the MCP Tool (defaults to `http://mcp:8000/sse` in docker).
   - `REDDIT_USER_AGENT`: User agent for Reddit requests (defaults to `stock-analysis-mcp/1.0`).
   - `LOG_FORMAT`: Set to `color` for human-readable console logs, otherwise defaults to `json`.

2. **Bootstrap the project:**
   This command installs all dependencies via `uv` and sets up `pre-commit` hooks.
   - Run task: `Setup Environment`

3. **Build and start the services:**
   We use a single consolidated `docker/compose.yml` for our microservices deployment.
   - Run task: `Docker: Build Images`
   - Run task: `Docker: Start Services`
   
   Once running:
   - The **MCP Server** will be available on port `8000`.
   - The **ADK Web UI** will be available on port `8080`.
   - To monitor startup logs, run task: `Docker: Tail Logs`

4. **Tear down:**
   - Run task: `Docker: Stop Services`

## Sample Usage

Once the ADK Web UI is running, try asking:

> Analyze the technical indicators for RELIANCE.NS over the last month and show me a candlestick chart.
>
> Analyze the technical indicators for AAPL over the last month and plot the RSI alongside price action.

*Note: For Indian stocks, append `.NS` for NSE or `.BO` for BSE (e.g., `RELIANCE.NS`). US stocks use standard tickers (e.g., `AAPL`).*

## Code Quality & Testing

The project requires `ruff` for formatting and linting, and `mypy`/`pyrefly` for strict type checking. It also includes a comprehensive test suite using `pytest-xdist` for parallel execution.

- **Run Tests**: Run task `Run Tests` (or execute `uv run pytest` in terminal)
- **Format your code**: Run task `Format Code`
- **Run Linters**: Run task `Lint Code (Ruff)`
- **Run Type Checks**: Run task `Typecheck (Mypy & Pyrefly)`

The tests are also integrated into the **pre-commit** workflow and will run automatically on every commit.

## Credits

This project uses the following repositories and libraries:
- [yfinance](https://github.com/ranaroussi/yfinance) for market data
- [PRAW (Python Reddit API Wrapper)](https://github.com/praw-dev/praw) for Reddit integration
- [finplot](https://github.com/highfestiva/finplot) for professional financial charting
