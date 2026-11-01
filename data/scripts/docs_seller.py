from common import *

D = "platform/seller"
S = SUPPORT


def build():
    w = write_doc
    fee_rows = "\n".join(
        f"| {c['name']} | {c['fee']}% | {c['fee_new']}%{' (changed)' if c['fee'] != c['fee_new'] else ''} |"
        for c in CATEGORIES)
    tier_rows = "\n".join(f"| {n} | {d} | {fee} EGP |" for n, d, fee in FBZ_TIERS)

    w(f"{D}/start-selling-on-znsouq.md", "Start Selling on ZNSouq", "seller", f"""
ZNSouq lets businesses and individuals in Egypt open a store and sell to millions of customers.

## Steps
1. Register and verify your business (see "Registration and Verification").
2. Choose a selling plan: Individual or Professional (see "Selling Plans").
3. List your products, or add offers to existing product pages.
4. Choose how to fulfill orders: **Fulfilled by ZNSouq (FBZ)** or **Fulfilled by seller**.
5. Set your store policies (return window, warranty, shipping) within ZNSouq rules.
6. Start selling. Payouts are sent weekly every {PAYOUT['day']}.

## What it costs
- Plan fee (0 or {PLANS['Professional']['monthly']} EGP/month)
- Referral fee per item sold (a % of the sale price, by category)
- Per-item closing fee of {PLANS['Individual']['per_item']} EGP on the Individual plan
- FBZ fees, if you use FBZ
- Optional advertising
All ZNSouq fees are subject to {VAT}% VAT.

## Seller support
{S['seller_phone']} ({S['seller_hours']}) or {S['seller_email']}.
""", doc_type="overview")

    w(f"{D}/registration-and-verification.md", "Registration and Verification", "seller", f"""
## Who can sell
- Companies registered in Egypt.
- Individuals (sole traders) aged 21 or older with an Egyptian national ID and a tax registration number.
- Foreign companies can sell only through FBZ and must have an Egyptian importer of record.

## Documents
| Seller type | Required documents |
|---|---|
| Company | Commercial registration (issued within the last 12 months), tax card, national ID of the authorized signatory, bank letter showing an Egyptian IBAN in the company name |
| Individual | National ID, tax registration number, bank account (IBAN) in your own name, utility bill showing your address |

## Verification
- Verification takes **{VERIFICATION_DAYS}** after all documents are uploaded.
- A short video call may be requested to confirm identity.
- Your store is not visible to buyers until verification is complete.
- Common rejection reasons: blurry documents, name mismatch between bank account and registration, expired commercial registration.

## After rejection
You can re-submit corrected documents at any time. After 3 rejections, the application is closed for 60 days.
""")

    plan_rows = "\n".join(f"| {k} | {v['monthly']} EGP | {v['per_item']} EGP | {v['note']} |" for k, v in PLANS.items())
    w(f"{D}/selling-plans.md", "Selling Plans", "seller", f"""
| Plan | Monthly fee | Per-item closing fee | Notes |
|---|---|---|---|
{plan_rows}

- Referral fees apply on both plans.
- Fees are before {VAT}% VAT.
- You can switch plans at any time. Upgrading to Professional takes effect immediately and the first month is charged pro rata. Downgrading takes effect at the end of the current billing month.
- If your Professional plan payment fails, you have 7 days to fix it before your account is moved to the Individual plan and your ads are paused.
- Break-even: Professional is cheaper than Individual if you sell more than about 40 items a month (40 x 10 EGP = 400 EGP).
""")

    w(f"{D}/fees-overview.md", "Seller Fees Overview", "seller", f"""
## Referral fees
A referral fee is charged on every item sold, as a percentage of the **total sale price** (item price + any shipping charged to the buyer), with a minimum of {MIN_REFERRAL_FEE} EGP per item.

| Category | Fee until 31 Oct 2026 | Fee from {FEE_CHANGE_DATE} |
|---|---|---|
{fee_rows}

See "Referral Fee Changes - November 2026" for details on the change.

## Other fees
- **Closing fee**: {PLANS['Individual']['per_item']} EGP per item on the Individual plan only.
- **Plan fee**: {PLANS['Professional']['monthly']} EGP/month on the Professional plan.
- **FBZ fees**: fulfillment, storage, long-term storage and removal (see "FBZ Fees").
- **Refund administration fee**: when you refund a buyer, ZNSouq refunds you the referral fee minus an administration fee of 20% of that referral fee (max 50 EGP per item).
- **Advertising**: cost per click, set by your bids.
- **VAT**: {VAT}% is added to all ZNSouq fees. A monthly tax invoice is issued.

## Example
A Men's Fashion shirt sold for 450 EGP with free shipping, Professional plan, seller-fulfilled, sold on 25 October 2026:
- Referral fee: 15% x 450 = 67.50 EGP
- VAT on fee: 14% x 67.50 = 9.45 EGP
- Total fees: 76.95 EGP; you receive 373.05 EGP.
The same sale on or after {FEE_CHANGE_DATE} has a 14% referral fee: 63.00 EGP + 8.82 EGP VAT = 71.82 EGP.
""")

    changed = [c for c in CATEGORIES if c["fee"] != c["fee_new"]]
    w(f"{D}/referral-fee-changes-november-2026.md", "Referral Fee Changes - November 2026", "seller", f"""
Announced: 1 October 2026. Effective: **{FEE_CHANGE_DATE}**.

The following referral fees change on {FEE_CHANGE_DATE}:
""" + "\n".join(f"- **{c['name']}**: {c['fee']}% -> {c['fee_new']}%" for c in changed) + f"""

All other categories are unchanged.

## Which fee applies to my order?
The fee is based on the date the **order is placed**, not the shipping or delivery date. An order placed on 31 October 2026 at 11:59 PM Cairo time uses the old fee, even if it ships in November.

## Why
- Electronics and mobile phones: to fund the expansion of express delivery to Zone C and the new extended return inspection centers.
- Fashion: reduced to support growth of local apparel brands.

## Fee for refunds
If an order placed before {FEE_CHANGE_DATE} is refunded after that date, the original (old) fee is used to calculate the refund administration fee.
""", updated="2026-10-01", doc_type="announcement")

    w(f"{D}/fbn-overview.md", "Fulfilled by ZNSouq (FBZ) Overview", "seller", f"""
With FBZ, you send your inventory to a ZNSouq warehouse. ZNSouq stores, picks, packs, ships, handles customer service and processes returns for those items.

## Benefits
- Your items are eligible for free shipping over {FREE_SHIP_THRESHOLD} EGP, express delivery and Plus benefits.
- Higher chance of winning the Buy Box.
- Late shipment and tracking metrics do not count against you for FBZ orders.
- ZNSouq handles returns and refunds.

## Warehouses
- **Cairo (Obour)**: all categories, including oversize.
- **Alexandria (Borg El Arab)**: all categories except heavy & bulky.
- **Assiut**: small and standard items only; opened in 2026 to speed up Zone C delivery.

## Not allowed in FBZ
Hazardous materials (aerosols over 500 ml, lithium batteries shipped alone, flammable liquids), perishable grocery requiring refrigeration, and items worth more than 150,000 EGP per unit.

See "FBZ Fees" and "FBZ Inbound Shipments and Packaging".
""")

    w(f"{D}/fbn-fees.md", "FBZ Fees", "seller", f"""
## Fulfillment fee (per unit sold)
| Size tier | Limits | Fee |
|---|---|---|
{tier_rows}

Heavy & bulky: {FBZ_TIERS[-1][2]} EGP + {HEAVY_PER_KG} EGP per kg above 20 kg. Weight is the greater of actual weight and dimensional weight (L x W x H in cm / 5000).

## Monthly storage fee (per cubic foot)
- January to September: {STORAGE_FEE['jan_sep']} EGP
- October to December: {STORAGE_FEE['oct_dec']} EGP (peak season)

## Long-term storage
Units stored more than {LONG_TERM_DAYS} days are charged an extra {LONG_TERM_SURCHARGE} EGP per cubic foot per month, assessed on the 15th of each month.

## Removal and disposal
{REMOVAL_FEE} EGP per unit for removal (returned to you) or disposal.

## Returns processing
No fee for buyer returns of FBZ items. Unsellable returns are moved to your "unfulfillable" inventory; you have 30 days to request removal before they are disposed of at the removal fee.

All fees are before {VAT}% VAT.
""")

    w(f"{D}/fbn-inbound-shipments-and-packaging.md", "FBZ Inbound Shipments and Packaging", "seller", f"""
1. Create a shipping plan in Seller Center > FBZ > Send inventory. ZNSouq assigns the warehouse.
2. Label every unit with its ZNSouq barcode (FNSKU) unless the item is enrolled in "manufacturer barcode" tracking.
3. Book a delivery slot. Missed slots can be rebooked once for free; after that, 250 EGP per missed slot.
4. Inventory is usually available for sale within 3 business days after arrival (up to 7 business days in October-December).

## Packaging rules
- Boxes must not exceed 23 kg or 63.5 cm on any side.
- Fragile items need bubble wrap and a "Fragile" label.
- Liquids must be sealed and bagged.
- Sets sold as one unit must be bundled and labeled "Sold as set".
- Apparel must be individually polybagged with a suffocation warning if the bag opening is over 12 cm.

## Problems at receiving
Units with missing or unreadable labels are labeled by ZNSouq for 5 EGP per unit. Damaged or non-compliant units are returned at your cost.
""")

    w(f"{D}/seller-fulfilled-shipping.md", "Shipping Orders Yourself (Fulfilled by Seller)", "seller", f"""
## Handling time
You must ship within **{HANDLING_MAX_DAYS} business days** of the order, or within the handling time shown on your listing (maximum 5 business days, for example for made-to-order items).

## Tracking
Every shipment must have valid tracking from a ZNSouq-integrated courier, uploaded within 24 hours of shipping. Your **valid tracking rate** must stay above {HEALTH['valid_tracking']}%.

## Shipping fees
You set your own shipping fees per zone. You may offer free shipping. ZNSouq's delivery zones (A-D) are used for your shipping templates.

## Cash on delivery
You may offer COD for seller-fulfilled orders if your courier supports it. Cash collected is reconciled to your ZNSouq balance within 5 business days of delivery; you never collect payment directly.

## Delivery promise
If you miss the latest estimated delivery date, the order counts as **late**. Buyers can file a ZNSouq Guarantee claim {GUARANTEE_WAIT_DAYS} days after the latest estimated delivery date.
""")

    w(f"{D}/payouts.md", "Payouts", "seller", f"""
- Payouts are sent every **{PAYOUT['day']}** to your registered Egyptian bank account (IBAN). There is no payout fee.
- An order's funds become available **{PAYOUT['reserve_days']} days after delivery** (the reserve period), to cover returns and claims.
- **New sellers** (first {PAYOUT['new_seller_period_days']} days after their first sale) have a **{PAYOUT['new_seller_reserve_days']}-day** reserve period instead.
- Minimum payout amount: {PAYOUT['minimum']} EGP. Balances below this roll over to the next payout.
- Bank transfers usually arrive 1-2 business days after the payout date.
- If you change your bank account, payouts are paused for 3 business days for security verification.

## Negative balance
If refunds and fees exceed your sales, your balance becomes negative. ZNSouq charges the card on file after 30 days if the balance is not covered by new sales.

## Payout holds
Payouts may be held if your account is under review, suspended, or has open ZNSouq Guarantee claims exceeding your available balance. Funds of permanently deactivated sellers are held for 90 days to cover claims, then released minus any amounts owed.
""")

    w(f"{D}/account-health.md", "Account Health", "seller", f"""
Account Health measures how well you serve buyers. Metrics are calculated over a rolling 60-day window unless noted.

| Metric | Target | What it measures |
|---|---|---|
| Order Defect Rate (ODR) | below {HEALTH['odr']}% | Orders with negative feedback (1-2 stars), a ZNSouq Guarantee claim, or a chargeback |
| Late Shipment Rate | below {HEALTH['late_shipment']}% | Seller-fulfilled orders shipped after the handling time (30-day window) |
| Pre-fulfillment Cancellation Rate | below {HEALTH['cancel']}% | Orders cancelled by the seller before shipping (7-day window) |
| Valid Tracking Rate | above {HEALTH['valid_tracking']}% | Seller-fulfilled shipments with valid tracking (30-day window) |
| Response Time | {HEALTH['response_24h']}% of messages answered within 24 hours | Buyer messages (business days only) |

FBZ orders do not count toward late shipment or tracking metrics.

## What happens if you miss a target
1. **Warning**: you receive a notification and have 14 days to improve.
2. **At risk**: listings may lose Buy Box eligibility.
3. **Deactivation**: if the ODR stays above {HEALTH['odr']}% or the cancellation rate stays above {HEALTH['cancel']}% after a warning, your account can be deactivated. See "Suspension and Appeals".

Policy violations (counterfeit, review manipulation, off-platform payments) can lead to immediate deactivation without a warning.
""")

    w(f"{D}/suspension-and-appeals.md", "Account Suspension and Appeals", "seller", f"""
## Types
- **Listing suppression**: individual listings hidden (for example missing information). Fix the listing to restore it.
- **Account suspension**: you cannot sell; listings are hidden. Funds are held.
- **Permanent deactivation**: for severe or repeated violations (counterfeit, fraud). Cannot be appealed after a final decision.

## Appealing a suspension
- Submit a **Plan of Action** within **{APPEAL_DAYS} days** of the suspension notice, in Seller Center > Account Health > Appeal.
- A Plan of Action must explain: (1) the root cause, (2) what you did to fix it, and (3) what you changed to prevent it happening again.
- ZNSouq reviews appeals within **{APPEAL_REVIEW}**.
- You can submit up to 3 appeals per suspension. If you miss the {APPEAL_DAYS}-day deadline, the suspension becomes a permanent deactivation.

## Funds during suspension
Funds are held during the suspension. If reinstated, payouts resume on the next payout day. If permanently deactivated, funds are held for 90 days (see "Payouts").
""")

    w(f"{D}/listing-policy.md", "Listing Policy", "seller", f"""
## Creating vs. matching listings
- If the product already exists on ZNSouq, you must **add your offer to the existing product page** instead of creating a duplicate. Duplicate listings are removed.
- If it doesn't exist, create a new listing with a unique barcode (GTIN/EAN). Products without a barcode require a GTIN exemption (approved within 2 business days).

## Requirements
- Title: max 200 characters, format "Brand + Model + Key attribute + Size/Color". No promotional words ("Best", "Sale", "Free shipping").
- Main image: white background, product fills 85% of the image, at least 1000 x 1000 pixels, no logos or text.
- Accurate condition: New, Renewed (refurbished with at least 6 months seller warranty), or Used (allowed only in Books, Electronics and Sports).
- Prices must include VAT. Prices more than 50% above the recent lowest price on ZNSouq are blocked as "unfair pricing".

## Variations
Use one parent listing for products that differ only in size or color (for example a t-shirt in 5 sizes and 3 colors).

## Product compliance
Electronics and appliances need Egyptian standards compliance where required. Mobile phones need NTRA type approval (see "Gated Categories").
""")

    gated = [c for c in CATEGORIES if c["gated"]]
    w(f"{D}/gated-categories.md", "Gated Categories (Approval Required)", "seller", f"""
Some categories require approval before you can list products:
""" + "\n".join(f"- **{c['name']}**" for c in gated) + f"""

## Requirements
- **Mobile Phones & Tablets**: proof of authorized distribution (invoice from the brand or an authorized distributor within the last 180 days) and NTRA type approval for every device model. Accessories (cases, chargers) do not need approval.
- **Health & Nutrition**: a valid license from the Egyptian Drug Authority (EDA) for supplements; medical devices need EDA registration. Medicines are prohibited.
- **Grocery**: a food safety license from the National Food Safety Authority (NFSA); products must have at least 60 days of shelf life when received at the FBZ warehouse (or when shipped, for seller-fulfilled).

## How to apply
Seller Center > Catalog > Request approval. Decisions take up to 5 business days. You must be on the Professional plan to apply.
""")

    w(f"{D}/prohibited-and-restricted-items.md", "Prohibited and Restricted Items", "seller and buyer", f"""
## Prohibited (cannot be sold on ZNSouq)
- Prescription and over-the-counter medicines
- Weapons, ammunition, and knives with blades over 15 cm (kitchen knives allowed)
- Drugs and drug paraphernalia, tobacco and e-cigarettes
- Counterfeit or replica products
- Recalled products
- Live animals
- Used underwear, used cosmetics
- Gift cards from other retailers
- Products requiring a license the seller doesn't have
- Drones with cameras (require Ministry of Defense approval in Egypt)

## Restricted (allowed with conditions)
- Supplements and medical devices: Health & Nutrition approval
- Mobile phones: NTRA approval
- Food: NFSA license
- Lithium batteries: only inside or with the device
- Laser pointers: under 5 mW only

Listings of prohibited items are removed. Repeated violations lead to account deactivation.
""")

    w(f"{D}/buy-box.md", "The Buy Box", "seller", f"""
When several sellers offer the same product, one offer is shown in the **Buy Box** (the "Add to cart" button). Other offers appear under "Other sellers".

## Eligibility
- Professional plan
- Account health metrics in good standing
- At least 90 days of selling history or Rising Star tier

## What influences who wins
- Total price (item price + shipping)
- Fulfillment method (FBZ offers are favored)
- Delivery speed
- Seller rating and Order Defect Rate
- Stock availability

The Buy Box can rotate between sellers with similar offers. There is no way to pay for the Buy Box.
""")

    w(f"{D}/advertising-sponsored-products.md", "Advertising: Sponsored Products", "seller", f"""
- Available on the **Professional** plan only.
- Cost per click (CPC): you pay only when a buyer clicks your ad. Minimum bid {ADS_MIN_BID:.2f} EGP.
- Set a daily budget (minimum 50 EGP/day). ZNSouq may spend up to 20% more on a single day but never more than your monthly total (daily budget x days in month).
- Ads are only shown for offers that are in stock and currently win the Buy Box.
- Ad charges are deducted from your seller balance; if the balance is insufficient, the card on file is charged.
- Ads are labeled "Sponsored" to buyers.
""")

    w(f"{D}/promotions-and-deals.md", "Promotions and Deals for Sellers", "seller", f"""
## Seller coupons
Create percentage or fixed-amount coupons for your own products. You pay the full discount. Minimum discount 5%.

## Lightning Deals
- Apply in Seller Center > Deals. Lightning Deal fee: 300 EGP per deal (1,000 EGP during Nile Days).
- The deal price must be at least 15% below the lowest price of the item in the last 30 days.
- Requirements: Professional plan, store rating 4.0+, and at least 3 product reviews with an average of 3.5+.

## Nile Days
ZNSouq's yearly sale in the last two weeks of November. Submissions open 6 weeks before. During Nile Days, items have an extended return window (until 15 January of the following year) and you cannot opt out of it.
""")

    w(f"{D}/handling-returns-as-a-seller.md", "Handling Returns as a Seller", "seller", f"""
## FBZ orders
ZNSouq handles return requests and refunds. Returned units are inspected; sellable units go back to your inventory, unsellable units to "unfulfillable".

## Seller-fulfilled orders
- You must **approve or respond** to a return request within **2 business days**. If you don't, it is approved automatically and ZNSouq arranges a pickup charged to you.
- You must issue the refund within **2 business days** of receiving the returned item.
- For defective, damaged or wrong items, you pay return shipping.
- You may deduct up to 50% of the item price for items returned used, damaged by the buyer, or missing parts, with photo evidence.

## Return window rules
- You must accept returns for at least ZNSouq's minimum window in each category (see "Returns Policy" in the buyer help center).
- You may offer a longer window; it then applies to all your sales in that category and must be shown on your store page.
- A store policy that is stricter than ZNSouq's rules is not valid. ZNSouq will apply its own rules and may suppress your store page until it is corrected.

## Refund administration fee
When you refund an order, ZNSouq refunds your referral fee minus 20% of it (max 50 EGP per item).
""")

    w(f"{D}/guarantee-claims-for-sellers.md", "ZNSouq Guarantee Claims (Seller Guide)", "seller", f"""
- When a buyer files a ZNSouq Guarantee claim, you have **{GUARANTEE_SELLER_RESPONSE_H} hours** to respond in Seller Center > Performance > Guarantee claims.
- You can: offer a full refund, provide proof of delivery or tracking, or explain why the claim is not valid.
- If you don't respond within {GUARANTEE_SELLER_RESPONSE_H} hours, ZNSouq usually decides in the buyer's favor.
- Claims decided against you count toward your Order Defect Rate and the amount is deducted from your balance.
- Claims withdrawn by the buyer, or decided in your favor, do not count toward ODR.
- FBZ orders: claims about delivery are handled by ZNSouq and do not affect your ODR.
- You can appeal a decision once, within 30 days, with new evidence.
""")

    w(f"{D}/store-policies-what-sellers-can-set.md", "Your Store Page and Store Policies", "seller", f"""
Your store page shows buyers your store name, logo, description, rating and **store policies**.

## What you can set
- Return window per category: equal to or **longer** than ZNSouq's minimum.
- Who pays return shipping for change-of-mind returns.
- A store warranty (in months) in addition to any manufacturer warranty.
- Handling time (1-{HANDLING_MAX_DAYS} business days, or up to 5 per listing).
- Shipping fees per zone (seller-fulfilled only).
- Whether you offer cash on delivery (seller-fulfilled only).

## What you cannot set
- A shorter return window or stricter conditions than ZNSouq's rules.
- Restocking fees on unopened items.
- Requirements to contact you outside ZNSouq.

If your store page conflicts with ZNSouq rules, **ZNSouq's rules take priority** for buyers, and your store page may be suppressed until corrected.
""")

    tier_rows2 = "\n".join(f"| {n} | {req} |" for n, req in SELLER_TIERS)
    w(f"{D}/seller-tiers.md", "Seller Tiers", "seller", f"""
| Tier | Requirements |
|---|---|
{tier_rows2}

## Benefits
- **Rising Star**: Buy Box eligibility before 90 days of history, a "Rising Star" badge, and a 10% discount on Lightning Deal fees.
- **Top Seller**: "Top Seller" badge, a dedicated account manager, 20% discount on Lightning Deal fees, and payouts with a 3-day reserve instead of {PAYOUT['reserve_days']} days.

Tiers are re-evaluated on the 1st of every month.
""")

    w(f"{D}/invoices-and-vat.md", "Invoices and VAT", "seller", f"""
- ZNSouq issues a monthly tax invoice for all fees charged to you, including {VAT}% VAT, available in Seller Center > Reports > Tax documents by the 5th of the following month.
- **You** are responsible for issuing a sales invoice to the buyer. VAT-registered sellers must issue e-invoices / e-receipts through the Egyptian Tax Authority (ETA) system; ZNSouq's ETA integration can do this automatically for Professional sellers.
- For FBZ orders, ZNSouq includes a packing slip but the tax invoice is issued in your name.
- Prices shown to buyers must include VAT.
""")

    w(f"{D}/brand-registry-and-ip-complaints.md", "Brand Registry and IP Complaints", "seller", f"""
## Brand Registry
Brand owners with a trademark registered in Egypt (or a pending application) can enroll in Brand Registry for free. Benefits:
- Control over product titles, images and descriptions for your brand.
- Tools to report counterfeit and infringing listings.
- A "Brand Store" page.

## Reporting infringement
Submit a report in Seller Center > Brand Registry > Report a violation. Reports are reviewed within 3 business days.

## If you receive an IP complaint
The listing is removed. You can contact the rights owner to request a retraction, or submit proof of authenticity (invoices from the brand or an authorized distributor). Three valid IP complaints within 180 days can lead to account deactivation.
""")

    w(f"{D}/contact-seller-support.md", "Contact Seller Support", "seller", f"""
- **Phone**: {S['seller_phone']}, {S['seller_hours']}
- **Email**: {S['seller_email']} (reply within 1 business day)
- **Seller Center**: Help > Open a case (fastest; available 24/7)
- **Seller University**: free online training videos in Seller Center > Learn

Top Sellers have a dedicated account manager.
""", doc_type="contact")
