# RAG System Evaluation

## Overview
This document contains manual evaluation tests for the Shoplite RAG system. Tests are organized into three categories: Retrieval Quality (10 tests), Response Quality (15 tests), and Edge Cases (5 tests).

**Evaluation Date:** [2/10/2025]
**Evaluator:** [Karl Sassine]
**System Version:** RAG with Qwen1.5-7B-Chat + FAISS + all-MiniLM-L6-v2

---

## 1. Retrieval Quality Tests (10 tests)

These tests verify that the FAISS similarity search retrieves relevant documents for queries.

| Test ID | Question | Expected Documents | Retrieved Documents | Pass/Fail | Notes |
|---------|----------|-------------------|---------------------|-----------|-------|
| R01 | How long does seller verification take? | Document 8: Seller Account Setup and managment| Seller Account Setup and managment| Pass | the source of the response came from document 8. 8.7s response time|
| R02 | What are the shipping timeframes? | Document 5: Order Tracking and Delivery | Shoplite Order Tracking and Delivery | Pass | The only issue is that it referred to document 5 as document 1, correct answer though |
| R03 | What commission do Basic tier sellers pay? | Document 10: Commission and Fee Structure |Commission and Fee Structure | Pass| the additional help are misnumbered, correct intial answer |
| R04 | How do I return a damaged product? | Document 6: Return and Refund Policies | list of the return proceedure | Pass | exellent answer, wrong document number again |
| R05 | What security measures protect my payment? | Document 4: Payment Methods and Security, Document 14: Security and Privacy | combined answer from both documents | Pass | |
| R06 | How do promotional codes work? | Document 15: Promotional Codes and Discounts | step by step list on how do prom codes work| Pass | correct document |
| R07 | What are the password requirements? | Document 1: User Registration Process | list of password requirement | Pass | correct answer, still refering to wrong document number |
| R08 | How do I track my order? | Document 5: Order Tracking and Delivery | Shoplite Order Tracking and Delivery  | Pass | correct answer, still refering to wrong document number |
| R09 | What performance metrics must sellers maintain? | Document 16: Seller Performance Metrics | list of the metrics | Pass | correct answer, still refering to wrong document number |
| R10 | What is the API rate limit? | Document 13: API Documentation for developpers | correct answer | Pass | |

**Retrieval Quality Summary:**
- Tests Passed: 10 / 10
- Tests Failed: 0 / 10
- Pass Rate: 100%
- Accuracy: 80%

Note: The initial test were generally accurate, as the model answered according to the response format in the prompt, however it seemed to have mixed the document numbers when it is required to give 
additional info. The answers themself on the other hand were accurate to the document and structured as in the prompts. With minor innaccuracies, the model has passed this test.
---

## 2. Response Quality Tests (15 tests)

These tests verify that generated responses contain required information and avoid forbidden content.

| Test ID | Question | Required Keywords | Forbidden Terms | Contains Required? | Avoids Forbidden? | Overall Pass/Fail | Notes |
|---------|----------|-------------------|-----------------|-------------------|------------------|------------------|-------|
| Q01 | How long does seller verification take? | ["2-3 business days", "verification", "documents"] | ["instant", "same day", "automatic"] | Yes | Yes | Pass | |
| Q02 | What are standard shipping timeframes? | ["5-7 business days", "standard shipping"] | ["overnight", "same day"] | Yes | Yes | Pass | it met the requirement however it is saying it provided a link when there is none |
| Q03 | What are password requirements? | ["8 characters", "uppercase", "lowercase", "numbers", "special character"] | ["no requirements", "any password"] | Yes | Yes | Pass | |
| Q04 | What commission do Basic sellers pay? | ["12%", "commission", "Basic tier", "$0.30"] | ["8%", "free", "no commission"] | Yes  |  Yes  | Pass | |
| Q05 | How many images required for listings? | ["3 images", "minimum", "1000x1000 pixels"] | ["1 image", "no images"] |Yes | Yes  | Pass | the answer contained 2 of 3 required keywords |
| Q06 | What is the ODR threshold? | ["1%", "ODR", "Order Defect Rate", "below"] | ["5%", "10%", "no limit"] | Yes | Yes | Pass | it rephrased below to should not exceed, same context though |
| Q07 | How long to complete email verification? | ["24 hours", "email verification", "mandatory"] | ["optional", "no time limit", "7 days"] | Yes | Yes  |  Pass  | it rephrased mandatory to essential, same context though |
| Q08 | What is standard API rate limit? | ["1000 requests", "per hour", "standard"] | ["unlimited", "5000 for standard"] | Yes | Yes | Pass | |
| Q09 | How do I start selling? (Multi-doc) | ["Seller Central", "verification", "2-3 business days", "12% commission"] | ["instant approval", "no fees"] | No | No | Fail | Request timed out. The API might be processing a long response. |
| Q10 | How to return damaged product? (Multi-doc) | ["Request Return", "24-48 hours", "prepaid label", "5-7 business days"] | ["immediate refund", "no return needed"] | Yes | Yes | Pass | |
| Q11 | How to track orders and get notifications? | ["My Orders", "email", "SMS", "tracking page"] | ["no tracking", "manual check only"] | Yes | Yes | Pass | not all the required keywords were mentioned |
| Q12 | What security measures exist? (Multi-doc) | ["256-bit SSL", "tokenization", "PCI DSS", "two-factor"] | ["no encryption", "stores credit cards"] | No | No | Fail | Request timed out. The API might be processing a long response. |
| Q13 | How to get customer support? | ["live chat", "9 AM - 9 PM EST", "email", "24 hours"] | ["no support", "weeks to respond"] | Yes |  Yes  |  Pass | |
| Q14 | Difference between cart and Save for Later? | ["Save for Later", "logged-in users", "preserved", "7 days"] | ["same thing", "no difference"] | Yes | Yes | Pass | |
| Q15 | How do product reviews work? | ["verified buyers", "3 days after delivery", "90 days", "Verified purchase badges"] | ["anyone can review", "instant posting"] |  Yes | Yes  |  Pass  | |

