# AI Cost Model (Optimized)

## Assumptions
- Model: GPT-4o-mini at $0.15/1K prompt tokens, $0.60/1K completion tokens
- Support Assistant: Avg tokens in = 150, Avg tokens out = 100
- Typeahead Search: Avg tokens in = 50, Avg tokens out = 20
- Support Assistant requests/day = 1,000
- Typeahead Search requests/day = 50,000
- Support Assistant cache hit rate = 50%
- Typeahead Search cache hit rate = 80%

---

## Calculation
Cost/action = (tokens_in / 1000 * prompt_price) + (tokens_out / 1000 * completion_price)  
Daily cost = Cost/action * Requests/day * (1 - cache_hit_rate)

---

### Support Assistant
Cost/action = (150/1000 * $0.15) + (100/1000 * $0.60)  
Cost/action = $0.0225 + $0.060 = **$0.0825**

Daily cost = $0.0825 * 1,000 * (1 - 0.50)  
Daily cost = $0.0825 * 1,000 * 0.50 = **$41.25/day**

---

### Typeahead Search
Cost/action = (50/1000 * $0.15) + (20/1000 * $0.60)  
Cost/action = $0.0075 + $0.012 = **$0.0195**

Daily cost = $0.0195 * 50,000 * (1 - 0.80)  
Daily cost = $0.0195 * 50,000 * 0.20 = **$195/day**

---

## Results
- Support Assistant: Cost/action = **$0.0825**, Daily = **$41.25**  
- Typeahead Search: Cost/action = **$0.0195**, Daily = **$195**  
- **Total daily AI costs: $236.25**  
- **Monthly estimate: ~$7,088**

---

## Cost Levers if Over Budget

### Typeahead Search Optimization
- Push cache hit rate to 85% (saves ~$49/day)  
- Reduce rerank tokens from 20 → 10 (saves ~$39/day)  
- Hybrid approach: cheap vector search for 90% of queries, LLM rerank only for long-tail  

### Support Assistant Optimization
- Pre-compute and cache top 50 FAQ answers (saves ~$10/day)  
- Cap response length to 75 tokens (saves ~$8/day)  
- Route trivial questions (“shipping cost”, “return policy”) to static responses  

### Emergency Cost Controls
- Apply **daily budget cap** with fallback to static keyword/typeahead  
- Dynamic model routing (e.g., fallback to Llama 3.1 8B for low-risk queries)  
- Query throttling to prevent abuse  
