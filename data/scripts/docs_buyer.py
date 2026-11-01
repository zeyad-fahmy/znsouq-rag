from common import *

B = "platform/buyer"
S = SUPPORT
zone_rows = "\n".join(
    f"| Zone {z} | {', '.join(d['govs'])} | {d['std_days']} business days | {d['std_fee']} EGP | "
    + (f"{d['exp']} ({d['exp_fee']} EGP)" if d['exp'] else "Not available") + " |"
    for z, d in ZONES.items())


def build():
    w = write_doc

    w(f"{B}/about-znsouq.md", "About ZNSouq", "buyer", f"""
ZNSouq is an online marketplace in Egypt. Most products on ZNSouq are sold by independent third-party sellers who run their own stores on the platform. Some products are sold directly by ZNSouq under the store name "ZNSouq Retail".

## Sold by vs. Fulfilled by
Every product page shows two lines:
- **Sold by**: the seller you are buying from. The seller sets the price, the product description and (within ZNSouq rules) their own store policies such as a longer return window or a store warranty.
- **Fulfilled by**: who stores, packs and ships the item.
  - **Fulfilled by ZNSouq (FBZ)**: the item is stored in a ZNSouq warehouse and delivered by ZNSouq. FBZ items are eligible for free shipping over {FREE_SHIP_THRESHOLD} EGP, Plus benefits and express delivery.
  - **Fulfilled by seller**: the seller ships the item using their own courier. Delivery time is the seller's handling time plus transit time, and the seller sets the shipping fee.

## Who is responsible for what
- ZNSouq is responsible for: payments, the ZNSouq Guarantee, delivery of FBZ orders, refunds, and enforcing marketplace rules.
- Sellers are responsible for: product accuracy, stock, shipping of seller-fulfilled orders, store warranties, and answering product questions.

## Buyer protection
Every order placed on ZNSouq, no matter which seller you buy from, is covered by the ZNSouq Guarantee (up to {fmt(GUARANTEE_MAX)} EGP per order). See "ZNSouq Guarantee".

## Contact
Customer service: {S['buyer_phone']} ({S['buyer_hours']}) or {S['buyer_email']}.
""", doc_type="overview")

    w(f"{B}/creating-an-account.md", "Creating and Managing Your Account", "buyer", f"""
## Creating an account
You can sign up with a mobile number (Egyptian numbers only) or an email address. A one-time password (OTP) is sent to verify your number. You must be at least 18 years old to create an account and place orders.

## Saved addresses
You can save up to 10 delivery addresses. Each address needs a governorate, city/area, street, building number and a mobile number for the courier. Delivery zone and delivery fees are calculated from the governorate of the address.

## Changing your mobile number or email
Go to Account > Login & Security. Changing your mobile number requires an OTP sent to both the old and the new number. If you no longer have the old number, contact customer service with your national ID for manual verification (takes 1-2 business days).

## Closing your account
You can request account closure from Account > Login & Security > Close account. Closure is permanent and takes up to 7 days. Before closing:
- Any open orders, returns or Guarantee claims must be completed.
- ZNSouq Wallet balance must be used or withdrawn (wallet balances below 10 EGP are forfeited).
- An active Plus membership is cancelled; see "ZNSouq Plus" for refund rules.
""")

    w(f"{B}/placing-an-order.md", "Placing an Order", "buyer", f"""
1. Add items to your cart. Items from different sellers can be in the same cart; they may arrive in separate packages and on different days.
2. Choose a delivery address. Delivery options and fees are calculated per seller and per fulfillment type.
3. Choose a delivery speed (Standard or Express, where available) for each shipment.
4. Choose a payment method: card, Meeza, ZNSouq Wallet, cash on delivery, installments, or gift card balance.
5. Apply a coupon if you have one (one coupon per order).
6. Place the order. You receive an order confirmation by SMS and email with an order number in the format ZN-XXXXXXXX.

## Quantity limits
Some items, especially deals and high-demand products, have a maximum quantity per customer, shown on the product page. Orders that try to bypass limits (for example several accounts with the same address) may be cancelled.

## Prices
Prices are set by sellers and include VAT. If a price is clearly wrong because of a listing error (for example a laptop listed at 10 EGP), ZNSouq or the seller may cancel the order and you receive a full refund.
""")

    w(f"{B}/fulfilled-by-znsouq-vs-seller.md", "Fulfilled by ZNSouq vs. Fulfilled by Seller", "buyer", f"""
| | Fulfilled by ZNSouq (FBZ) | Fulfilled by seller |
|---|---|---|
| Who ships | ZNSouq couriers | Seller's courier |
| Delivery time | Zone transit time only (see "Delivery Options and Fees") | Seller handling time (1-{HANDLING_MAX_DAYS} business days, up to 5 if stated on the listing) + transit time |
| Shipping fee | ZNSouq delivery fees; free over {FREE_SHIP_THRESHOLD} EGP (standard, Zones A-C) | Set by the seller, shown at checkout |
| Express delivery | Available in Zones A-C | Not available |
| Plus benefits | Yes | No |
| Cash on delivery | Yes | Only if the seller offers it |
| Returns | Free pickup or drop-off at a pickup point | Return to the seller's address; the seller provides a prepaid label or refunds return shipping for defective items |
| Who handles refunds | ZNSouq | Seller, within 2 business days of receiving the return (ZNSouq steps in if they don't) |

You can filter search results by "Fulfilled by ZNSouq". When a product has several sellers, the "Other sellers" section shows each seller's price, delivery estimate and fulfillment type.
""")

    w(f"{B}/delivery-options-and-fees.md", "Delivery Options and Fees", "buyer", f"""
Delivery time and fees depend on the governorate of your delivery address. Egypt's 27 governorates are grouped into four delivery zones. The times below are for **Fulfilled by ZNSouq** items; seller-fulfilled items add the seller's handling time.

| Zone | Governorates | Standard delivery | Standard fee | Express delivery |
|---|---|---|---|---|
{zone_rows}

## Notes
- Business days are Saturday to Thursday. Friday and official public holidays are not delivery days.
- Free standard delivery on FBZ orders of {FREE_SHIP_THRESHOLD} EGP or more in Zones A, B and C. Zone D orders always pay the delivery fee unless you are a Plus member.
- Orders from several sellers are charged delivery per shipment.
- Large and bulky items (refrigerators, washing machines, furniture over 30 kg) have a fixed delivery fee of 150 EGP in Zones A-C and 300 EGP in Zone D, and are delivered within 3-7 business days in all zones. Basic installation is not included unless the listing says so.
- For coverage details for a specific governorate, see the governorate pages under "Delivery by Governorate".
""")

    w(f"{B}/free-shipping.md", "Free Shipping", "buyer", f"""
You get free **standard** delivery when:
- Your order contains Fulfilled by ZNSouq items worth {FREE_SHIP_THRESHOLD} EGP or more (after discounts, before delivery fee), **and**
- The delivery address is in Zone A, B or C.

Plus members get free standard delivery on all FBZ orders with no minimum, in all zones including Zone D, and free express delivery in Zones A and B.

Free shipping does **not** apply to:
- Seller-fulfilled items (some sellers offer their own free shipping; this is shown on the listing).
- Large and bulky items (fixed fee, see "Delivery Options and Fees").
- Express delivery for non-Plus members.

If you return items and the remaining order falls below {FREE_SHIP_THRESHOLD} EGP, the delivery fee is **not** charged back to you.
""")

    w(f"{B}/tracking-your-order.md", "Tracking Your Order", "buyer", f"""
Go to Orders and select the order to see the status of each shipment:
1. **Confirmed**: the order was placed and payment authorized.
2. **Processing**: the seller or the ZNSouq warehouse is preparing the item.
3. **Shipped**: the item was handed to the courier. A tracking number is shown.
4. **Out for delivery**: the courier will deliver today; you receive an SMS with the courier's phone number.
5. **Delivered**.

## Delivery attempts
The courier makes up to 3 delivery attempts on 3 different business days. After 3 failed attempts the item is returned to the seller or warehouse and prepaid orders are fully refunded, including the delivery fee. Repeated refused cash-on-delivery orders may lead to cash on delivery being disabled on your account.

## My order is late
If your order has not arrived by the latest estimated delivery date, wait 1 extra business day, then contact the seller (for seller-fulfilled orders) or customer service (for FBZ orders). If it still hasn't arrived {GUARANTEE_WAIT_DAYS} days after the latest estimated delivery date, you can file a ZNSouq Guarantee claim.
""")

    w(f"{B}/cancelling-an-order.md", "Cancelling an Order", "buyer", f"""
## Before the item ships
You can cancel any item for free from Orders > Cancel item while its status is Confirmed or Processing. Refunds for prepaid orders follow the refund timelines in "Refunds".

## After the item ships
You can no longer cancel. You can either refuse the delivery (cash on delivery orders) or accept it and request a return.
- Refusing a prepaid delivery: you get a full refund once the item returns to the seller or warehouse, minus the delivery fee you paid.
- Refusing a cash on delivery order is free, but 3 refused COD orders within 6 months disable cash on delivery on your account for 90 days.

## Seller cancellations
Sellers may cancel an order if the item is out of stock or the price was a clear error. You receive a full refund automatically and an email explaining the reason. Sellers with high cancellation rates are penalized by ZNSouq.

## Plus and installment orders
Cancelling an installment order cancels the installment plan; no admin fee is charged if the item had not shipped.
""")

    w(f"{B}/cash-on-delivery.md", "Cash on Delivery (COD)", "buyer", f"""
- Cash on delivery is available for orders up to {fmt(COD_MAX)} EGP.
- A COD fee of {COD_FEE} EGP is added per shipment. Plus members do not pay the COD fee.
- In Zone D (Red Sea, South Sinai, North Sinai, Matrouh, New Valley), COD is limited to orders up to {fmt(COD_ZONE_D_MAX)} EGP, and COD is **not available at all in North Sinai**.
- For seller-fulfilled items, COD is only available if the seller offers it.
- The courier accepts cash in Egyptian pounds only and may not have change for amounts above 200 EGP. Card payment at the door is available in Cairo, Giza and Alexandria.
- You can open the outer package to check the item is the correct one before paying, but you cannot open sealed product packaging or test the item.
- Refunds for COD orders go to your ZNSouq Wallet within 24 hours after the return is inspected, or by bank transfer within 7 business days if you request it.
- Three refused COD deliveries within 6 months disable COD on your account for 90 days.
""")

    w(f"{B}/payment-methods.md", "Payment Methods", "buyer", f"""
ZNSouq accepts:
- **Credit and debit cards**: Visa and Mastercard issued in any country. Cards are charged when the order is placed.
- **Meeza cards**.
- **ZNSouq Wallet** balance.
- **Cash on delivery** (see "Cash on Delivery").
- **Installments** through ZNSouq's partner ZNPay, for orders of {fmt(INSTALLMENT_MIN)} EGP or more (see "Installments").
- **Gift cards** (redeemed into your Wallet).

You can split a payment between Wallet balance and one other method. You cannot split between two cards.

## Failed payments
If a card payment fails but money was deducted, the amount is an authorization hold and is released by your bank automatically within 7 business days. ZNSouq cannot release it faster.

## Foreign cards
Foreign-issued cards are accepted, but the order must be delivered to an address in Egypt. Your bank may charge a currency conversion fee.
""")

    plans = "\n".join(f"| {m} months | {t} |" for m, t in INSTALLMENT_PLANS)
    w(f"{B}/installments.md", "Paying in Installments", "buyer", f"""
ZNSouq offers installments through its partner **ZNPay** on orders of {fmt(INSTALLMENT_MIN)} EGP or more.

| Plan | Cost |
|---|---|
{plans}

## Requirements
- A ZNPay account (sign up in 5 minutes inside the ZNSouq app with your national ID).
- Your approved ZNPay credit limit must cover the order value.
- Installments are not available for gift cards, grocery items or orders delivered to Zone D.

## Returns on installment orders
If you return an item, the installment plan for that item is cancelled. Installments you already paid are refunded within 14 business days. Admin fees are refunded only if the item was returned as defective or wrong.
""")

    w(f"{B}/znsouq-wallet.md", "ZNSouq Wallet", "buyer", f"""
The ZNSouq Wallet is a balance in your account that can be used to pay for orders.

## How money gets into your Wallet
- Refunds (Wallet refunds are the fastest: within 24 hours after a return is inspected).
- Redeemed gift cards.
- Cashback from promotions.

## Using and withdrawing
- Wallet balance is applied at checkout automatically unless you turn it off.
- Refund money in your Wallet can be withdrawn to an Egyptian bank account (IBAN) at any time for free; transfers take up to 7 business days.
- Gift card and cashback balance **cannot** be withdrawn, only spent.
- Promotional cashback expires 90 days after it is added. Refund and gift card balances do not expire while your account is active.
""")

    w(f"{B}/gift-cards.md", "Gift Cards", "buyer", f"""
- ZNSouq gift cards are available from {GIFT_CARD['min']} EGP to {fmt(GIFT_CARD['max'])} EGP.
- Gift cards are valid for {GIFT_CARD['validity_years']} years from the date of purchase.
- When redeemed, the balance is added to your ZNSouq Wallet and can be spent on any item sold on ZNSouq, from any seller.
- Gift card balance cannot be withdrawn as cash or transferred to another account.
- Gift cards cannot be used to buy other gift cards, and cannot be paid for with installments.
- Lost or stolen gift card codes cannot be replaced once redeemed by someone else. Contact customer service immediately if a code you bought was redeemed without your permission.
""")

    w(f"{B}/coupons-and-promotions.md", "Coupons, Deals and Sales Events", "buyer", f"""
## Coupons
- Only one coupon can be used per order.
- Coupons have a minimum order value and an expiry date, shown in the coupon terms.
- Seller coupons apply only to items sold by that seller. ZNSouq coupons apply to eligible items from all sellers unless the terms say otherwise.
- Coupons cannot be combined with Lightning Deals.
- If you return part of an order paid with a coupon, the refund is reduced proportionally by the coupon discount. If the remaining order no longer meets the coupon minimum, the coupon is not re-issued.

## Lightning Deals
Limited-time discounts with limited stock. A Lightning Deal price is reserved for 15 minutes once you add the item to your cart.

## Nile Days
ZNSouq's biggest yearly sale, held in the last two weeks of November. During Nile Days:
- Plus members get early access 24 hours before everyone else.
- Return windows for items bought during Nile Days are extended: returns are accepted until 15 January of the following year, for categories that normally allow change-of-mind returns.

## Price drops after purchase
ZNSouq does not refund the difference if a price drops after you buy.
""")

    w(f"{B}/returns-policy.md", "Returns Policy (Platform Rules)", "buyer", f"""
This page describes the ZNSouq rules that apply to **all sellers**. Category-specific rules are in "Returns by Category", and individual sellers may offer **more generous** policies on their store page.

## Return windows
Each category has a minimum return window, counted from the delivery date:

| Category | Return window | Change-of-mind returns |
|---|---|---|
""" + "\n".join(
        f"| {c['name']} | {str(c['ret']) + ' days' if c['ret'] else 'Not returnable (except damaged/expired/wrong items)'} | {c['change_of_mind']} |"
        for c in CATEGORIES) + f"""

## Sellers' own policies vs. ZNSouq minimums
- Sellers can offer a **longer** return window or extra benefits (for example free return shipping). These are shown on the seller's store page and apply to items sold by that seller.
- Sellers **cannot** offer less than ZNSouq's minimum. If a seller's store page shows a shorter return window or stricter conditions than ZNSouq's rules, **ZNSouq's rules apply** and you can still return the item within the ZNSouq window. Please report such store pages to customer service.

## Defective, damaged or wrong items
Can always be returned within the return window for a full refund including delivery fees, even in categories that do not accept change-of-mind returns. See "Damaged, Defective or Wrong Items".

## Return shipping cost
- **Defective, damaged or wrong items**: free.
- **Change of mind, Fulfilled by ZNSouq**: {RETURN_SHIPPING_FEE} EGP is deducted from your refund. Free for Plus members.
- **Change of mind, Fulfilled by seller**: depends on the seller's store policy. If the seller does not say, the buyer pays return shipping.

## Nile Days purchases
Items bought during Nile Days can be returned until 15 January of the following year (only in categories that allow change-of-mind returns).
""")

    w(f"{B}/how-to-return-an-item.md", "How to Return an Item", "buyer", f"""
1. Go to Orders, select the item and click **Return or replace**.
2. Choose a reason. Choosing "defective", "damaged" or "wrong item" requires at least one photo.
3. Choose refund or replacement (replacement only if the seller has the same item in stock).
4. Choose how to send it back:
   - **Fulfilled by ZNSouq items**: free courier pickup from your address (Zones A-C), or drop-off at any ZNSouq pickup point (all zones). Zone D: drop-off only.
   - **Seller-fulfilled items**: the seller has 2 business days to approve the request and send a return label or address. If the seller does not respond in 2 business days, the request is approved automatically and ZNSouq arranges the pickup.
5. Pack the item with all accessories, manuals, free gifts and the original packaging.

## After you send it
- FBZ returns are inspected within {INSPECTION_DAYS} business days after reaching the warehouse.
- Seller-fulfilled returns: the seller must issue the refund within 2 business days of receiving the item.
- If an item fails inspection (for example used, or missing parts), it is sent back to you and no refund is issued. You can appeal within 7 days through customer service.

## Bundled free gifts
If you return an item that came with a free gift, the gift must be returned too, otherwise its listed value is deducted from the refund.
""")

    refund_rows = "\n".join(f"| {k} | {v} |" for k, v in REFUND_TIMES.items())
    w(f"{B}/refunds.md", "Refunds", "buyer", f"""
Refunds are issued to the original payment method after the returned item passes inspection.

| Original payment method | Refund timing |
|---|---|
{refund_rows}

## What is refunded
- The item price.
- The delivery fee, **only** if the item was defective, damaged, wrong, or never delivered.
- The COD fee is not refunded, except for defective, damaged or wrong items.
- For change-of-mind returns of FBZ items, {RETURN_SHIPPING_FEE} EGP return shipping is deducted (not for Plus members).

## Refund not received?
Card refunds can take up to 10 business days to appear on your statement. If 10 business days have passed since the refund date shown in your order, contact customer service with the refund reference number (format RF-XXXXXXXX) so your bank can trace it.
""")

    w(f"{B}/damaged-defective-wrong-items.md", "Damaged, Defective or Wrong Items", "buyer", f"""
## Reporting deadlines
- **Grocery and large appliances** (refrigerators, washing machines, air conditioners, ovens): report damage, expired items or wrong items within **{DAMAGE_REPORT_HOURS} hours** of delivery. For large appliances, note visible damage on the courier's delivery receipt if possible.
- **All other categories**: report a damaged or wrong item within **{DEFECT_REPORT_DAYS} days** of delivery. Report a defect (item stops working) at any time within the category's return window.
- After the return window ends, defects are handled as a **warranty claim** (see "Warranty Claims").

## What you get
- A full refund including delivery and COD fees, **or** a free replacement if available.
- Free return pickup or drop-off.

## Evidence
Upload clear photos of the item, the damage, and the shipping label. For electronics that do not turn on, a short video helps.

## Counterfeit items
If you believe an item is counterfeit, report it under "Report a Counterfeit Item". Counterfeit reports are always eligible for a full refund and are not limited by the category return window, as long as the report is made within 90 days of delivery.
""")

    w(f"{B}/warranty-claims.md", "Warranty Claims", "buyer", f"""
Many products come with a warranty. The product page shows the warranty type and length:
- **Manufacturer warranty**: handled by the brand's authorized service centers. Keep your ZNSouq invoice; it serves as proof of purchase.
- **Seller warranty**: provided by the seller. Contact the seller through Orders > Contact seller; they must respond within 2 business days.
- **No warranty**: only the ZNSouq return window applies.

Default warranty lengths by category (if the listing does not state otherwise):
""" + "\n".join(f"- {c['name']}: {str(c['warranty']) + ' months' if c['warranty'] else 'no default warranty'}" for c in CATEGORIES) + f"""

## How the warranty and return window work together
- Inside the return window: return the defective item for a refund or replacement (faster).
- Outside the return window but inside the warranty: make a warranty claim; repairs typically take 7-21 days.

## If a seller does not honor their warranty
Open a ZNSouq Guarantee claim ("item not as described"). ZNSouq covers seller warranties for up to 12 months after delivery, even if the seller leaves ZNSouq.

## What warranties do not cover
Physical damage, liquid damage, unauthorized repairs, normal wear, and consumable parts such as batteries after 6 months (unless the listing says otherwise).
""")

    w(f"{B}/znsouq-guarantee.md", "ZNSouq Guarantee (Buyer Protection)", "buyer", f"""
The ZNSouq Guarantee protects every order on ZNSouq, whether it is sold by ZNSouq Retail or a third-party seller, up to **{fmt(GUARANTEE_MAX)} EGP per order**.

## You are covered if
1. **Item not received**: the item has not arrived {GUARANTEE_WAIT_DAYS} days after the latest estimated delivery date.
2. **Item not as described**: the item is materially different from the listing (wrong item, counterfeit, missing parts, different condition, undisclosed defects).
3. **Seller did not honor a return or warranty** that ZNSouq rules or the seller's own store policy require.

## How to file
1. First contact the seller through Orders > Contact seller and wait 2 business days.
2. If not resolved, go to Orders > Problem with order > File a ZNSouq Guarantee claim.
3. Claims must be filed within **{GUARANTEE_FILE_WINDOW} days** after the latest estimated delivery date.
4. The seller has **{GUARANTEE_SELLER_RESPONSE_H} hours** to respond. ZNSouq then decides, usually within 5 business days.

## Not covered
- Orders paid outside ZNSouq (for example a seller asking you to pay by bank transfer). **Never pay a seller outside ZNSouq.**
- Buyer's remorse in categories that do not allow change-of-mind returns.
- Damage caused by the buyer.
- Services such as installation booked directly with the seller outside ZNSouq.

## Outcome
If the claim is approved you receive a full refund including delivery fees, usually to the original payment method. You may be asked to return the item first.
""")

    w(f"{B}/znsouq-plus.md", "ZNSouq Plus Membership", "buyer", f"""
ZNSouq Plus is a paid membership.

## Price
- Monthly: {PLUS['monthly']} EGP / month
- Yearly: {PLUS['yearly']} EGP / year
- Students (with a valid university email): {PLUS['student_monthly']} EGP / month
- New members get a **{PLUS['trial_days']}-day free trial** (one trial per person, card required).

## Benefits
- Free standard delivery on all Fulfilled by ZNSouq orders, no minimum, in all zones (including Zone D).
- Free express delivery in Zones A and B; same-day delivery in Cairo and Giza for orders placed before 12:00 PM.
- No cash on delivery fee.
- Free change-of-mind return shipping on FBZ items.
- Early access to Lightning Deals (30 minutes) and to Nile Days (24 hours).
- 5% cashback in Wallet credit on ZNSouq Retail purchases, up to 300 EGP per month.

Plus benefits apply to **Fulfilled by ZNSouq** items only. Seller-fulfilled items are not included, except for the cashback rule above (which only applies to ZNSouq Retail).

## Cancelling
- Cancel anytime from Account > Plus. Monthly plans stay active until the end of the paid month; no partial refunds.
- Yearly plans: if you cancel within **{PLUS['refund_window_days']} days** of being charged and you have not used any Plus benefit, you get a full refund. Otherwise the membership stays active until the end of the year with no refund.
- Free trials can be cancelled at any time before they end without being charged.
""")

    w(f"{B}/product-reviews-policy.md", "Product Reviews and Ratings", "buyer", f"""
- Only customers who bought the product on ZNSouq can write a review ("Verified Purchase"). You can review an item from 1 day after delivery until 12 months after delivery.
- Reviews rate the **product**. A separate **seller rating** (1-5 stars) rates the seller's service: delivery, packaging and communication.
- Reviews must not include: personal information, links, offensive language, or content about price or delivery (use seller feedback for that).
- Sellers may not offer refunds, gifts or discounts in exchange for reviews, and may not ask you to change or remove a negative review. Report such requests to customer service; the seller can be suspended.
- ZNSouq removes reviews that break these rules. Removal usually happens within 72 hours of being reported.
- A product's star rating is the average of all approved reviews across all sellers of the same product.
""")

    w(f"{B}/report-a-counterfeit-item.md", "Report a Counterfeit Item", "buyer", f"""
ZNSouq has a zero-tolerance policy for counterfeit products.

## How to report
Go to Orders > select the item > Problem with order > "Item is counterfeit". Add photos showing why you believe it is not genuine (logo, serial number, packaging, comparison with an original).

## What happens
- You receive a full refund after the item is returned, including delivery fees, even if the normal return window has ended (reports accepted up to 90 days after delivery).
- ZNSouq investigates the seller. Sellers found selling counterfeits are permanently removed and their payouts may be withheld.
- For brand owners: see "Brand Registry and IP Complaints" in the seller help center.
""")

    w(f"{B}/contacting-a-seller.md", "Contacting a Seller", "buyer", f"""
You can message any seller from the product page ("Ask a question") or from Orders > Contact seller.
- Sellers must reply within 24 hours on business days.
- All communication must stay on ZNSouq messaging. Sellers are not allowed to ask for your phone number, WhatsApp, or for payment outside ZNSouq.
- Messages are monitored for fraud and abuse.
- If a seller does not reply within 2 business days about an order problem, you can file a ZNSouq Guarantee claim.
""")

    w(f"{B}/pickup-points.md", "ZNSouq Pickup Points", "buyer", f"""
ZNSouq pickup points are partner shops and lockers where you can collect orders and drop off returns.
- There are pickup points in all 27 governorates. In Zone D, pickup points are the main return option.
- Pickup is free of charge.
- Orders stay at a pickup point for 5 days. After that they are returned and you receive a refund (minus any delivery fee for prepaid orders).
- You need the pickup code sent by SMS and your national ID.
- Large and bulky items cannot be delivered to pickup points.
""")

    w(f"{B}/account-security-and-scams.md", "Account Security and Avoiding Scams", "buyer", f"""
- ZNSouq will **never** ask for your password, OTP code or full card number by phone, SMS, WhatsApp or email.
- ZNSouq customer service only calls from {S['buyer_phone']}. Calls or messages from other numbers claiming to be ZNSouq are scams.
- Never pay a seller outside ZNSouq (bank transfer, InstaPay, mobile wallet). Payments outside ZNSouq are **not covered** by the ZNSouq Guarantee.
- Enable two-step verification in Account > Login & Security.
- If you see an order you didn't place, change your password immediately and contact customer service. Unauthorized orders reported within 48 hours are cancelled and refunded.
""")

    w(f"{B}/privacy-summary.md", "Privacy Summary", "buyer", f"""
This is a short summary of how ZNSouq handles your data.
- ZNSouq collects account details, addresses, orders, payment tokens (not full card numbers), device information and support conversations.
- Sellers receive only the information needed to fulfill your order: name, delivery address and phone number for seller-fulfilled orders. Sellers may not use your data for marketing.
- Data is stored in line with Egypt's Personal Data Protection Law.
- You can download your data or request deletion from Account > Privacy. Order records are kept for 5 years for tax purposes even after account deletion.
- Marketing messages can be turned off in Account > Notifications.
""")

    w(f"{B}/contact-customer-service.md", "Contact Customer Service", "buyer", f"""
- **Phone**: {S['buyer_phone']}, {S['buyer_hours']}
- **Live chat**: in the ZNSouq app and website, 24/7 (automated assistant; human agents during phone hours)
- **Email**: {S['buyer_email']} (reply within 24 hours)
- **Head office (no walk-in support)**: {S['hq']}

For order problems, have your order number (ZN-XXXXXXXX) ready. For refund questions, have the refund reference (RF-XXXXXXXX).

For questions about a specific product or a seller's store policy, contact the seller first via Orders > Contact seller.
""", doc_type="contact")
