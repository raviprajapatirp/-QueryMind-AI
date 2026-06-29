import streamlit as st
import json
from data import PRODUCTS, CATEGORIES, BANNERS
from utils import (
    add_to_cart, remove_from_cart, update_quantity,
    get_cart_total, get_cart_count, toggle_wishlist,
    apply_coupon, filter_products
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlamCart – Fine Jewellery",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "cart": {},
    "wishlist": set(),
    "page": "home",
    "selected_product": None,
    "selected_category": "All",
    "search_query": "",
    "sort_by": "Featured",
    "price_range": (0, 200000),
    "coupon_applied": None,
    "discount": 0,
    "order_placed": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
* { box-sizing: border-box; }
.stApp { background: #0a0a0a; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Typography ── */
h1,h2,h3,h4 { font-family: 'Cormorant Garamond', serif !important; }
p, span, div, label, button { font-family: 'Inter', sans-serif !important; }

/* ── Navbar ── */
.gc-nav {
  background: linear-gradient(135deg, #0d0d0d 0%, #1a0a1e 100%);
  border-bottom: 1px solid #3d1c5a;
  padding: 14px 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top: 0; z-index: 999;
}
.gc-logo {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(90deg, #d4af37, #f5d98b, #c9a227);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}
.gc-logo span { font-weight: 300; }
.gc-tagline {
  font-family: 'Inter', sans-serif;
  font-size: 0.6rem;
  letter-spacing: 4px;
  color: #9b6fbf;
  text-transform: uppercase;
  margin-top: -6px;
}

/* ── Hero Banner ── */
.gc-hero {
  background: linear-gradient(135deg, #0d0d0d 0%, #1a0520 40%, #0a0015 100%);
  padding: 80px 60px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.gc-hero::before {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.08) 0%, transparent 70%);
}
.gc-hero-eyebrow {
  font-family: 'Inter', sans-serif;
  font-size: 0.7rem;
  letter-spacing: 5px;
  color: #d4af37;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.gc-hero h1 {
  font-family: 'Cormorant Garamond', serif;
  font-size: clamp(2.5rem, 6vw, 5rem);
  font-weight: 300;
  color: #f5f0e8;
  line-height: 1.1;
  margin-bottom: 20px;
}
.gc-hero h1 em { font-style: italic; color: #d4af37; }
.gc-hero p {
  font-size: 1rem;
  color: #9b8fa8;
  max-width: 500px;
  margin: 0 auto 36px;
  line-height: 1.7;
}

/* ── Buttons ── */
.gc-btn-primary {
  background: linear-gradient(90deg, #d4af37, #f5d98b, #c9a227);
  color: #0a0a0a;
  border: none;
  padding: 14px 36px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  display: inline-block;
  text-align: center;
  transition: all 0.3s;
}
.gc-btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }

.gc-btn-outline {
  background: transparent;
  color: #d4af37;
  border: 1px solid #d4af37;
  padding: 12px 30px;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  display: inline-block;
  text-align: center;
}

/* ── Category Chips ── */
.gc-chip-row {
  display: flex; flex-wrap: wrap; gap: 10px;
  padding: 20px 40px;
  background: #0f0f0f;
  border-bottom: 1px solid #1e1e1e;
}
.gc-chip {
  background: #1a1a1a;
  color: #b0a0c0;
  border: 1px solid #2a2a2a;
  padding: 8px 18px;
  font-size: 0.78rem;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Inter', sans-serif !important;
}
.gc-chip.active {
  background: linear-gradient(90deg, #d4af37, #f5d98b);
  color: #0a0a0a;
  border-color: #d4af37;
  font-weight: 600;
}

/* ── Product Card ── */
.gc-card {
  background: #111;
  border: 1px solid #1e1e1e;
  transition: all 0.3s;
  overflow: hidden;
  height: 100%;
}
.gc-card:hover {
  border-color: #d4af37;
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(212,175,55,0.15);
}
.gc-card-img {
  width: 100%; aspect-ratio: 1;
  object-fit: cover;
  display: block;
}
.gc-card-img-placeholder {
  width: 100%; aspect-ratio: 1;
  display: flex; align-items: center; justify-content: center;
  font-size: 4rem;
  background: linear-gradient(135deg, #1a1020, #0d0d1a);
}
.gc-card-body { padding: 16px; }
.gc-card-tag {
  font-size: 0.65rem; letter-spacing: 2px;
  text-transform: uppercase; color: #9b6fbf;
  margin-bottom: 6px;
}
.gc-card-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.15rem;
  color: #f0e8d8;
  margin-bottom: 4px;
  font-weight: 500;
  line-height: 1.3;
}
.gc-card-price {
  font-size: 1rem;
  color: #d4af37;
  font-weight: 600;
  margin-bottom: 4px;
}
.gc-card-mrp {
  font-size: 0.78rem;
  color: #555;
  text-decoration: line-through;
  margin-right: 8px;
}
.gc-card-discount {
  font-size: 0.75rem;
  color: #4caf50;
  font-weight: 500;
}
.gc-card-rating {
  font-size: 0.75rem;
  color: #d4af37;
  margin-bottom: 10px;
}
.gc-badge-new {
  background: #d4af37;
  color: #0a0a0a;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  padding: 3px 8px;
  display: inline-block;
  margin-bottom: 8px;
}
.gc-badge-sale {
  background: #9b1a4a;
  color: #fff;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 1.5px;
  padding: 3px 8px;
  display: inline-block;
  margin-bottom: 8px;
}

/* ── Section Headers ── */
.gc-section-header {
  padding: 50px 40px 30px;
  background: #0a0a0a;
}
.gc-section-eyebrow {
  font-size: 0.65rem;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: #d4af37;
  margin-bottom: 8px;
}
.gc-section-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.2rem;
  font-weight: 300;
  color: #f0e8d8;
  line-height: 1.2;
}

/* ── Product Detail ── */
.gc-detail-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 2.5rem;
  font-weight: 400;
  color: #f0e8d8;
  line-height: 1.2;
  margin-bottom: 8px;
}
.gc-detail-price {
  font-size: 1.8rem;
  color: #d4af37;
  font-weight: 600;
}
.gc-detail-desc {
  color: #9b8fa8;
  line-height: 1.8;
  font-size: 0.95rem;
}
.gc-spec-row {
  display: flex; justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #1e1e1e;
  font-size: 0.85rem;
}
.gc-spec-label { color: #666; }
.gc-spec-value { color: #d0c0e0; font-weight: 500; }

/* ── Cart ── */
.gc-cart-item {
  background: #111;
  border: 1px solid #1e1e1e;
  padding: 16px;
  margin-bottom: 12px;
  display: flex; gap: 16px;
  align-items: center;
}
.gc-cart-emoji { font-size: 2.5rem; width: 60px; text-align: center; }
.gc-cart-name {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.1rem;
  color: #f0e8d8;
}
.gc-cart-price { color: #d4af37; font-size: 0.95rem; font-weight: 600; }

/* ── Banner Offer ── */
.gc-offer-strip {
  background: linear-gradient(90deg, #d4af37, #f5d98b, #c9a227);
  padding: 12px 40px;
  text-align: center;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 2px;
  color: #0a0a0a;
  text-transform: uppercase;
}

/* ── Streamlit overrides ── */
div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
.stButton > button {
  width: 100%;
  background: linear-gradient(90deg, #d4af37, #c9a227) !important;
  color: #0a0a0a !important;
  border: none !important;
  border-radius: 0 !important;
  font-weight: 600 !important;
  font-size: 0.78rem !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  padding: 10px !important;
  transition: all 0.2s !important;
}
.stButton > button:hover {
  opacity: 0.85 !important;
  transform: translateY(-1px) !important;
}
.stButton.secondary > button,
button[kind="secondary"] {
  background: transparent !important;
  border: 1px solid #3d1c5a !important;
  color: #d4af37 !important;
}
.stTextInput > div > div > input {
  background: #111 !important;
  border: 1px solid #2a2a2a !important;
  color: #f0e8d8 !important;
  border-radius: 0 !important;
}
.stSelectbox > div > div {
  background: #111 !important;
  border: 1px solid #2a2a2a !important;
  color: #f0e8d8 !important;
  border-radius: 0 !important;
}
.stSlider { padding: 0 !important; }
div[data-testid="stMetricValue"] { color: #d4af37 !important; font-size: 1.5rem !important; }
div[data-testid="stMetricLabel"] { color: #9b8fa8 !important; }
.stSuccess { background: rgba(76,175,80,0.1) !important; border-color: #4caf50 !important; }
.stWarning { background: rgba(212,175,55,0.1) !important; }

/* ── Divider ── */
.gc-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, #3d1c5a, transparent);
  margin: 20px 40px;
}

/* ── Trust badges ── */
.gc-trust {
  display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
  padding: 50px 40px;
  background: #0d0d0d;
  border-top: 1px solid #1e1e1e;
}
.gc-trust-item { text-align: center; }
.gc-trust-icon { font-size: 2rem; margin-bottom: 8px; }
.gc-trust-title {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1rem;
  color: #f0e8d8;
  margin-bottom: 4px;
}
.gc-trust-sub { font-size: 0.75rem; color: #666; }

/* ── Footer ── */
.gc-footer {
  background: #050505;
  border-top: 1px solid #1e1e1e;
  padding: 40px;
  text-align: center;
  color: #333;
  font-size: 0.8rem;
}
.gc-footer-logo {
  font-family: 'Cormorant Garamond', serif;
  font-size: 1.5rem;
  color: #d4af37;
  margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: nav ───────────────────────────────────────────────────────────────
def go(page, product=None):
    st.session_state.page = page
    if product:
        st.session_state.selected_product = product
    st.rerun()


# ── Navbar ────────────────────────────────────────────────────────────────────
def render_navbar():
    cart_count = get_cart_count(st.session_state.cart)
    wishlist_count = len(st.session_state.wishlist)

    st.markdown(f"""
    <div class="gc-nav">
      <div>
        <div class="gc-logo">Glam<span>Cart</span></div>
        <div class="gc-tagline">Fine Jewellery</div>
      </div>
      <div style="display:flex;gap:8px;align-items:center;">
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Nav buttons
    c1, c2, c3, c4, c5, c6 = st.columns([2, 1, 1, 1, 1, 1])
    with c1:
        q = st.text_input("", placeholder="🔍  Search jewellery...", label_visibility="collapsed",
                          value=st.session_state.search_query, key="nav_search")
        if q != st.session_state.search_query:
            st.session_state.search_query = q
            st.session_state.page = "shop"
            st.rerun()
    with c2:
        if st.button("🏠 Home"):
            go("home")
    with c3:
        if st.button("💍 Shop"):
            go("shop")
    with c4:
        if st.button(f"❤️ Wishlist ({wishlist_count})"):
            go("wishlist")
    with c5:
        if st.button(f"🛒 Cart ({cart_count})"):
            go("cart")
    with c6:
        if st.button("📦 Orders"):
            go("orders")


# ── HOME PAGE ─────────────────────────────────────────────────────────────────
def render_home():
    # Offer strip
    st.markdown("""
    <div class="gc-offer-strip">
      ✨ Free shipping on orders above ₹5,000 &nbsp;|&nbsp; Use GLAM20 for 20% off &nbsp;|&nbsp; BIS Hallmarked Gold & Silver
    </div>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="gc-hero">
      <div class="gc-hero-eyebrow">New Collection 2025</div>
      <h1>Where Every Piece<br>Tells Your <em>Story</em></h1>
      <p>Curated fine jewellery crafted with precision — from heritage gold to contemporary silver, diamonds to gemstones.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([3, 2, 3])
    with c2:
        if st.button("✦ Explore Collection", key="hero_btn"):
            go("shop")

    st.markdown('<div class="gc-divider"></div>', unsafe_allow_html=True)

    # Category showcase
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Shop by Category</div>
      <div class="gc-section-title">Find Your Perfect Piece</div>
    </div>
    """, unsafe_allow_html=True)

    cat_icons = {"Rings": "💍", "Necklaces": "📿", "Earrings": "✨",
                 "Bracelets": "💛", "Bangles": "🔮", "Pendants": "🌟",
                 "Anklets": "🌙", "Sets": "👑"}

    cols = st.columns(4)
    for i, (cat, icon) in enumerate(cat_icons.items()):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="gc-card" style="text-align:center;padding:30px 20px;margin-bottom:16px;cursor:pointer;">
              <div style="font-size:2.5rem;margin-bottom:12px;">{icon}</div>
              <div style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;color:#f0e8d8;">{cat}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Browse {cat}", key=f"cat_{cat}"):
                st.session_state.selected_category = cat
                go("shop")

    st.markdown('<div class="gc-divider"></div>', unsafe_allow_html=True)

    # Featured products
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Handpicked for You</div>
      <div class="gc-section-title">Featured Collection</div>
    </div>
    """, unsafe_allow_html=True)

    featured = [p for p in PRODUCTS if p.get("featured")][:8]
    render_product_grid(featured, cols_n=4)

    # Trending
    st.markdown('<div class="gc-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Most Loved</div>
      <div class="gc-section-title">Trending Now</div>
    </div>
    """, unsafe_allow_html=True)

    trending = sorted(PRODUCTS, key=lambda x: x["rating"], reverse=True)[:4]
    render_product_grid(trending, cols_n=4)

    # Trust
    st.markdown("""
    <div class="gc-trust">
      <div class="gc-trust-item">
        <div class="gc-trust-icon">🏅</div>
        <div class="gc-trust-title">BIS Hallmarked</div>
        <div class="gc-trust-sub">Certified purity on all gold</div>
      </div>
      <div class="gc-trust-item">
        <div class="gc-trust-icon">🚚</div>
        <div class="gc-trust-title">Free Shipping</div>
        <div class="gc-trust-sub">On orders above ₹5,000</div>
      </div>
      <div class="gc-trust-item">
        <div class="gc-trust-icon">↩️</div>
        <div class="gc-trust-title">15-Day Returns</div>
        <div class="gc-trust-sub">Hassle-free return policy</div>
      </div>
      <div class="gc-trust-item">
        <div class="gc-trust-icon">🔒</div>
        <div class="gc-trust-title">Secure Payments</div>
        <div class="gc-trust-sub">UPI · Cards · EMI options</div>
      </div>
      <div class="gc-trust-item">
        <div class="gc-trust-icon">💎</div>
        <div class="gc-trust-title">Certified Gems</div>
        <div class="gc-trust-sub">GIA & IGI certified diamonds</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="gc-footer">
      <div class="gc-footer-logo">GlamCart</div>
      <p>© 2025 GlamCart Fine Jewellery. All rights reserved.</p>
      <p style="margin-top:8px;">Made with ❤️ in India</p>
    </div>
    """, unsafe_allow_html=True)


# ── PRODUCT CARD ──────────────────────────────────────────────────────────────
def render_product_card(p):
    discount_pct = round((1 - p["price"] / p["mrp"]) * 100)
    badge = ""
    if p.get("new"):
        badge = '<span class="gc-badge-new">NEW</span><br>'
    elif discount_pct >= 20:
        badge = f'<span class="gc-badge-sale">{discount_pct}% OFF</span><br>'

    stars = "★" * int(p["rating"]) + "☆" * (5 - int(p["rating"]))
    in_wishlist = p["id"] in st.session_state.wishlist

    st.markdown(f"""
    <div class="gc-card">
      <div class="gc-card-img-placeholder">{p['emoji']}</div>
      <div class="gc-card-body">
        {badge}
        <div class="gc-card-tag">{p['material']} · {p['category']}</div>
        <div class="gc-card-name">{p['name']}</div>
        <div class="gc-card-rating">{stars} ({p['reviews']})</div>
        <div>
          <span class="gc-card-mrp">₹{p['mrp']:,}</span>
          <span class="gc-card-discount">{discount_pct}% off</span>
        </div>
        <div class="gc-card-price">₹{p['price']:,}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("View", key=f"view_{p['id']}"):
            go("product", p)
    with c2:
        wl_label = "♥ Saved" if in_wishlist else "♡ Save"
        if st.button(wl_label, key=f"wl_{p['id']}"):
            toggle_wishlist(p["id"])
            st.rerun()


def render_product_grid(products, cols_n=4):
    if not products:
        st.markdown("<p style='color:#555;padding:40px;text-align:center;'>No products found.</p>",
                    unsafe_allow_html=True)
        return

    st.markdown("<div style='padding:0 30px 40px;background:#0a0a0a;'>", unsafe_allow_html=True)
    rows = [products[i:i+cols_n] for i in range(0, len(products), cols_n)]
    for row in rows:
        cols = st.columns(cols_n)
        for j, p in enumerate(row):
            with cols[j]:
                render_product_card(p)
    st.markdown("</div>", unsafe_allow_html=True)


# ── SHOP PAGE ─────────────────────────────────────────────────────────────────
def render_shop():
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Our Collection</div>
      <div class="gc-section-title">All Jewellery</div>
    </div>
    """, unsafe_allow_html=True)

    # Category chips
    all_cats = ["All"] + CATEGORIES
    chip_html = '<div class="gc-chip-row">'
    for c in all_cats:
        active = "active" if c == st.session_state.selected_category else ""
        chip_html += f'<span class="gc-chip {active}">{c}</span>'
    chip_html += '</div>'
    st.markdown(chip_html, unsafe_allow_html=True)

    # Category selector
    cat_cols = st.columns(len(all_cats))
    for i, c in enumerate(all_cats):
        with cat_cols[i]:
            if st.button(c, key=f"cat_btn_{c}"):
                st.session_state.selected_category = c
                st.rerun()

    # Filters
    st.markdown("<div style='padding:16px 40px;background:#0d0d0d;border-bottom:1px solid #1e1e1e;'>",
                unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([2, 1, 1])
    with fc1:
        price_range = st.slider("Price Range (₹)", 0, 200000,
                                st.session_state.price_range, step=1000,
                                format="₹%d", key="price_slider")
        st.session_state.price_range = price_range
    with fc2:
        sort_by = st.selectbox("Sort by", ["Featured", "Price: Low to High",
                                            "Price: High to Low", "Top Rated", "New Arrivals"],
                               index=["Featured", "Price: Low to High",
                                      "Price: High to Low", "Top Rated", "New Arrivals"].index(
                                   st.session_state.sort_by), key="sort_select")
        st.session_state.sort_by = sort_by
    with fc3:
        material = st.selectbox("Material", ["All", "Gold", "Silver", "Diamond",
                                              "Platinum", "Rose Gold", "Kundan", "Meenakari"],
                                key="mat_select")
    st.markdown("</div>", unsafe_allow_html=True)

    products = filter_products(
        PRODUCTS,
        category=st.session_state.selected_category,
        search=st.session_state.search_query,
        price_range=st.session_state.price_range,
        sort_by=st.session_state.sort_by,
        material=material
    )

    st.markdown(f"<p style='color:#555;font-size:0.8rem;padding:12px 40px;background:#0a0a0a;'>"
                f"{len(products)} products found</p>", unsafe_allow_html=True)

    render_product_grid(products, cols_n=4)


# ── PRODUCT DETAIL ────────────────────────────────────────────────────────────
def render_product_detail():
    p = st.session_state.selected_product
    if not p:
        go("shop")
        return

    discount_pct = round((1 - p["price"] / p["mrp"]) * 100)
    stars = "★" * int(p["rating"]) + "☆" * (5 - int(p["rating"]))

    st.markdown("<div style='padding:16px 40px;background:#0a0a0a;'>", unsafe_allow_html=True)
    if st.button("← Back to Shop"):
        go("shop")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='padding:30px 40px;background:#0a0a0a;'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1020,#0d0d1a);
                    aspect-ratio:1;display:flex;align-items:center;
                    justify-content:center;font-size:10rem;border:1px solid #2a2a2a;">
          {p['emoji']}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="padding:10px 0;">
          <div class="gc-card-tag" style="margin-bottom:12px;">{p['material']} · {p['category']}</div>
          <div class="gc-detail-name">{p['name']}</div>
          <div style="color:#d4af37;font-size:0.85rem;margin-bottom:16px;">{stars} &nbsp;{p['rating']}/5 ({p['reviews']} reviews)</div>
          <div style="margin-bottom:20px;">
            <span class="gc-card-mrp">₹{p['mrp']:,}</span>
            <span class="gc-card-discount">&nbsp;{discount_pct}% off</span><br>
            <span class="gc-detail-price">₹{p['price']:,}</span>
          </div>
          <p class="gc-detail-desc">{p['description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Specifications
        st.markdown(f"""
        <div style="margin:20px 0;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;color:#f0e8d8;margin-bottom:12px;">
            Specifications
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Material</span>
            <span class="gc-spec-value">{p['material']}</span>
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Weight</span>
            <span class="gc-spec-value">{p.get('weight','N/A')}</span>
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Purity</span>
            <span class="gc-spec-value">{p.get('purity','N/A')}</span>
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Occasion</span>
            <span class="gc-spec-value">{p.get('occasion','All occasions')}</span>
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Availability</span>
            <span class="gc-spec-value" style="color:#4caf50;">✓ In Stock</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🛒 Add to Cart", key="detail_add_cart"):
                add_to_cart(p)
                st.success(f"'{p['name']}' added to cart!")
        with c2:
            wl = "♥ Saved" if p["id"] in st.session_state.wishlist else "♡ Wishlist"
            if st.button(wl, key="detail_wl"):
                toggle_wishlist(p["id"])
                st.rerun()

        if st.button("⚡ Buy Now", key="detail_buy"):
            add_to_cart(p)
            go("cart")

    st.markdown("</div>", unsafe_allow_html=True)

    # Related products
    related = [x for x in PRODUCTS if x["category"] == p["category"] and x["id"] != p["id"]][:4]
    if related:
        st.markdown("""
        <div class="gc-section-header">
          <div class="gc-section-eyebrow">You May Also Like</div>
          <div class="gc-section-title">Similar Pieces</div>
        </div>
        """, unsafe_allow_html=True)
        render_product_grid(related, cols_n=4)


# ── CART PAGE ─────────────────────────────────────────────────────────────────
def render_cart():
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Your Selection</div>
      <div class="gc-section-title">Shopping Cart</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.cart:
        st.markdown("""
        <div style="text-align:center;padding:80px 40px;color:#555;">
          <div style="font-size:4rem;margin-bottom:20px;">🛒</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;color:#f0e8d8;margin-bottom:12px;">Your cart is empty</div>
          <p>Discover our curated jewellery collection.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Collection", key="empty_cart_browse"):
            go("shop")
        return

    st.markdown("<div style='padding:20px 40px;background:#0a0a0a;'>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div style='font-family:Cormorant Garamond,serif;font-size:1.2rem;color:#f0e8d8;margin-bottom:16px;'>Cart Items</div>", unsafe_allow_html=True)
        for pid, item in list(st.session_state.cart.items()):
            p = item["product"]
            qty = item["qty"]
            st.markdown(f"""
            <div class="gc-cart-item">
              <div class="gc-cart-emoji">{p['emoji']}</div>
              <div style="flex:1;">
                <div class="gc-cart-name">{p['name']}</div>
                <div style="font-size:0.75rem;color:#666;margin-bottom:4px;">{p['material']}</div>
                <div class="gc-cart-price">₹{p['price']:,} × {qty} = ₹{p['price']*qty:,}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            cq1, cq2, cq3 = st.columns([1, 1, 1])
            with cq1:
                if st.button("−", key=f"dec_{pid}"):
                    update_quantity(pid, qty - 1)
                    st.rerun()
            with cq2:
                st.markdown(f"<div style='text-align:center;color:#d4af37;font-size:1.1rem;padding:8px 0;'>{qty}</div>", unsafe_allow_html=True)
            with cq3:
                if st.button("+", key=f"inc_{pid}"):
                    update_quantity(pid, qty + 1)
                    st.rerun()

            if st.button("🗑 Remove", key=f"rm_{pid}"):
                remove_from_cart(pid)
                st.rerun()

    with col2:
        subtotal = get_cart_total(st.session_state.cart)
        shipping = 0 if subtotal >= 5000 else 199
        discount = st.session_state.discount
        total = subtotal + shipping - discount

        st.markdown(f"""
        <div class="gc-card" style="padding:24px;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.3rem;color:#f0e8d8;margin-bottom:20px;">Order Summary</div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Subtotal</span>
            <span class="gc-spec-value">₹{subtotal:,}</span>
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Shipping</span>
            <span class="gc-spec-value" style="color:{'#4caf50' if shipping==0 else '#f0e8d8'}">
              {'FREE' if shipping==0 else f'₹{shipping}'}
            </span>
          </div>
          {"" if not discount else f'<div class="gc-spec-row"><span class="gc-spec-label">Discount</span><span class="gc-spec-value" style="color:#4caf50;">−₹{discount:,}</span></div>'}
          <div class="gc-spec-row" style="border-bottom:none;padding-top:16px;margin-top:8px;border-top:1px solid #2a2a2a;">
            <span style="color:#f0e8d8;font-weight:600;">Total</span>
            <span style="color:#d4af37;font-size:1.3rem;font-weight:700;">₹{total:,}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Coupon
        coupon = st.text_input("Coupon Code", placeholder="Enter code", key="coupon_input")
        if st.button("Apply Coupon", key="apply_coupon"):
            msg, disc = apply_coupon(coupon, subtotal)
            if disc > 0:
                st.session_state.discount = disc
                st.session_state.coupon_applied = coupon
                st.success(msg)
            else:
                st.error(msg)

        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("Proceed to Checkout →", key="checkout_btn"):
            go("checkout")

    st.markdown("</div>", unsafe_allow_html=True)


# ── CHECKOUT PAGE ─────────────────────────────────────────────────────────────
def render_checkout():
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Final Step</div>
      <div class="gc-section-title">Checkout</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:20px 40px;background:#0a0a0a;'>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("<div style='font-family:Cormorant Garamond,serif;font-size:1.3rem;color:#f0e8d8;margin-bottom:20px;'>Delivery Address</div>", unsafe_allow_html=True)
        name = st.text_input("Full Name *", placeholder="Your name")
        email = st.text_input("Email Address *", placeholder="email@example.com")
        phone = st.text_input("Phone Number *", placeholder="+91 XXXXX XXXXX")
        address = st.text_area("Address *", placeholder="House/Flat, Street, Area")
        co1, co2 = st.columns(2)
        with co1:
            city = st.text_input("City *", placeholder="City")
        with co2:
            pincode = st.text_input("Pincode *", placeholder="6-digit PIN")
        state = st.selectbox("State", ["Select State", "Maharashtra", "Delhi", "Karnataka",
                                        "Tamil Nadu", "Gujarat", "Rajasthan", "West Bengal",
                                        "Uttar Pradesh", "Telangana", "Kerala"])

        st.markdown("<div style='margin-top:24px;font-family:Cormorant Garamond,serif;font-size:1.3rem;color:#f0e8d8;margin-bottom:16px;'>Payment Method</div>", unsafe_allow_html=True)
        payment = st.radio("", ["💳 Credit/Debit Card", "📱 UPI", "🏦 Net Banking",
                                 "💵 Cash on Delivery", "💰 EMI"],
                           label_visibility="collapsed")

        if "Card" in payment:
            st.text_input("Card Number", placeholder="XXXX XXXX XXXX XXXX", max_chars=19)
            p1, p2 = st.columns(2)
            with p1:
                st.text_input("Expiry (MM/YY)", placeholder="MM/YY")
            with p2:
                st.text_input("CVV", placeholder="XXX", max_chars=3, type="password")
        elif "UPI" in payment:
            st.text_input("UPI ID", placeholder="yourname@upi")

    with c2:
        subtotal = get_cart_total(st.session_state.cart)
        shipping = 0 if subtotal >= 5000 else 199
        discount = st.session_state.discount
        total = subtotal + shipping - discount

        st.markdown(f"""
        <div class="gc-card" style="padding:24px;margin-bottom:16px;">
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.3rem;color:#f0e8d8;margin-bottom:16px;">Order Summary</div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Items ({get_cart_count(st.session_state.cart)})</span>
            <span class="gc-spec-value">₹{subtotal:,}</span>
          </div>
          <div class="gc-spec-row">
            <span class="gc-spec-label">Shipping</span>
            <span class="gc-spec-value">{'FREE' if shipping==0 else f'₹{shipping}'}</span>
          </div>
          {"" if not discount else f'<div class="gc-spec-row"><span class="gc-spec-label">Coupon</span><span class="gc-spec-value" style="color:#4caf50;">−₹{discount:,}</span></div>'}
          <div class="gc-spec-row" style="border-bottom:none;border-top:1px solid #2a2a2a;padding-top:16px;margin-top:8px;">
            <span style="color:#f0e8d8;font-weight:600;font-size:1.1rem;">Total Payable</span>
            <span style="color:#d4af37;font-size:1.5rem;font-weight:700;">₹{total:,}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:12px;font-size:0.75rem;color:#555;'>🔒 Secured by 256-bit SSL encryption</div>", unsafe_allow_html=True)

        if st.button(f"Place Order · ₹{total:,}", key="place_order"):
            if not all([name, email, phone, address, city, pincode]) or state == "Select State":
                st.error("Please fill all required fields.")
            else:
                st.session_state.order_placed = True
                st.session_state.cart = {}
                st.session_state.discount = 0
                st.session_state.coupon_applied = None
                go("order_success")

    st.markdown("</div>", unsafe_allow_html=True)


# ── ORDER SUCCESS ─────────────────────────────────────────────────────────────
def render_order_success():
    st.markdown("""
    <div style="text-align:center;padding:100px 40px;background:#0a0a0a;min-height:60vh;">
      <div style="font-size:5rem;margin-bottom:24px;">✅</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:3rem;color:#f0e8d8;margin-bottom:16px;">
        Order Placed!
      </div>
      <p style="color:#9b8fa8;font-size:1rem;max-width:400px;margin:0 auto 32px;line-height:1.7;">
        Thank you for shopping with GlamCart. Your jewellery will be carefully packaged 
        and delivered within 5–7 business days.
      </p>
      <div style="color:#d4af37;font-size:0.85rem;letter-spacing:2px;margin-bottom:40px;">
        ORDER #GC{str(hash(str(st.session_state.get('order_placed',''))))[-6:].upper()}
      </div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("Continue Shopping", key="post_order_shop"):
            go("home")


# ── WISHLIST PAGE ─────────────────────────────────────────────────────────────
def render_wishlist():
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Saved by You</div>
      <div class="gc-section-title">My Wishlist</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.wishlist:
        st.markdown("""
        <div style="text-align:center;padding:80px 40px;color:#555;">
          <div style="font-size:4rem;margin-bottom:20px;">❤️</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;color:#f0e8d8;margin-bottom:12px;">Nothing saved yet</div>
          <p>Heart pieces you love and find them here.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Jewellery", key="empty_wl"):
            go("shop")
        return

    wish_products = [p for p in PRODUCTS if p["id"] in st.session_state.wishlist]
    render_product_grid(wish_products, cols_n=4)


# ── ORDERS PAGE ───────────────────────────────────────────────────────────────
def render_orders():
    st.markdown("""
    <div class="gc-section-header">
      <div class="gc-section-eyebrow">Your Purchases</div>
      <div class="gc-section-title">My Orders</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.order_placed:
        st.markdown("""
        <div style="text-align:center;padding:80px 40px;color:#555;">
          <div style="font-size:4rem;margin-bottom:20px;">📦</div>
          <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;color:#f0e8d8;margin-bottom:12px;">No orders yet</div>
          <p>Your placed orders will appear here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:24px 40px;background:#0a0a0a;">
          <div class="gc-card" style="padding:24px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
              <div style="font-family:'Cormorant Garamond',serif;font-size:1.2rem;color:#f0e8d8;">Recent Order</div>
              <span style="color:#4caf50;font-size:0.8rem;background:rgba(76,175,80,0.1);padding:4px 12px;border:1px solid #4caf50;">Confirmed</span>
            </div>
            <div style="font-size:0.8rem;color:#666;margin-bottom:8px;">Placed today · Expected delivery in 5–7 days</div>
            <div style="color:#d4af37;font-size:0.85rem;">Track your order via SMS & Email</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("Shop More", key="orders_shop"):
            go("shop")


# ── ROUTER ────────────────────────────────────────────────────────────────────
render_navbar()

page = st.session_state.page
if page == "home":
    render_home()
elif page == "shop":
    render_shop()
elif page == "product":
    render_product_detail()
elif page == "cart":
    render_cart()
elif page == "checkout":
    render_checkout()
elif page == "order_success":
    render_order_success()
elif page == "wishlist":
    render_wishlist()
elif page == "orders":
    render_orders()
