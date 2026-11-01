import json, random, re, os
from datetime import date, timedelta
from common import *
from catalog_defs import *

random.seed(42)
N_SELLERS = 100
N_PRODUCTS = 5000
CAT_WEIGHTS = {"electronics": 10, "mobile-phones": 9, "computers": 7, "home-appliances": 6, "home-kitchen": 8,
               "fashion-men": 8, "fashion-women": 9, "kids-baby": 5, "beauty": 7, "health": 4, "sports": 5,
               "toys": 4, "books": 4, "grocery": 5, "automotive": 4, "pet-supplies": 3}
GOV_WEIGHTS = {"Cairo": 30, "Giza": 15, "Alexandria": 15, "Qalyubia": 5, "Dakahlia": 5, "Gharbia": 4, "Sharqia": 4,
               "Damietta": 4, "Port Said": 3, "Ismailia": 2, "Asyut": 3, "Minya": 2, "Sohag": 2, "Luxor": 2, "Red Sea": 2, "Aswan": 2}
TODAY_D = date(2026, 10, 30)


def wchoice(d):
    return random.choices(list(d), weights=list(d.values()))[0]


def rdate(a, b):
    return a + timedelta(days=random.randint(0, (b - a).days))


# ======================= SELLERS =======================
def make_sellers():
    sellers = [dict(seller_id="S0000", store_name="ZNSouq Retail", categories=[c["slug"] for c in CATEGORIES],
                    governorate="Cairo", joined="2019-03-01", plan="Professional", fulfillment="FBZ", tier="Top Seller",
                    rating=4.7, rating_count=184230, handling_days=None, cod=True, return_overrides={},
                    change_of_mind_shipping="ZNSouq standard rules", store_warranty_months=0, ships_zone_d=True,
                    shipping_fees=None, free_shipping_over=None, policy_conflict=False,
                    metrics=dict(odr=0.3, late_shipment=0.0, cancel=0.4, valid_tracking=100.0, response_24h=99.0),
                    description="ZNSouq Retail is ZNSouq's own store. All items are Fulfilled by ZNSouq.")]
    names = set()
    conflict_ids = {"S0017", "S0052", "S0088"}  # store pages with policies stricter than ZNSouq rules (on purpose)
    for i in range(1, N_SELLERS + 1):
        sid = f"S{i:04d}"
        cat = wchoice(CAT_WEIGHTS)
        cats = [cat]
        if random.random() < 0.3:
            other = wchoice(CAT_WEIGHTS)
            if other != cat:
                cats.append(other)
        while True:
            name = f"{random.choice(STORE_WORDS_A)} {random.choice(CAT_STORE_HINT[cat] + STORE_WORDS_B)}"
            if name not in names:
                names.add(name); break
        is_new = random.random() < 0.12
        joined = rdate(date(2026, 8, 5), date(2026, 10, 10)) if is_new else rdate(date(2019, 6, 1), date(2026, 4, 30))
        fulfillment = random.choices(["FBZ", "Seller", "Both"], weights=[35, 40, 25])[0]
        if any(CAT[c].get("slug") in ("grocery",) for c in cats) and fulfillment == "Seller" and random.random() < 0.5:
            fulfillment = "Both"
        plan = "Professional" if random.random() < 0.75 else "Individual"
        rating = round(min(4.9, max(3.2, random.gauss(4.4, 0.35))), 1)
        if is_new:
            tier = "Standard"
        else:
            r = random.random()
            tier = "Top Seller" if (r < 0.08 and rating >= 4.7 and plan == "Professional") else (
                "Rising Star" if (r < 0.3 and rating >= 4.5) else "Standard")
        overrides = {}
        for c in cats:
            base = CAT[c]["ret"]
            if base and fulfillment != "FBZ" and random.random() < 0.4:
                overrides[c] = {15: random.choice([30, 30, 45]), 14: 30, 30: random.choice([45, 60])}[base]
        conflict = sid in conflict_ids
        seller_ships = fulfillment in ("Seller", "Both")
        ships_d = random.random() > 0.2
        fees = None
        if seller_ships:
            fees = dict(A=random.choice([35, 40, 45, 50]), B=random.choice([45, 50, 55, 60]), C=random.choice([60, 65, 70, 80]),
                        D=random.choice([90, 110, 130, 140]) if ships_d else None)
        metrics = dict(odr=round(abs(random.gauss(0.6, 0.4)), 2), late_shipment=round(abs(random.gauss(1.8, 1.5)), 1) if seller_ships else 0.0,
                       cancel=round(abs(random.gauss(0.9, 0.8)), 1), valid_tracking=round(min(100, random.gauss(98, 1.8)), 1) if seller_ships else 100.0,
                       response_24h=round(min(100, random.gauss(94, 4)), 1))
        hint = CAT[cat]["examples"]
        desc = random.choice([
            f"{name} is a {CAT[cat]['name'].lower()} store based in {{gov}}, selling {hint}.",
            f"Family-run business from {{gov}} specializing in {hint}. Every item is checked before shipping.",
            f"Authorized reseller of leading {CAT[cat]['name'].lower()} brands in Egypt. We sell {hint}.",
            f"{name} has served customers in {{gov}} since {joined.year}. We focus on {hint} at fair prices.",
        ])
        gov = wchoice(GOV_WEIGHTS)
        sellers.append(dict(
            seller_id=sid, store_name=name, categories=cats, governorate=gov, joined=joined.isoformat(), plan=plan,
            fulfillment=fulfillment, tier=tier, rating=rating, rating_count=random.randint(15, 600) if is_new else random.randint(120, 25000),
            handling_days=(random.choice([1, 1, 2, 2, 3]) if seller_ships else None),
            cod=(random.random() < 0.7) if seller_ships else True,
            return_overrides=overrides,
            change_of_mind_shipping=random.choice(["seller pays", "buyer pays", "buyer pays"]),
            store_warranty_months=(random.choice([0, 0, 6, 12]) if cat in ("electronics", "mobile-phones", "computers", "home-appliances") else 0),
            ships_zone_d=ships_d if seller_ships else True, shipping_fees=fees,
            free_shipping_over=(random.choice([None, 750, 1000, 1500]) if seller_ships else None),
            policy_conflict=conflict, metrics=metrics, new_seller=is_new,
            description=desc.format(gov=gov)))
    return sellers


