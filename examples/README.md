# Workflow Examples

This directory contains examples demonstrating different workflow patterns.

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
1. Start Prefect server: `uv run prefect server start`
2. Run a workflow
3. Open http://localhost:4200 to view the dashboard

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
