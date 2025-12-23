# Workflow Examples

This directory contains examples demonstrating different workflow patterns.

## LLM Deployment Pipeline Example

The LLM deployment pipeline demonstrates a **purely sequential workflow** with real dependencies:

### Workflow Steps
1. **Fetch Models** - Call catalog service to get available models
2. **Select Model** - Find and select `Llama-3.1-8B-Instruct` from the list
3. **Deploy Model** - Simulate deployment to inference endpoint
4. **Run Inference** - Send question to deployed model and get response

Each step depends on the previous step's output, making this a perfect example of sequential execution.

### Key Features
- **API Integration**: Fetches real models from catalog service (`localhost:9090`)
- **Error Handling**: Automatic retries with 3-second backoff
- **Flexible Endpoints**: Supports both `/v1/chat/completions` and `/openai/v1/chat/completions` API paths
- **Token Tracking**: Captures prompt/completion token usage
- **Real Model**: Uses deployed vLLM server with `meta-llama/Llama-3.1-8B-Instruct`

### Running the Example

**Default question:**
```bash
uv run python examples/llm_deployment/run_llm_deployment.py
```

**Custom question:**
```bash
uv run python examples/llm_deployment/run_llm_deployment.py --question "What is machine learning?"
```

### Prerequisites

- Catalog service running at `http://localhost:9090`
- vLLM server running at `http://localhost:7070` with `meta-llama/Llama-3.1-8B-Instruct` model

### Prefect Integration

**To use persistent Prefect server:**
```bash
# Set the API URL (do this once)
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"

# Start the server (in one terminal)
prefect server start

# Run the workflow (in another terminal)
uv run python examples/llm_deployment/run_llm_deployment.py
```

Then visit `http://127.0.0.1:4200` to view the workflow execution dashboard.

## Trading Bot Example

The trading bot workflow demonstrates:

### Parallel Execution
Tasks that can run independently are executed in parallel:
```python
# These run simultaneously
market_data_future = scrape_market_data.submit(symbol)
sentiment_future = scrape_sentiment.submit(symbol)
```

### Sequential Execution
Tasks with dependencies run one after another:
```python
insights = extract_insights(market_data, sentiment_data)
processed_data = clean_and_normalize(insights)
prediction = run_prediction_model(processed_data)
result = execute_trade(prediction)
```

### Flow-Level Parallelism
Multiple workflow instances run in parallel using ThreadPoolExecutor:
```python
# Each symbol gets its own parallel workflow
with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
    future_to_symbol = {
        executor.submit(trading_bot_flow, symbol): symbol
        for symbol in symbols
    }
    for future in as_completed(future_to_symbol):
        result = future.result()
```

## Running Examples

### LLM Deployment
```bash
uv run python examples/llm_deployment/run_llm_deployment.py
```

### Single Symbol Trading
```bash
uv run python run_trading_bot.py --symbol AAPL
```

### Multi-Symbol Trading (Parallel)
```bash
uv run python run_trading_bot.py --multi
```

## Workflow Visualization

To visualize workflow execution:
1. Set Prefect API URL: `prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"`
2. Start Prefect server: `prefect server start`
3. Run a workflow in another terminal
4. Open http://localhost:4200 to view the dashboard

## Key Concepts

### Tasks
Atomic units of work decorated with `@task`:
- Automatic retries on failure
- Caching support
- Distributed execution
- State tracking

### Flows
Orchestrate tasks, decorated with `@flow`:
- Define execution order
- Handle parallel execution
- Error handling and recovery
- Observability and monitoring

### Task Futures
Enable parallel execution:
```python
future = task.submit(args)  # Non-blocking
result = future.result()     # Wait for completion
```

### Why Use Prefect?

1. **Automatic Retries**: Built-in retry logic with exponential backoff
2. **Observability**: Task-level logging, timing, and state tracking
3. **Distributed Execution**: Run tasks across multiple machines
4. **Error Recovery**: Structured failure handling and flow resumption
5. **Monitoring Dashboard**: Real-time visibility into workflow execution
6. **Type Safety**: Implicit dependency tracking and validation
