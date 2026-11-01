# ZNSouq Dataset

A synthetic knowledge base for **ZNSouq**, a fictional Egyptian online marketplace where third-party sellers run their own stores. Built to learn RAG on a realistic, multi-seller ("multi-tenant") problem. All names, brands, stores and people are fictional. The dataset's "today" is **2026-10-30**.

## What's inside

| Folder / file | What it is | Size | RAG role |
|---|---|---|---|
| `platform/buyer/` | Buyer help center: orders, delivery, payments, returns, refunds, Guarantee, Plus... | 28 docs | Embed |
| `platform/buyer/delivery-by-governorate/` | One page per Egyptian governorate (zones, fees, COD, coverage notes) | 27 docs | Embed |
| `platform/buyer/returns-by-category/` | Return rules for each of the 16 categories | 16 docs | Embed |
| `platform/seller/` | Seller help center: plans, fees, FBZ, payouts, account health, appeals... | 25 docs | Embed |
| `platform/seller/fees-by-category/` | Referral fees per category (incl. the Nov 2026 change) | 16 docs | Embed |
| `sellers/` | One store page per seller: shipping, return and warranty policies | 101 docs | Embed (filter by `seller_id`) |
| `catalog/products.jsonl` | 5,000 products with attributes, features, warranty and **offers** (1,294 have several sellers) | 5,000 rows | Convert each to text, then embed |
| `catalog/reviews.jsonl` | ~26,000 verified reviews | ~26k rows | Embed (filter by `product_id`) |
| `catalog/sellers.json` | Structured seller data incl. account-health metrics | 101 rows | Metadata / lookups |
| `catalog/orders.jsonl` | 600 sample orders | 600 rows | **Not for RAG**: used on Day 2 to learn tool calling |
| `eval/questions.jsonl` | 43 test questions with expected answers and source docs | 43 rows | Evaluation |
| `scripts/` | The generator scripts (deterministic, seeded) | | Rebuild/modify the data |

Every Markdown doc starts with a metadata header (`title`, `audience`, `type`, `last_updated`, plus `governorate`, `category` or `seller_id` where relevant). Use these as **metadata filters**.

## Business model in one minute
- **Sellers** list products. Many products have **several offers** (different sellers, prices, conditions and fulfillment).
- **Fulfilled by ZNSouq (FBZ)** vs **Fulfilled by seller** changes delivery time, fees, returns and Plus eligibility.
- **4 delivery zones** across 27 governorates.
- **Platform rules are minimums.** Sellers may offer more generous terms (for example longer return windows), never stricter ones.
- **ZNSouq Plus** membership, the **ZNSouq Guarantee**, COD, installments, Wallet.
- Sellers pay plan fees, **category referral fees**, and FBZ fees, all subject to 14% VAT.

## Traps built in on purpose (the eval set tests them)
1. **Seller overrides**: some stores extend return windows, so the right answer depends on *which seller*.
2. **Conflicting store pages**: S0017, S0052 and S0088 claim a 7-day return policy that breaks ZNSouq's rules. The platform rule wins.
3. **Time**: referral fees change on **2026-11-01**. The fee depends on the order date.
4. **Similar products**: thousands of products share types and brands. Exact model codes like `ZNP-ELE-00042` and `ZE-518` need hybrid (keyword) search.
5. **Structured vs. unstructured**: prices, stock and order status are data, not prose. Order questions need a tool, not RAG.
6. **Unanswerable and out-of-scope** questions: the bot must say "I don't know" instead of inventing.

## Eval question types
`fact`, `temporal`, `calculation`, `seller_override`, `conflict`, `product`, `reviews`, `needs_tool`, `unanswerable`, `out_of_scope`.

## Regenerating
```bash
cd scripts
python -c "import docs_buyer, docs_seller, docs_generated as g; docs_buyer.build(); docs_seller.build(); g.build()"
python gen_catalog.py
python gen_eval.py
```
Edit `facts.py` to change any policy number; every doc and eval answer updates consistently.
