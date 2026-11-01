"""Build eval/questions.jsonl: questions with expected answers and the source docs that contain them.
Answers are computed from facts.py and the generated catalog, so they are guaranteed consistent."""
import json, random
from common import *

random.seed(7)
C = f"{OUT}/catalog"
sellers = json.load(open(f"{C}/sellers.json"))
products = [json.loads(l) for l in open(f"{C}/products.jsonl")]
S = {s["seller_id"]: s for s in sellers}
Q = []


def add(q, a, sources, kind, audience="buyer", difficulty="easy"):
    Q.append(dict(id=f"Q{len(Q) + 1:03d}", question=q, expected_answer=a, sources=sources, type=kind,
                  audience=audience, difficulty=difficulty))


pb, ps = "platform/buyer/", "platform/seller/"
# ---- platform facts (buyer)
add("Can I return a shirt I already washed?", "No. Men's and Women's Fashion change-of-mind returns require the item to be unworn, unwashed and with original tags attached (30-day window). Defective items are still returnable.",
    [pb + "returns-by-category/fashion-men.md", pb + "returns-policy.md"], "fact")
add("How much is the cash on delivery fee?", f"{COD_FEE} EGP per shipment; free for Plus members. COD is available for orders up to {fmt(COD_MAX)} EGP.", [pb + "cash-on-delivery.md"], "fact")
add("What is the minimum order for free shipping?", f"{FREE_SHIP_THRESHOLD} EGP of Fulfilled by ZNSouq items, standard delivery, Zones A-C only.", [pb + "free-shipping.md"], "fact")
add("How much does ZNSouq Plus cost per year?", f"{PLUS['yearly']} EGP per year (or {PLUS['monthly']} EGP/month; students {PLUS['student_monthly']} EGP/month), with a {PLUS['trial_days']}-day free trial.", [pb + "znsouq-plus.md"], "fact")
add("How long does a refund to my card take?", REFUND_TIMES["Credit/debit card"] + ".", [pb + "refunds.md"], "fact")
add("My order hasn't arrived. When can I file a ZNSouq Guarantee claim?", f"{GUARANTEE_WAIT_DAYS} days after the latest estimated delivery date, and within {GUARANTEE_FILE_WINDOW} days of it. Contact the seller first and wait 2 business days.", [pb + "znsouq-guarantee.md"], "fact", difficulty="medium")
add("What's the minimum order to pay in installments?", f"{fmt(INSTALLMENT_MIN)} EGP, through ZNPay. 6 months is 0% interest on orders of 3,000 EGP or more.", [pb + "installments.md"], "fact")
add("How long are gift cards valid?", f"{GIFT_CARD['validity_years']} years from the date of purchase.", [pb + "gift-cards.md"], "fact")
add("Can I use two coupons on the same order?", "No, only one coupon per order, and coupons cannot be combined with Lightning Deals.", [pb + "coupons-and-promotions.md"], "fact")
add("I received an opened bag of coffee that tastes stale. Can I return it?", f"Grocery items are not returnable for change of mind. Damaged, expired or wrong items must be reported within {DAMAGE_REPORT_HOURS} hours of delivery.", [pb + "returns-by-category/grocery.md", pb + "damaged-defective-wrong-items.md"], "fact", difficulty="medium")
add("Someone called me from ZNSouq asking for my OTP. Is that normal?", f"No. ZNSouq never asks for passwords or OTP codes and only calls from {SUPPORT['buyer_phone']}. It's a scam.", [pb + "account-security-and-scams.md"], "fact")

# ---- governorates
for gov in ["Luxor", "North Sinai", "Giza", "Matrouh"]:
    z = GOV_ZONE[gov]; d = ZONES[z]
    exp = f"express {d['exp']} ({d['exp_fee']} EGP)" if d["exp"] else "no express delivery"
    extra = " Cash on delivery is not available in North Sinai, and delivery covers Arish only." if gov == "North Sinai" else ""
    add(f"How long does delivery to {gov} take and how much does it cost?",
        f"{gov} is Zone {z}: standard {d['std_days']} business days for {d['std_fee']} EGP (FBZ items); {exp}.{extra}",
        [pb + f"delivery-by-governorate/{gov.lower().replace(' ', '-')}.md", pb + "delivery-options-and-fees.md"], "fact", difficulty="medium")