def store_page(s):
    cats = ", ".join(CAT[c]["name"] for c in s["categories"])
    lines = [f"**Store:** {s['store_name']} (seller ID {s['seller_id']})",
             f"**Categories:** {cats}", f"**Based in:** {s['governorate']}", f"**On ZNSouq since:** {s['joined']}",
             f"**Seller rating:** {s['rating']} / 5 from {fmt(s['rating_count'])} ratings", f"**Seller tier:** {s['tier']}"]
    ful = {"FBZ": "All our items are Fulfilled by ZNSouq (stored, shipped and returned through ZNSouq).",
           "Seller": "We ship all orders ourselves (Fulfilled by seller).",
           "Both": "Some items are Fulfilled by ZNSouq and some are shipped by us. Check \"Fulfilled by\" on each product page."}[s["fulfillment"]]
    ship = [ful]
    if s["shipping_fees"]:
        f = s["shipping_fees"]
        ship.append(f"Handling time: we ship within {s['handling_days']} business day(s) of your order.")
        ship.append(f"Our shipping fees: Zone A {f['A']} EGP, Zone B {f['B']} EGP, Zone C {f['C']} EGP, "
                    + (f"Zone D {f['D']} EGP." if f["D"] else "we do not ship to Zone D (Red Sea, South Sinai, North Sinai, Matrouh, New Valley)."))
        if s["free_shipping_over"]:
            ship.append(f"Free shipping on orders from our store over {fmt(s['free_shipping_over'])} EGP (Zones A-C).")
        ship.append("Cash on delivery: " + ("available." if s["cod"] else "not available for items we ship ourselves."))
    ret = []
    if s["policy_conflict"]:
        ret.append("We accept returns within 7 days of delivery only, and only for unopened items. No returns on sale items.")
    else:
        for c in s["categories"]:
            base = CAT[c]["ret"]
            if not base:
                ret.append(f"{CAT[c]['name']}: non-returnable except damaged, expired or wrong items (ZNSouq rules).")
            elif c in s["return_overrides"]:
                ret.append(f"{CAT[c]['name']}: extended return window of **{s['return_overrides'][c]} days** from delivery (ZNSouq minimum is {base} days).")
            else:
                ret.append(f"{CAT[c]['name']}: {base}-day return window (ZNSouq standard).")
        ret.append(f"Change-of-mind return shipping: {s['change_of_mind_shipping']}." if s["fulfillment"] != "FBZ"
                   else "Returns are handled by ZNSouq under ZNSouq's standard rules.")
    war = (f"Store warranty: {s['store_warranty_months']} months in addition to any manufacturer warranty. Contact us via ZNSouq messaging to claim."
           if s["store_warranty_months"] else "We do not offer an extra store warranty; manufacturer warranties apply as shown on each product page.")
    body = (f"{s['description']}\n\n## Store facts\n" + "\n".join(f"- {l}" for l in lines)
            + "\n\n## Shipping\n" + "\n".join(f"- {l}" for l in ship)
            + "\n\n## Returns\n" + "\n".join(f"- {l}" for l in ret)
            + f"\n\n## Warranty\n- {war}\n\n## Contact\n- Message us through ZNSouq (Orders > Contact seller or \"Ask a question\" on any product). "
              f"We reply within 24 hours on business days.")
    write_doc(f"sellers/{s['seller_id']}-{re.sub('[^a-z0-9]+', '-', s['store_name'].lower()).strip('-')}.md",
              f"{s['store_name']} - Store Page", "buyer", body, updated="2026-10-01", doc_type="store_page",
              extra={"seller_id": s["seller_id"], "categories": cats})


