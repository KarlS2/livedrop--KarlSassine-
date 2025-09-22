# AI Capability Map

| Capability | Intent (user) | Inputs (this sprint) | Risk 1–5 (tag) | p95 ms | Est. cost/action | Fallback | Selected |
|---|---|---|---|---:|---:|---|:---:|
| Smart Product Search | Find products quickly with natural language | Product catalog, user query, search history | 2 | 300 | $0.02 | Keyword search | yes |
| Support Chat Assistant | Get instant help with orders/policies | FAQ/policies MD, order-status API, user query | 3 | 1200 | $0.08 | Human handoff | yes |
| Dynamic Product Recommendations | Discover relevant products | User session data, product catalog, purchase history | 4 | 800 | $0.1 | Popular items | |
| Inventory Demand Forecasting | Predict stock needs | Historical sales, seasonal trends, market data | 4 | 2000 | $0.25 | Rule-based forecast | |
| Review Sentiment Analysis | Understand customer feedback | Product reviews, ratings, text content | 2 | 500 | $0.05 | Star rating only | |
| Price Optimization | Set competitive pricing | Competitor data, demand signals, cost structure | 5 | 1500 | $0.15 | Manual pricing | |

## Why these two

I've selected **Smart Product Search** and **Support Chat Assistant** as my initial AI touchpoints because they directly address two critical conversion bottlenecks in e-commerce: product discovery friction and support resolution time. Smart search can immediately improve conversion rate by helping customers find products faster with natural language queries, while the support assistant can reduce the support contact rate by around 40 to 60% through instant resolution of common order status and policy questions. Both capabilities have low integration risk, leverage existing data sources (product catalog and FAQ/policies), and provide clear fallback mechanisms to existing systems. These touchpoints also generate measurable business impact through improved user experience metrics while maintaining manageable technical complexity for our first AI implementation sprint. (And also because i have given estimates)
While other proposed options seems more intresting the complexity and risk factor (as well as the cost) makes them a less go-to option in my opinion for now.