# ---- seller platform facts
add("When do sellers get paid?", f"Every {PAYOUT['day']}, for orders delivered at least {PAYOUT['reserve_days']} days ago ({PAYOUT['new_seller_reserve_days']} days for new sellers in their first {PAYOUT['new_seller_period_days']} days). Minimum payout {PAYOUT['minimum']} EGP.", [ps + "payouts.md"], "fact", "seller")
add("What Order Defect Rate do I need to keep?", f"Below {HEALTH['odr']}%.", [ps + "account-health.md"], "fact", "seller")
add("How long do I have to appeal an account suspension?", f"{APPEAL_DAYS} days from the suspension notice, by submitting a Plan of Action; review takes {APPEAL_REVIEW}.", [ps + "suspension-and-appeals.md"], "fact", "seller")
add("What does the Professional plan cost?", f"{PLANS['Professional']['monthly']} EGP per month (+{VAT}% VAT), no per-item closing fee. Individual plan has no monthly fee but {PLANS['Individual']['per_item']} EGP per item sold.", [ps + "selling-plans.md"], "fact", "seller")
add("What is the FBZ fulfillment fee for a 3 kg item?", f"Standard large tier (up to 5 kg): {FBZ_TIERS[2][2]} EGP per unit, plus {VAT}% VAT.", [ps + "fbn-fees.md"], "fact", "seller", "medium")
add("Do I need approval to sell mobile phones?", "Yes. Mobile Phones & Tablets is gated: proof of authorized distribution and NTRA type approval per model; Professional plan required. Accessories don't need approval.", [ps + "gated-categories.md"], "fact", "seller")
add("How much is FBZ storage in December?", f"{STORAGE_FEE['oct_dec']} EGP per cubic foot per month (October-December peak rate).", [ps + "fbn-fees.md"], "fact", "seller")

# ---- temporal: fee change (dataset date is 2026-10-30)
e = CAT["electronics"]
add("What is the referral fee for Electronics?", f"{e['fee']}% today; it changes to {e['fee_new']}% for orders placed from {FEE_CHANGE_DATE}. A good answer mentions both.", [ps + "fees-by-category/electronics.md", ps + "referral-fee-changes-november-2026.md"], "temporal", "seller", "hard")
add("An electronics order was placed on 31 October and shipped on 2 November. Which referral fee applies?", f"The old fee ({e['fee']}%), because the fee is based on the order date, not the shipping date.", [ps + "referral-fee-changes-november-2026.md"], "temporal", "seller", "hard")

# ---- multi-hop calculation
price = 2000
fee = price * e["fee_new"] / 100
add(f"If I sell a {price} EGP TV accessory in Electronics on 5 November on the Professional plan, seller-fulfilled, how much are ZNSouq's fees?",
    f"Referral fee {e['fee_new']}% = {fee:.2f} EGP + {VAT}% VAT {fee * VAT / 100:.2f} = {fee * (1 + VAT / 100):.2f} EGP. No closing fee on Professional; no FBZ fees.",
    [ps + "fees-by-category/electronics.md", ps + "fees-overview.md", ps + "selling-plans.md"], "calculation", "seller", "hard")
add("Is the Professional plan worth it if I sell 60 items a month?", f"Yes: Individual costs 60 x {PLANS['Individual']['per_item']} = {60 * PLANS['Individual']['per_item']} EGP in closing fees vs {PLANS['Professional']['monthly']} EGP for Professional (break-even ~40 items).",
    [ps + "selling-plans.md"], "calculation", "seller", "medium")

# ---- seller-specific overrides (multi-tenant)
ext = [s for s in sellers[1:] if s["return_overrides"] and not s["policy_conflict"]][:3]
for s in ext:
    c, days = next(iter(s["return_overrides"].items()))
    add(f"What is the return window for {CAT[c]['name']} items bought from {s['store_name']}?",
        f"{days} days: {s['store_name']} offers an extended window (ZNSouq minimum is {CAT[c]['ret']} days).",
        [f"sellers/{s['seller_id']}", pb + f"returns-by-category/{c}.md"], "seller_override", difficulty="hard")