# ======================= PRODUCTS =======================
def size_tier(kg, bulky):
    if kg > 20 or (bulky and kg > 15):
        return "Heavy & bulky"
    if bulky or kg > 5:
        return "Oversize"
    if kg <= 0.25:
        return "Small envelope"
    if kg <= 1:
        return "Standard small"
    return "Standard large"


def make_products(sellers):
    by_cat = {c["slug"]: [s for s in sellers[1:] if c["slug"] in s["categories"]] for c in CATEGORIES}
    for c, lst in by_cat.items():  # make sure every category has sellers
        if not lst:
            s = random.choice(sellers[1:]); s["categories"].append(c); by_cat[c] = [s]
    products, seen = [], set()
    counters = {}
    titles_seen = {}
    while len(products) < N_PRODUCTS:
        cat = wchoice(CAT_WEIGHTS)
        d = DEFS[cat]
        t = random.choice(d["types"])
        brand = random.choice(d["brands"])
        attrs = {k: random.choice(v) for k, v in t["attrs"].items()}
        model = f"{brand[:2].upper()}-{random.randint(10, 990)}"
        if t.get("book"):
            words = ["River", "Silent", "Desert", "Memory", "Light", "City", "Garden", "Last", "Letters", "Moon", "Journey", "Salt", "Winter", "Pharaoh's"]
            name = (f"The {random.choice(words)} {random.choice(words)}" if t["t"] == "Novel" else
                    (f"{attrs.get('subject')} Made Simple" if t["t"] == "Textbook" else f"The Little {random.choice(['Cat', 'Boat', 'Star', 'Camel', 'Lantern'])}"))
            author = f"{random.choice(FIRST)} {random.choice(['Hamdy', 'Fawzy', 'Saleh', 'Nabil', 'Adel', 'Ramzy', 'Shawky'])}"
            title = f"{name} by {author} ({', '.join(attrs.values())}) - {brand}"
        else:
            title = f"{brand} {model} {t['t']}, " + ", ".join(attrs.values())
        if title in titles_seen:
            continue
        titles_seen[title] = 1
        code = {"mobile-phones": "MOB", "home-appliances": "APL", "home-kitchen": "HKT", "fashion-men": "FMN",
                "fashion-women": "FWM", "kids-baby": "KID", "pet-supplies": "PET"}.get(cat, cat[:3].upper())
        counters[code] = counters.get(code, 0) + 1
        pid = f"ZNP-{code}-{counters[code]:05d}"
        lo, hi = t["price"]
        price = round(random.uniform(lo, hi) / 5) * 5 - 1
        kg = round(random.uniform(*t["kg"]), 2)
        feats = [f.format(**attrs) for f in t["feats"]]
        random.shuffle(feats)
        feats = feats[:random.randint(3, len(feats))]
        warranty_m = CAT[cat]["warranty"]
        wtype = "Manufacturer warranty" if warranty_m else "No warranty"
        if warranty_m and random.random() < 0.25:
            warranty_m = warranty_m * 2 if warranty_m <= 12 else warranty_m
        intro = random.choice([
            f"The {brand} {t['t']} is made for {t['use']}.",
            f"Designed for {t['use']}, this {t['t']} from {brand} combines quality and value.",
            f"{brand} brings you a reliable {t['t']} for {t['use']}.",
        ])
        desc = intro + " " + " ".join(f + "." for f in feats[:2])
        if t.get("install"):
            desc += " " + t["install"] + "."
        # offers
        main = random.choice(by_cat[cat])
        offer_sellers = [main]
        if random.random() < 0.08:
            offer_sellers.insert(0, sellers[0])
        if random.random() < 0.2:
            for s in random.sample(by_cat[cat], min(len(by_cat[cat]), random.randint(1, 3))):
                if s not in offer_sellers:
                    offer_sellers.append(s)
        offers = []
        for s in offer_sellers:
            ful = "FBZ" if s["fulfillment"] == "FBZ" else ("Seller" if s["fulfillment"] == "Seller" else random.choice(["FBZ", "Seller"]))
            cond = "Renewed" if (t.get("renewed") and s["seller_id"] != "S0000" and random.random() < 0.1) else "New"
            p = price if s is main else round(price * random.uniform(0.9, 1.12) / 5) * 5 - 1
            if cond == "Renewed":
                p = round(p * 0.72 / 5) * 5 - 1
            stock = 0 if random.random() < 0.05 else random.choice([random.randint(1, 9), random.randint(10, 300)])
            offers.append(dict(seller_id=s["seller_id"], price=p, condition=cond, fulfillment=ful, stock=stock,
                               handling_days=(s["handling_days"] if ful == "Seller" else None),
                               seller_warranty_months=(6 if cond == "Renewed" else s["store_warranty_months"])))
        products.append(dict(
            product_id=pid, title=title, category=CAT[cat]["name"], category_slug=cat, product_type=t["t"], brand=brand,
            attributes=attrs, description=desc, features=feats, in_the_box=t["box"],
            weight_kg=kg, fbn_size_tier=size_tier(kg, t.get("bulky", False)), large_bulky_delivery=bool(t.get("bulky")),
            warranty=dict(type=wtype, months=warranty_m),
            offers=offers, listed_date=rdate(date(2024, 1, 1), date(2026, 10, 20)).isoformat()))
    return products


