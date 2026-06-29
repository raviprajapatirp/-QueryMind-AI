import streamlit as st

COUPONS = {
    "GLAM20": 0.20,
    "FIRST10": 0.10,
    "GOLD15": 0.15,
    "DIWALI25": 0.25,
    "WELCOME5": 0.05,
}


def add_to_cart(product):
    pid = product["id"]
    if pid in st.session_state.cart:
        st.session_state.cart[pid]["qty"] += 1
    else:
        st.session_state.cart[pid] = {"product": product, "qty": 1}


def remove_from_cart(pid):
    if pid in st.session_state.cart:
        del st.session_state.cart[pid]


def update_quantity(pid, qty):
    if qty <= 0:
        remove_from_cart(pid)
    else:
        st.session_state.cart[pid]["qty"] = qty


def get_cart_total(cart):
    return sum(item["product"]["price"] * item["qty"] for item in cart.values())


def get_cart_count(cart):
    return sum(item["qty"] for item in cart.values())


def toggle_wishlist(pid):
    if pid in st.session_state.wishlist:
        st.session_state.wishlist.discard(pid)
    else:
        st.session_state.wishlist.add(pid)


def apply_coupon(code, subtotal):
    code = code.strip().upper()
    if not code:
        return "Please enter a coupon code.", 0
    if code not in COUPONS:
        return f"'{code}' is not a valid coupon code.", 0
    pct = COUPONS[code]
    discount = int(subtotal * pct)
    return f"🎉 Coupon '{code}' applied! You saved ₹{discount:,}.", discount


def filter_products(products, category="All", search="", price_range=(0, 200000),
                    sort_by="Featured", material="All"):
    result = products[:]

    if category and category != "All":
        result = [p for p in result if p["category"] == category]

    if search:
        q = search.lower()
        result = [p for p in result if q in p["name"].lower()
                  or q in p["category"].lower()
                  or q in p["material"].lower()
                  or q in p.get("description", "").lower()]

    result = [p for p in result if price_range[0] <= p["price"] <= price_range[1]]

    if material and material != "All":
        result = [p for p in result if material.lower() in p["material"].lower()]

    if sort_by == "Price: Low to High":
        result.sort(key=lambda x: x["price"])
    elif sort_by == "Price: High to Low":
        result.sort(key=lambda x: x["price"], reverse=True)
    elif sort_by == "Top Rated":
        result.sort(key=lambda x: x["rating"], reverse=True)
    elif sort_by == "New Arrivals":
        result.sort(key=lambda x: x.get("new", False), reverse=True)
    # "Featured" keeps original order

    return result
