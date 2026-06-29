# 💎 GlamCart – Fine Jewellery Shopping App

A full-featured jewellery e-commerce app built with Python & Streamlit, inspired by Flipkart.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🏠 **Home Page** – Hero banner, category grid, featured & trending collections
- 🛍️ **Shop Page** – Filter by category, material, price range; sort options
- 🔍 **Search** – Real-time product search across name, category, material
- 💍 **Product Detail** – Full specs, related products, add to cart/wishlist
- 🛒 **Cart** – Quantity controls, coupon codes, order summary
- 💳 **Checkout** – Address form, multiple payment methods
- ❤️ **Wishlist** – Save favourite pieces
- 📦 **Order Tracking** – Order confirmation & history

## 📦 Project Structure

```
glamcart/
├── app.py              # Main Streamlit application
├── data.py             # Product catalogue (21+ products)
├── utils.py            # Cart, wishlist, coupon, filter logic
├── requirements.txt    # Dependencies
├── .streamlit/
│   └── config.toml     # Dark theme configuration
└── README.md
```

## 🚀 Deploy on Streamlit Cloud (GitHub)

### Step 1 – Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: GlamCart jewellery app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/glamcart.git
git push -u origin main
```

### Step 2 – Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"New app"**
3. Connect your **GitHub account**
4. Select your repo: `YOUR_USERNAME/glamcart`
5. Set **Main file path**: `app.py`
6. Click **"Deploy!"**

Your app will be live at:
`https://YOUR_USERNAME-glamcart-app-XXXX.streamlit.app`

## 🏃 Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/glamcart.git
cd glamcart

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open your browser at `http://localhost:8501`

## 🎫 Coupon Codes (for testing)

| Code       | Discount |
|------------|----------|
| `GLAM20`   | 20% off  |
| `FIRST10`  | 10% off  |
| `GOLD15`   | 15% off  |
| `DIWALI25` | 25% off  |
| `WELCOME5` | 5% off   |

## 🎨 Tech Stack

- **Frontend/Backend**: Python + Streamlit
- **Styling**: Custom CSS (Google Fonts: Cormorant Garamond + Inter)
- **State management**: Streamlit session state
- **Deployment**: Streamlit Cloud (free)

---
Made with ❤️ in India
