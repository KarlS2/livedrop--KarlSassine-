# AI Cost Model 

## Given Info
- Model: GPT-4o-mini at $0.15/1K prompt tokens, $0.60/1K completion tokens
- Support Assistant: Avg tokens in = 800, Avg tokens out = 200
- Typeahead Search: Avg tokens in = 150, Avg tokens out = 50
- Support Assistant requests/day = 1,000
- Typeahead Search requests/day = 50,000
- Support Assistant cache hit rate = 30%
- Typeahead Search cache hit rate = 70%

---

## Calculation (main logic)
Cost/action = (tokens_in / 1000 * prompt_price) + (tokens_out / 1000 * completion_price)  
Daily cost = Cost/action * Requests/day * (1 - cache_hit_rate)

---

### Support Assistant
Cost/action = (800/1000 * $0.15) + (200/1000 * $0.60)  
Cost/action = $0.12 + $0.12 = **$0.24**
Daily cost = $0.24 * 1,000 * (1 - 0.30)  
Daily cost = $0.24 * 1,000 * 0.70 = **$168/day**

Effective cost/action with cache = $0.24 * 0.70 = **$0.168 ≈ $0.17**

---

### Typeahead Search  
Cost/action = (150/1000 * $0.15) + (50/1000 * $0.60)  
Cost/action = $0.0225 + $0.030 = **$0.0525**
Daily cost = $0.0525 * 50,000 * (1 - 0.70)  
Daily cost = $0.0525 * 50,000 * 0.30 = **$787.50/day**

Effective cost/action with cache = $0.0525 * 0.30 = **$0.016**

---

## Results
- Support Assistant: Cost/action = **$0.17**, Daily = **$168**  
- Typeahead Search: Cost/action = **$0.016**, Daily = **$787.50**  
- **Total daily AI costs: $955.50**  
- **Monthly estimate: ~$28,665**

It seems that the cost is a bit high for an application of this size but the estimate price is according to the given info.
However i might have misunderstood the numbers. (According to these result, my verdict is that this is not efficient).

---

## Cost Levers if Over Budget

### Typeahead Search Optimization
- Push cache hit rate to 80% (saves ~$157/day)  
- Reduce context tokens from 150 → 100 (saves ~$131/day)  
- Hybrid approach: cheap vector search for 90% of queries, LLM rerank only for long-tail  

### Support Assistant Optimization
- Pre-compute and cache top 50 FAQ answers (saves ~$50/day)  
- Cap response length to 150 tokens (saves ~$17/day)  
- Route trivial questions ("shipping cost", "return policy") to static responses  

### Emergency Cost Controls
- Apply **daily budget cap** with fallback to static keyword/typeahead  
- Dynamic model routing (e.g., fallback to Llama 3.1 8B for low-risk queries)  
- Query throttling to prevent abuse
