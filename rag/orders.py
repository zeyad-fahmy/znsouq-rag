"""Order lookup TOOL: live, per-customer data that RAG can't answer from documents.
Claude decides when to call `lookup_order`; our code runs it and sends the result back."""
import json
from datetime import date

from rag.loader import DATA_DIR

ORDERS = {}
with (DATA_DIR / "catalog" / "orders.jsonl").open(encoding="utf-8") as f:
    for line in f:
        o = json.loads(line)
        ORDERS[o["order_id"]] = o

SELLERS = {s["seller_id"]: s["store_name"]
           for s in json.loads((DATA_DIR / "catalog" / "sellers.json").read_text(encoding="utf-8"))}

# The tool description Claude reads. It decides from this text WHEN and HOW to call the tool.
ORDER_TOOL = {
    "name": "lookup_order",
    "description": ("Look up one of the logged-in customer's orders by its order number. "
                    "Returns status, items, seller, payment method, estimated delivery dates and delivery date. "
                    "Use it whenever the customer asks about a specific order (where is it, when will it arrive, "
                    "what's in it, was it delivered). Only works for the logged-in customer's own orders."),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "Order number in the format ZN-12345678"},
        },
        "required": ["order_id"],
    },
}


def lookup_order(order_id: str, customer_id: str | None):
    """Run the tool. Privacy rule: a customer can only see their OWN orders."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None or customer_id is None or order["customer_id"] != customer_id:
        # Same message whether the order doesn't exist or belongs to someone else (don't leak which)
        return {"found": False, "message": f"No order {order_id} was found on this customer's account."}
    latest = order["estimated_delivery"].split(" to ")[-1]
    late = order["status"] in ("shipped", "delayed") and date.today().isoformat() > latest
    return {
        "found": True,
        "order_id": order["order_id"],
        "placed_on": order["placed"],
        "status": order["status"],
        "estimated_delivery": order["estimated_delivery"],
        "delivered_on": order["delivered_on"],
        "late": late,
        "delivery_governorate": order["governorate"],
        "payment_method": order["payment_method"],
        "items": [{"title": i["title"], "qty": i["qty"], "unit_price_egp": i["unit_price"],
                   "sold_by": SELLERS.get(i["seller_id"], i["seller_id"]),
                   "fulfilled_by": "ZNSouq (FBZ)" if i["fulfillment"] == "FBZ" else "seller"}
                  for i in order["items"]],
    }


def demo_customers(n_per_status=1):
    """A few demo accounts with different order situations, for the app's sidebar."""
    picked = {}
    for o in ORDERS.values():
        if o["status"] not in picked:
            picked[o["status"]] = o
    return [{"customer_id": o["customer_id"], "order_id": o["order_id"], "status": o["status"]}
            for o in picked.values()]