std = [s for s in sellers[1:] if not s["return_overrides"] and not s["policy_conflict"] and CAT[s["categories"][0]]["ret"]][0]
c = std["categories"][0]
add(f"What is the return window at {std['store_name']} for {CAT[c]['name']}?", f"{CAT[c]['ret']} days (ZNSouq standard; this seller does not extend it).",
    [f"sellers/{std['seller_id']}", pb + f"returns-by-category/{c}.md"], "seller_override", difficulty="hard")

# ---- conflict: seller page stricter than platform rules
for sid in ["S0017", "S0052"]:
    s = S[sid]; c = s["categories"][0]
    add(f"{s['store_name']} says they only accept returns within 7 days. I received an item from their {CAT[c]['name']} range 10 days ago. Can I still return it?",
        f"Yes. Sellers cannot be stricter than ZNSouq's rules; the ZNSouq minimum for {CAT[c]['name']} is "
        + (f"{CAT[c]['ret']} days, so you are still within the window (subject to the category's conditions)." if CAT[c]["ret"] else "non-returnable except damaged/expired/wrong items, so only those cases apply."),
        [f"sellers/{sid}", pb + "returns-policy.md", pb + f"returns-by-category/{c}.md"], "conflict", difficulty="hard")

# ---- product questions (multi-offer)
multi = [p for p in products if len(p["offers"]) >= 3 and p["review_count"] >= 5][:3]
for p in multi:
    cheapest = min(p["offers"], key=lambda o: o["price"])
    add(f"Who sells the {p['title']} at the lowest price?",
        f"{S[cheapest['seller_id']]['store_name']} at {fmt(cheapest['price'])} EGP ({cheapest['condition']}, fulfilled by {'ZNSouq' if cheapest['fulfillment'] == 'FBZ' else 'seller'}). Offers: "
        + "; ".join(f"{S[o['seller_id']]['store_name']} {fmt(o['price'])} EGP" for o in p["offers"]),
        [f"catalog/products.jsonl#{p['product_id']}"], "product", difficulty="medium")
p = next(x for x in products if x["product_type"] == "Smart TV")
add(f"What's in the box with the {p['title']}, and is the wall bracket included?", f"In the box: {p['in_the_box']}. The wall bracket is not included.",
    [f"catalog/products.jsonl#{p['product_id']}"], "product", difficulty="medium")
p = next(x for x in products if x["product_type"] == "Split Air Conditioner")
add(f"Does the {p['title']} include installation?", "No. Installation is not included; book an authorized technician (approx. 1,200-1,800 EGP).",
    [f"catalog/products.jsonl#{p['product_id']}"], "product", difficulty="medium")

# ---- review summarization
rv = [p for p in products if p["review_count"] >= 15][:2]
for p in rv:
    add(f"What do customers say about the {p['title']}?", f"Summary of {p['review_count']} reviews, average {p['rating']} stars. Should mention common positives and negatives and not invent reviews.",
        [f"catalog/reviews.jsonl#{p['product_id']}"], "reviews", difficulty="hard")

# ---- needs a tool, not RAG
add("Where is my order ZN-48213377?", "The knowledge base cannot answer this: order status is live per-customer data. The bot should say it can't look up orders (or call an order-lookup tool on Day 2) and point to Orders in the app or customer service.",
    [], "needs_tool", difficulty="hard")
# ---- out of scope / unanswerable
add("Do you sell PlayStation 5 consoles?", "Should not invent products; answer only from the catalog (none of the catalog's brands is PlayStation) and suggest searching the site.", [], "unanswerable", difficulty="hard")
add("What is the capital of France?", "Out of scope: politely say it can only help with ZNSouq shopping and selling questions.", [], "out_of_scope")
add("Can I pay with Bitcoin?", "Not supported: payment methods are cards (Visa/Mastercard), Meeza, ZNSouq Wallet, cash on delivery, installments via ZNPay, and gift cards.", [pb + "payment-methods.md"], "unanswerable", difficulty="medium")

os.makedirs(f"{OUT}/eval", exist_ok=True)
with open(f"{OUT}/eval/questions.jsonl", "w") as f:
    for q in Q:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")
print(len(Q), "eval questions")