# ======================= REVIEWS =======================
def make_reviews(products):
    reviews, rid = [], 0
    for p in products:
        n = random.choices([0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 25], weights=[10, 12, 12, 12, 11, 10, 9, 8, 7, 6, 3])[0]
        q = random.betavariate(5, 1.6)  # latent product quality
        pos_a, neg_a = ASPECT[p["category_slug"]]
        ratings = []
        for _ in range(n):
            rid += 1
            r = max(1, min(5, round(1 + 4 * q + random.gauss(0, 0.9))))
            ratings.append(r)
            feat = random.choice(p["features"])
            if r >= 4:
                parts = random.sample(pos_a, 1) + ([random.choice(["True to the description: ", "Can confirm: "]) + feat[0].lower() + feat[1:] + "."] if random.random() < 0.5 else [])
                parts = parts + random.sample(POS["generic"], random.randint(1, 2))
                if random.random() < 0.25:
                    parts.append("Only small issue: " + random.choice(neg_a).lower())
                title = random.choice(["Excellent", "Very good", "Highly recommended", "Worth it", "Love it", "Great purchase"])
            elif r == 3:
                parts = [random.choice(pos_a), "But " + random.choice(neg_a).lower()]
                title = random.choice(["Okay", "Average", "Good but not great", "Mixed feelings"])
            else:
                parts = random.sample(neg_a, 1) + random.sample(NEG["generic"], random.randint(1, 2))
                if random.random() < 0.4:
                    parts.insert(1, f"The listing says \"{feat}\" but that was not my experience.")
                if random.random() < 0.3:
                    parts.append(random.choice(SELLER_NEG))
                title = random.choice(["Disappointed", "Not recommended", "Poor quality", "Waste of money", "Returned it"])
            offer = random.choice(p["offers"])
            reviews.append(dict(review_id=f"R{rid:06d}", product_id=p["product_id"], seller_id=offer["seller_id"], rating=r,
                                title=title, body=" ".join(parts),
                                reviewer=f"{random.choice(FIRST)} {random.choice(LAST_INITIAL)}.",
                                date=rdate(date.fromisoformat(p["listed_date"]), TODAY_D).isoformat(),
                                verified_purchase=True, helpful_votes=random.choices([0, 1, 2, 5, 12, 40], weights=[40, 20, 15, 12, 9, 4])[0]))
        p["rating"] = round(sum(ratings) / len(ratings), 1) if ratings else None
        p["review_count"] = len(ratings)
    return reviews


