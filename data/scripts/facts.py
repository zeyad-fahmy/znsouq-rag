"""Single source of truth for every number in the ZNSouq dataset.
All docs, sellers, products and eval answers are generated from these values,
so the knowledge base never contradicts itself (except where we do it on purpose)."""

MARKET = "ZNSouq"
CURRENCY = "EGP"
TODAY = "2026-10-30"           # "current date" of the dataset
FEE_CHANGE_DATE = "2026-11-01"  # upcoming referral-fee change (temporal trap)
VAT = 14                        # % VAT on ZNSouq's fees to sellers

SUPPORT = {
    "buyer_phone": "00001 (demo number)",
    "buyer_hours": "every day, 9:00 AM - 11:00 PM (Cairo time)",
    "buyer_email": "help@znsouq.example",
    "seller_phone": "00002 (demo number)",
    "seller_hours": "Sunday to Thursday, 9:00 AM - 6:00 PM (Cairo time)",
    "seller_email": "sellers@znsouq.example",
    "hq": "ZNSouq Egypt LLC (fictional), 42 Example Business Park, New Cairo, Egypt",
}

# ---------------- Categories ----------------
# referral fee = % of total sale price (item + shipping charged to buyer), min 5 EGP/item
CATEGORIES = [
    dict(slug="electronics", name="Electronics", fee=8, fee_new=9, ret=15, warranty=12, gated=False,
         change_of_mind="only if unopened and in original sealed packaging",
         non_returnable=["software or game codes once revealed"],
         examples="TVs, headphones, speakers, cameras, smart watches"),
    dict(slug="mobile-phones", name="Mobile Phones & Tablets", fee=6, fee_new=7, ret=15, warranty=12, gated=True,
         change_of_mind="only if the device is still factory-sealed",
         non_returnable=["SIM cards", "devices with the activation seal broken (unless defective)"],
         examples="smartphones, tablets, chargers, phone cases"),
    dict(slug="computers", name="Computers & Accessories", fee=7, fee_new=7, ret=15, warranty=12, gated=False,
         change_of_mind="only if unopened",
         non_returnable=["opened software", "ink cartridges once installed"],
         examples="laptops, monitors, keyboards, storage drives, printers"),
    dict(slug="home-appliances", name="Home Appliances", fee=9, fee_new=9, ret=15, warranty=24, gated=False,
         change_of_mind="only if unopened and not installed",
         non_returnable=["appliances that have been installed by a technician (unless defective)"],
         examples="refrigerators, washing machines, air conditioners, blenders, irons"),
    dict(slug="home-kitchen", name="Home & Kitchen", fee=12, fee_new=12, ret=30, warranty=6, gated=False,
         change_of_mind="if unused and in original packaging",
         non_returnable=["custom-made or personalized items"],
         examples="cookware, bedding, furniture, storage, decor"),
    dict(slug="fashion-men", name="Men's Fashion", fee=15, fee_new=14, ret=30, warranty=0, gated=False,
         change_of_mind="if unworn, unwashed and with original tags attached",
         non_returnable=["underwear", "socks"],
         examples="shirts, trousers, shoes, watches, bags"),
    dict(slug="fashion-women", name="Women's Fashion", fee=15, fee_new=14, ret=30, warranty=0, gated=False,
         change_of_mind="if unworn, unwashed and with original tags attached",
         non_returnable=["lingerie", "swimwear with the hygiene liner removed", "earrings for pierced ears"],
         examples="dresses, abayas, shoes, handbags, jewelry"),
    dict(slug="kids-baby", name="Kids & Baby", fee=11, fee_new=11, ret=30, warranty=6, gated=False,
         change_of_mind="if unused and in original packaging",
         non_returnable=["opened feeding bottles and pacifiers", "opened diapers"],
         examples="strollers, car seats, baby clothes, feeding bottles"),
    dict(slug="beauty", name="Beauty & Personal Care", fee=13, fee_new=13, ret=14, warranty=0, gated=False,
         change_of_mind="only if the product is sealed and unused",
         non_returnable=["any opened cosmetics, skincare or fragrance"],
         examples="skincare, makeup, perfume, hair dryers, shavers"),
    dict(slug="health", name="Health & Nutrition", fee=12, fee_new=12, ret=14, warranty=0, gated=True,
         change_of_mind="only if sealed and unused",
         non_returnable=["opened supplements", "medical devices once used"],
         examples="vitamins, protein powder, blood pressure monitors"),
    dict(slug="sports", name="Sports & Outdoors", fee=12, fee_new=12, ret=30, warranty=6, gated=False,
         change_of_mind="if unused and in original packaging",
         non_returnable=[],
         examples="fitness equipment, bicycles, camping gear, sportswear"),
    dict(slug="toys", name="Toys & Games", fee=12, fee_new=12, ret=30, warranty=0, gated=False,
         change_of_mind="if unopened",
         non_returnable=["opened puzzle or card packs"],
         examples="LEGO-style building sets, dolls, board games, RC cars"),
    dict(slug="books", name="Books", fee=10, fee_new=10, ret=30, warranty=0, gated=False,
         change_of_mind="if in new condition",
         non_returnable=["digital codes", "magazines"],
         examples="novels, textbooks, children's books"),
    dict(slug="grocery", name="Grocery", fee=7, fee_new=7, ret=0, warranty=0, gated=True,
         change_of_mind="not accepted",
         non_returnable=["all grocery items, except damaged, expired or wrong items reported within 48 hours of delivery"],
         examples="coffee, snacks, rice, cooking oil, cleaning supplies"),
    dict(slug="automotive", name="Automotive", fee=11, fee_new=11, ret=15, warranty=6, gated=False,
         change_of_mind="only if unused and not installed",
         non_returnable=["electrical parts once installed"],
         examples="car accessories, tires, dash cams, car care"),
    dict(slug="pet-supplies", name="Pet Supplies", fee=11, fee_new=11, ret=30, warranty=0, gated=False,
         change_of_mind="if unopened",
         non_returnable=["opened pet food"],
         examples="pet food, litter, toys, carriers"),
]
CAT = {c["slug"]: c for c in CATEGORIES}
MIN_REFERRAL_FEE = 5  # EGP per item

