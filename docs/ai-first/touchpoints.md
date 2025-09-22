
# AI Cost Model

## Assumptions
- Model: GPT-4o-mini at $0.15/1K prompt tokens, $0.60/1K completion tokens
- Smart Search: Avg tokens in: 800, Avg tokens out: 150
- Support Assistant: Avg tokens in: 1200, Avg tokens out: 200
- Smart Search requests/day: 50,000
- Support Assistant requests/day: 1,000
- Smart Search cache hit rate: 70%
- Support Assistant cache hit rate: 30%

## Calculation
Cost/action = (tokens_in/1000 * prompt_price) + (tokens_out/1000 * completion_price)
Daily cost = Cost/action * Requests/day * (1 - cache_hit_rate)

### Smart Product Search
Cost/action = (800/1000 * $0.15) + (150/1000 * $0.60)
Cost/action = $0.12 + $0.09 = **$0.21**

Daily cost = $0.21 * 50,000 * (1 - 0.70) = $0.21 * 50,000 * 0.30 = **$3,150/day**

### Support Chat Assistant  
Cost/action = (1200/1000 * $0.15) + (200/1000 * $0.60)
Cost/action = $0.18 + $0.12 = **$0.30**

Daily cost = $0.30 * 1,000 * (1 - 0.30) = $0.30 * 1,000 * 0.70 = **$210/day**

## Results
- Smart Product Search: Cost/action = $0.21, Daily = $3,150
- Support Chat Assistant: Cost/action = $0.30, Daily = $210
- **Total daily AI costs: $3,360**
- **Monthly estimate: ~$100,800**

## Cost Levers if Over Budget

### Smart Search Optimization
- Reduce context window from 800 to 500 tokens (saves ~$0.045/action = $675/day)
- Increase cache hit rate to 80% through better cache key strategies (saves $525/day)
- Use Llama 3.1 8B Instruct for 70% of simple queries (saves ~$2,100/day)

### Support Assistant Optimization  
- Implement smarter caching for common FAQ responses (target 50% hit rate saves $60/day)
- Reduce response token limit from 200 to 150 tokens (saves ~$42/day)
- Pre-filter obvious non-support queries to avoid API calls

### Emergency Cost Controls
- Daily spending caps with graceful degradation to fallback systems
- Dynamic model switching based on query complexity
- Rate limiting per user to prevent abuse