# ======================= ORDERS (for Day 2 tool-calling lesson) =======================
def make_orders(products, n=600):
    orders = []
    gov_all = list(GOV_ZONE)
    for i in range(n):
        p = random.choice(products)
        o = random.choice(p["offers"])
        gov = random.choice(gov_all) if random.random() < 0.3 else wchoice(GOV_WEIGHTS)
        z = GOV_ZONE[gov]
        placed = rdate(date(2026, 9, 1), date(2026, 10, 29))
        lo, hi = map(int, ZONES[z]["std_days"].split("-"))
        extra = o["handling_days"] or 0
        est_lo, est_hi = placed + timedelta(days=lo + extra), placed + timedelta(days=hi + extra + 1)
        age = (TODAY_D - placed).days
        status = ("processing" if age < 1 else "shipped" if TODAY_D < est_lo else
                  random.choices(["delivered", "delivered", "delivered", "returned", "cancelled", "delayed"], weights=[60, 10, 10, 8, 6, 6])[0])
        payment = random.choices(["card", "cash on delivery", "wallet", "installments", "meeza"], weights=[40, 35, 10, 8, 7])[0]
        if payment == "cash on delivery" and gov == "North Sinai":
            payment = "card"
        orders.append(dict(order_id=f"ZN-{random.randint(10**7, 10**8 - 1)}", customer_id=f"C-{random.randint(10000, 99999)}",
                           placed=placed.isoformat(), governorate=gov, zone=z,
                           items=[dict(product_id=p["product_id"], title=p["title"], seller_id=o["seller_id"], qty=random.choice([1, 1, 1, 2]),
                                       unit_price=o["price"], fulfillment=o["fulfillment"])],
                           payment_method=payment, status=status,
                           estimated_delivery=f"{est_lo.isoformat()} to {est_hi.isoformat()}",
                           delivered_on=(rdate(est_lo, est_hi).isoformat() if status in ("delivered", "returned") and est_hi <= TODAY_D else None)))
    return orders


def main():
    sellers = make_sellers()
    products = make_products(sellers)
    reviews = make_reviews(products)
    orders = make_orders(products)
    for s in sellers:
        store_page(s)
    os.makedirs(f"{OUT}/catalog", exist_ok=True)
    with open(f"{OUT}/catalog/sellers.json", "w") as f:
        json.dump(sellers, f, indent=1)
    for name, rows in (("products", products), ("reviews", reviews), ("orders", orders)):
        with open(f"{OUT}/catalog/{name}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(len(sellers), "sellers |", len(products), "products |", len(reviews), "reviews |", len(orders), "orders")


if __name__ == "__main__":
    main()