# ---------------- Delivery ----------------
ZONES = {
    "A": dict(govs=["Cairo", "Giza"], std_days="1-2", exp="same day if ordered before 12:00 PM, otherwise next day",
              std_fee=30, exp_fee=60),
    "B": dict(govs=["Alexandria", "Qalyubia", "Gharbia", "Dakahlia", "Sharqia", "Monufia", "Beheira",
                    "Kafr El Sheikh", "Damietta"], std_days="2-3", exp="next day", std_fee=40, exp_fee=80),
    "C": dict(govs=["Port Said", "Ismailia", "Suez", "Faiyum", "Beni Suef", "Minya", "Asyut", "Sohag", "Qena",
                    "Luxor", "Aswan"], std_days="3-5", exp="2 days", std_fee=55, exp_fee=110),
    "D": dict(govs=["Red Sea", "South Sinai", "North Sinai", "Matrouh", "New Valley"], std_days="5-8", exp=None,
              std_fee=85, exp_fee=None),
}
GOV_ZONE = {g: z for z, d in ZONES.items() for g in d["govs"]}
GOV_NOTES = {
    "Red Sea": "Delivery covers Hurghada, Safaga, El Gouna and Marsa Alam. Other areas: pickup from the Hurghada pickup point.",
    "South Sinai": "Delivery covers Sharm El Sheikh, Dahab and El Tor only.",
    "North Sinai": "Delivery covers Arish only and may be paused at short notice for security reasons. Cash on delivery is not available in North Sinai.",
    "Matrouh": "Delivery covers Marsa Matrouh city and the North Coast (Sahel) resorts. North Coast deliveries from June to September take 2-4 days.",
    "New Valley": "Delivery covers Kharga and Dakhla only.",
    "Aswan": "Abu Simbel deliveries take 2 extra days.",
    "Cairo": "New Capital and Shorouk are included in Zone A. Express same-day delivery is available.",
    "Giza": "6th of October and Sheikh Zayed are included in Zone A. Express same-day delivery is available.",
    "Alexandria": "Borg El Arab is included. Express next-day delivery is available.",
}
FREE_SHIP_THRESHOLD = 500   # EGP, FBZ items, zones A-C, standard delivery
COD_FEE = 15
COD_MAX = 20000
COD_ZONE_D_MAX = 5000
PICKUP_POINT_FEE = 0        # pickup points are free