**Response Quality Summary:**
- Tests Passed: 13 / 15
- Tests Failed: 2 / 15
- Pass Rate: 86%

---

## 3. Edge Case Tests (5 tests)

These tests verify system behavior in challenging scenarios.

| Test ID | Scenario | Expected Response Type | Actual Behavior | Pass/Fail | Notes |
|---------|----------|----------------------|-----------------|-----------|-------|
| E01 | Question not in knowledge base: "What is your refund policy for digital downloads?" | Refusal with explanation ("documentation doesn't contain...") + suggest support channels + Should NOT make up information | It responded better than expected by giving convicing claims| Pass | again wrong document number referal |
| E02 | Ambiguous question: "How long does it take?" | Clarification request asking what process/timeframe they mean. Should ask for specifics| it assumed that the user was asking about delivery time | Fail |  the top 3 sources were somewhat close to containg all the answers however the user was not asked for specifics |
| E03 | Query with typos: "How do I creat a seler acount" | Still retrieves correct docs and answers about seller account creation. Embedding model should handle typos | it retrieved the correct document| Pass |  |
| E04 | Empty/nonsense query: "" or "asdfghjkl" | Error message or request for valid question. Should handle gracefully| it asked itself a random( not out of topic) question and answered itself| Fail |  |
| E05 | Very specific detail: "What is the exact hex color code for the Shoplite logo?" | Acknowledge limitation, explain info not in documentation, suggest contacting support. Should not hallucinate specifics | the model did not answer, and said sorry(acknowledgement of limitation about specifics) | Pass | it mentioned that this is not part of its documentation |

**Edge Case Summary:**
- Tests Passed: 3 / 5
- Tests Failed: 2 / 5
- Pass Rate: 60%

---

## 4. Overall System Performance

### Aggregate Metrics
- **Total Tests:** 30
- **Total Passed:** 26
- **Total Failed:** 4
- **Overall Pass Rate:** 86%

---

## 5. Qualitative Assessment

### Strengths
1. Good answer structure
2. Not too much hallucination
3. Covers alot of ground

### Weaknesses
1. Providing correct answers but with wrong document numbers when providing additional info
2. Can't handle long responses
3. 


### Example Failure Case
**Query:**  What are the shipping timeframes?
**Retrieved Docs:**  Shoplite Order Tracking and Delivery (document 5) 
**Response:** Shipping timeframes for Shoplite vary based on the selected shipping method. Standard shipping typically takes 5-7 business days, expedited shipping takes 2-3 business days, and express overnight shipping delivers within 1 business day for orders placed before 2 PM. International orders have extended delivery windows of 10-21 business days, depending on the destination country and customs processing. You can find this information in Document 1: Shoplite Order Tracking and Delivery.
**What went wrong:** it reffers the correct document but with its wrong number.( it is giving the same document number for other cases like this)
**Potential fix:** fix the embedings or the prompts

---

## Future Enhancements
1. Make sure to provide longer responses
2. Fixes for failed edge cases.

Note: if the LLM deployment shows on the logs, Qwen guard 8B it was the previous model i used before this one. The correct model name should work when you rerun the cells, but i ran out of GPU usage.


