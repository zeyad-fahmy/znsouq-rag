from common import *


def build():
    # ---- Delivery by governorate (27 docs)
    for gov, z in GOV_ZONE.items():
        d = ZONES[z]
        exp = f"Express: {d['exp']} ({d['exp_fee']} EGP)." if d["exp"] else "Express delivery is not available."
        if z == "D":
            free = "Free standard delivery threshold does not apply in Zone D; Plus members still get free standard delivery on FBZ items."
            cod = ("Cash on delivery is not available." if gov == "North Sinai"
                   else f"Cash on delivery is available for orders up to {fmt(COD_ZONE_D_MAX)} EGP ({COD_FEE} EGP fee).")
            returns = "Returns: drop-off at a pickup point only (no courier pickup)."
        else:
            free = f"Free standard delivery on Fulfilled by ZNSouq orders of {FREE_SHIP_THRESHOLD} EGP or more."
            cod = f"Cash on delivery is available for orders up to {fmt(COD_MAX)} EGP ({COD_FEE} EGP fee; free for Plus members)."
            returns = "Returns: free courier pickup from your address, or drop-off at a pickup point."
        bulky = "150 EGP" if z != "D" else "300 EGP"
        note = GOV_NOTES.get(gov, "")
        write_doc(f"platform/buyer/delivery-by-governorate/{gov.lower().replace(' ', '-')}.md",
                  f"Delivery to {gov}", "buyer", f"""
{gov} is in **delivery Zone {z}**.

- Standard delivery (Fulfilled by ZNSouq): {d['std_days']} business days, {d['std_fee']} EGP.
- {exp}
- {free}
- Large and bulky items: {bulky}, delivered within 3-7 business days.
- {cod}
- {returns}
- Seller-fulfilled items: add the seller's handling time (usually 1-{HANDLING_MAX_DAYS} business days) to the transit time; shipping fees are set by the seller.
{('- ' + note) if note else ''}
""", doc_type="delivery", extra={"governorate": gov, "zone": z})

    # ---- Returns by category (16 docs)
    for c in CATEGORIES:
        nr = "\n".join(f"- {x}" for x in c["non_returnable"]) or "- None beyond the general rules."
        window = (f"{c['ret']} days from delivery" if c["ret"]
                  else "No change-of-mind returns. Damaged, expired or wrong items must be reported within 48 hours of delivery.")
        warranty = f"{c['warranty']} months (if the listing does not state otherwise)" if c["warranty"] else "No default warranty"
        report = (f"Report damage or wrong items within {DAMAGE_REPORT_HOURS} hours of delivery."
                  if c["slug"] in ("grocery", "home-appliances")
                  else f"Report damaged or wrong items within {DEFECT_REPORT_DAYS} days of delivery; defects any time within the return window.")
        if c["slug"] == "home-appliances":
            report = (f"Large appliances (refrigerators, washing machines, air conditioners, ovens): report damage within "
                      f"{DAMAGE_REPORT_HOURS} hours of delivery. Small appliances: within {DEFECT_REPORT_DAYS} days.")
        write_doc(f"platform/buyer/returns-by-category/{c['slug']}.md", f"Returns: {c['name']}", "buyer", f"""
Applies to all {c['name']} items on ZNSouq ({c['examples']}), from any seller. Sellers may offer more generous terms on their store page, never stricter ones.

- **Minimum return window**: {window}
- **Change-of-mind returns**: {c['change_of_mind']}
- **Damaged/defective/wrong items**: {report}
- **Default warranty**: {warranty}

## Not returnable (unless defective, damaged or wrong)
{nr}
""", doc_type="returns", extra={"category": c["name"]})

    # ---- Seller fees by category (16 docs)
    for c in CATEGORIES:
        ex_price = 1000
        old_fee = max(ex_price * c["fee"] / 100, MIN_REFERRAL_FEE)
        new_fee = max(ex_price * c["fee_new"] / 100, MIN_REFERRAL_FEE)
        change = (f"**Changes on {FEE_CHANGE_DATE}**: {c['fee']}% -> {c['fee_new']}% (based on order date)."
                  if c["fee"] != c["fee_new"] else "No change scheduled.")
        gated = ("Yes. Approval required before listing (see \"Gated Categories\")." if c["gated"] else "No")
        write_doc(f"platform/seller/fees-by-category/{c['slug']}.md", f"Seller Fees: {c['name']}", "seller", f"""
- **Referral fee**: {c['fee']}% of the total sale price, minimum {MIN_REFERRAL_FEE} EGP per item.
- {change}
- **Gated category**: {gated}
- **Minimum return window you must offer**: {str(c['ret']) + ' days' if c['ret'] else 'not returnable (damaged/expired/wrong items only)'}
- Plus the per-item closing fee ({PLANS['Individual']['per_item']} EGP, Individual plan only), FBZ fees if applicable, and {VAT}% VAT on all fees.

## Example: 1,000 EGP sale
- Before {FEE_CHANGE_DATE}: referral fee {old_fee:.2f} EGP + VAT {old_fee * VAT / 100:.2f} EGP = {old_fee * (1 + VAT / 100):.2f} EGP
- From {FEE_CHANGE_DATE}: referral fee {new_fee:.2f} EGP + VAT {new_fee * VAT / 100:.2f} EGP = {new_fee * (1 + VAT / 100):.2f} EGP
""", doc_type="fees", extra={"category": c["name"]})