# ---------------- Returns & refunds (buyer) ----------------
RETURN_SHIPPING_FEE = 25            # change-of-mind returns on FBZ items (Plus: free)
DAMAGE_REPORT_HOURS = 48            # for grocery & large appliances
DEFECT_REPORT_DAYS = 7              # report wrong/damaged item (other categories) after delivery
INSPECTION_DAYS = 2                 # business days after return reaches warehouse
REFUND_TIMES = {
    "ZNSouq Wallet": "within 24 hours after inspection",
    "Credit/debit card": "5-10 business days after inspection, depending on your bank",
    "Meeza card": "5-10 business days after inspection",
    "Cash on delivery": "to your ZNSouq Wallet within 24 hours, or by bank transfer within 7 business days if you request it",
    "Installments (ZNPay)": "the installment plan is cancelled and paid installments are refunded within 14 business days",
}

# ---------------- ZNSouq Guarantee ----------------
GUARANTEE_WAIT_DAYS = 3        # days after latest estimated delivery date before a 'not received' claim
GUARANTEE_FILE_WINDOW = 90     # days after latest estimated delivery date
GUARANTEE_SELLER_RESPONSE_H = 48
GUARANTEE_MAX = 50000          # EGP per order

# ---------------- Plus membership ----------------
PLUS = dict(monthly=99, yearly=899, trial_days=30, student_monthly=49,
            refund_window_days=14)

# ---------------- Payments ----------------
INSTALLMENT_MIN = 1500
INSTALLMENT_PLANS = [(6, "0% interest on orders of 3,000 EGP or more; 5% admin fee below 3,000 EGP"),
                     (12, "admin fee of 8% of the order value"),
                     (24, "admin fee of 15% of the order value")]
GIFT_CARD = dict(min=100, max=5000, validity_years=3)

# ---------------- Seller program ----------------
PLANS = {
    "Individual": dict(monthly=0, per_item=10,
                       note="best for sellers with fewer than 40 sales per month; no access to advertising, bulk listing tools or the Buy Box"),
    "Professional": dict(monthly=399, per_item=0,
                         note="includes advertising, bulk listing tools, reports and Buy Box eligibility"),
}
FBZ_TIERS = [
    ("Small envelope", "up to 250 g, max 30 x 20 x 2 cm", 22),
    ("Standard small", "up to 1 kg, max 35 x 25 x 12 cm", 30),
    ("Standard large", "up to 5 kg, max 45 x 35 x 20 cm", 45),
    ("Oversize", "up to 20 kg, max 120 x 60 x 60 cm", 95),
    ("Heavy & bulky", "over 20 kg or larger than oversize", 180),  # + 6 EGP/kg over 20 kg
]
HEAVY_PER_KG = 6
STORAGE_FEE = dict(jan_sep=25, oct_dec=60)  # EGP per cubic foot per month
LONG_TERM_DAYS = 180
LONG_TERM_SURCHARGE = 15
REMOVAL_FEE = 8
PAYOUT = dict(day="Tuesday", reserve_days=7, new_seller_reserve_days=14, new_seller_period_days=90, minimum=100)
HEALTH = dict(odr=1.0, late_shipment=4.0, cancel=2.5, valid_tracking=95.0, response_24h=90.0)
APPEAL_DAYS = 14
APPEAL_REVIEW = "3-5 business days"
VERIFICATION_DAYS = "2-5 business days"
HANDLING_MAX_DAYS = 3   # seller-fulfilled: must ship within this many business days unless listing says longer (max 5)
ADS_MIN_BID = 0.50
SELLER_TIERS = [
    ("Standard", "all new sellers"),
    ("Rising Star", "at least 100 orders in the last 30 days, store rating 4.5+, and all account health metrics in good standing"),
    ("Top Seller", "at least 1,000 orders in the last 90 days, store rating 4.7+, ODR below 0.5%, and late shipment rate below 2%"),
]
