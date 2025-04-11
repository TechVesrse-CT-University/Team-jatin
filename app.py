import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date, datetime, timedelta
from openai import OpenAI
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from bs4 import BeautifulSoup



client = OpenAI(
    api_key="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"
)

st.set_page_config(page_title="AgroSphere", layout="wide")


# 🧭 Select Location
st.title("🌿 Welcome, Farmer!")
st.subheader("Smart tools to help you grow more.")


# Define state and market dropdowns
states = {
    "Maharashtra": ["Pune", "Nashik", "Nagpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Patiala"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi"]
}

crop_quality_data = {
    "Maharashtra": {
        "Pune": {
            "Tomato": 8,
            "Wheat": 7,
            "Onion": 6,
            "Potato": 7,
            "Rice": 8,
        },
        "Nashik": {
            "Tomato": 7,
            "Wheat": 6,
            "Onion": 8,
            "Potato": 6,
            "Rice": 7,
        }
    },
    "Punjab": {
        "Ludhiana": {
            "Tomato": 8,
            "Wheat": 7,
            "Onion": 6,
            "Potato": 7,
            "Rice": 8,
        },
        "Amritsar": {
            "Tomato": 9,
            "Wheat": 8,
            "Onion": 7,
            "Potato": 7,
            "Rice": 9,
        },
        "Patiala": {
            "Tomato": 7,
            "Wheat": 6,
            "Onion": 6,
            "Potato": 7,
            "Rice": 7,
        }
    }
}

selected_state = st.selectbox("Choose your State", list(states.keys()))
selected_market = st.selectbox("Choose your Market", states[selected_state])

# --- Live Scraper (Simulated) ---
def scrape_agmarknet_prices(state, market):
    today = date.today().strftime('%Y-%m-%d')
    crops = ["Tomato", "Wheat", "Onion", "Potato", "Rice"]
    prices = []

    for crop in crops:
        prices.append({
            "state": state,
            "market": market,
            "crop": crop,
            "modal_price": 2000 + hash(crop + market) % 400,
            "min_price": 1800 + hash(crop + market) % 200,
            "max_price": 2200 + hash(crop + state) % 300,
            "unit": "Rs/Quintal",
            "date": today
        })

    df = pd.DataFrame(prices)
    df.to_csv("mandi_data.csv", index=False)
    return df

df_scraped = scrape_agmarknet_prices(selected_state, selected_market)

st.markdown("### 🌤️ 7-Day Weather Forecast")
try:
    geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={selected_market}&count=1").json()
    if "results" in geo:
        lat = geo['results'][0]['latitude']
        lon = geo['results'][0]['longitude']
        res = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,weathercode&timezone=auto"
        ).json()
        days = res["daily"]["time"]
        temps = res["daily"]["temperature_2m_max"]
        codes = res["daily"]["weathercode"]
        emoji_map = {
            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
            45: "🌫️", 48: "🌫️", 51: "🌦️",
            61: "🌧️", 63: "🌧️", 65: "🌧️",
            80: "🌧️", 95: "⛈️"
        }
        cols = st.columns(7)
        for i in range(7):
            with cols[i]:
                st.markdown(f"**{days[i]}**")
                st.markdown(emoji_map.get(codes[i], "❓"))
                st.markdown(f"`{temps[i]}°C`")
    else:
        st.warning("⚠️ Couldn't find coordinates.")
except Exception as e:
    st.warning(f"⚠️ Could not load weather: {str(e)}")

# --- Mandi Price Display ---
st.markdown("### 🏪 Mandi Prices (Live)")
if not df_scraped.empty:
    st.dataframe(df_scraped)
else:
    st.warning("❌ No mandi data available.")

# --- Crop Quality Comparison Button ---
if st.button("Compare Crop Quality Across Cities"):

    # Loop through each crop and compare across cities
    for crop in ["Tomato", "Wheat", "Onion", "Potato", "Rice"]:
        crop_names = list(crop_quality_data[selected_state].keys())
        crop_qualities = [crop_quality_data[selected_state][city].get(crop, 0) for city in crop_names]

        # Plot bar chart for crop quality comparison
        fig = go.Figure([go.Bar(x=crop_names, y=crop_qualities)])
        fig.update_layout(
            title=f"Quality Comparison of {crop} in {selected_state}",
            xaxis_title="Cities",
            yaxis_title="Quality Rating",
            template="plotly_dark"
        )
        st.plotly_chart(fig)

# --- Price Prediction Button & Logic ---
st.markdown("### 📊 Predict Future Crop Prices")
if st.button("📈 Predict Prices"):

    today = datetime.today()
    prediction_data = []

    for crop in df_scraped["crop"]:
        # Get base price from scraped data
        base_price = df_scraped[df_scraped["crop"] == crop]["modal_price"].values[0]

        # Simulate 15 days of historical prices
        history = [base_price + np.random.normal(0, 30) for _ in range(15)]
        days = np.arange(15).reshape(-1, 1)
        prices = np.array(history)

        # Linear Regression Model
        model = LinearRegression()

        model.fit(days, prices)

        # Predict next 7 days
        future_days = np.arange(15, 22).reshape(-1, 1)
        future_prices = model.predict(future_days)
        future_dates = [today + timedelta(days=i) for i in range(1, 8)]

        # Collect for table
        for i in range(7):
            prediction_data.append({
                "crop": crop,
                "date": future_dates[i],
                "predicted_price": round(future_prices[i], 2)
            })

        # --- Plotly Chart per Crop ---
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[today - timedelta(days=i) for i in reversed(range(15))],
            y=history,
            mode='lines+markers',
            name='Past Prices',
            line=dict(color='green'),
            marker=dict(size=6)
        ))
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=future_prices,
            mode='lines+markers',
            name='Predicted Prices',
            line=dict(color='orange', dash='dash'),
            marker=dict(size=7)
        ))
        fig.update_layout(
            title=f"{crop} Price Prediction – {selected_market}",
            xaxis_title="Date",
            yaxis_title="Price (₹/Quintal)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    df_pred = pd.DataFrame(prediction_data)
    st.markdown("### 📋 Predicted Prices Table")
    st.dataframe(df_pred)

# --- ChatBot Section ---
st.markdown("### 🤖 Ask AgroBot")
user_input = st.text_input("Ask your farming question...")
if user_input:
    with st.spinner("Thinking..."):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are AgroBot, helping farmers in simple Hinglish."},
                    {"role": "user", "content": user_input}
                ]
            )
            st.success(response.choices[0].message.content)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


# --- Disease & Adulteration Detection ---
st.markdown("### 🧪 Diagnose Crop Issues (Natural or Lab-Induced)")

image = st.file_uploader("📸 Upload a photo of your crop (Max 2MB)", type=["jpg", "jpeg", "png"])

if image:
    if image.size > 2 * 1024 * 1024:
        st.error("❌ Image too large! Please upload under 2MB.")
    else:
        st.image(image, caption="✅ Uploaded Crop Image", use_column_width=True)

        crop_name = st.text_input("🌾 What crop is this? (e.g., Tomato, Wheat, Rice)", placeholder="Enter crop name here")

        if crop_name:
            with st.spinner("🧠 Analyzing for natural disease or adulteration in lab..."):
                prompt = f"""
                A farmer from {selected_market}, {selected_state} has uploaded a photo of their {crop_name}.
                You are a smart AI trained in both agricultural diseases and lab adulteration diagnostics.

                Based on the crop type and the visible symptoms in the image, identify whether the issue is:
                1. A **naturally occurring disease** (caused by bacteria, fungus, pests, viruses, etc.)
                OR
                2. A **lab or chemical adulteration** (e.g., artificial coloring, fertilizer burn, chemical overdose, contamination, etc.)

                Give the response in this structure:
                - 🔍 Likely Issue Type: Natural Disease / Adulteration
                - 🧪 Name of Disease / Type of Adulteration
                - 🧠 Visible Symptoms
                - 🌱 Probable Source (weather, pests, improper storage, lab testing issues)
                - 💊 Treatment Steps
                - ✅ Prevention Tips (scientific or organic)
                - 🗣️ Language: Use **simple Hinglish** (Hindi-English mix), understandable by rural farmers.
                - 👨‍🌾 Tone: Friendly, clear, and actionable.
                """

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are AgroBot – a smart, farmer-friendly crop health expert trained in lab and natural disease diagnosis."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    st.success("🧠 Analysis Result:")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ Could not process analysis: {str(e)}")

# Define state and market dropdowns
states = {
    "Maharashtra": ["Pune", "Nashik", "Nagpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Patiala"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi"]
}

selected_state = st.selectbox("Choose your State", list(states.keys()), key="state_select")
selected_market = st.selectbox("Choose your Market", states[selected_state], key="market_select")

# --- Marketplace Feature ---
st.markdown("### 🛒 Marketplace: Sell Your Crops")

# Create form to upload crop details
crop_name = st.selectbox("Select Crop for Sale", ["Tomato", "Wheat", "Onion", "Potato", "Rice"], key="crop_select")
quantity = st.number_input("Enter Quantity (in Quintals)", min_value=1, step=1, key="quantity_input")
price_per_unit = st.number_input("Enter Price per Quintal (in Rs)", min_value=1, step=10, key="price_input")
seller_name = st.text_input("Enter Your Name", key="seller_name_input")
contact_number = st.text_input("Enter Your Contact Number", key="contact_number_input")

# Button to upload data to the marketplace
if st.button("Upload Crop for Sale", key="upload_button"):
    # Simple validation for required fields
    if not crop_name or not quantity or not price_per_unit or not seller_name or not contact_number:
        st.error("All fields are required to upload your crop.")
    else:
        # Initialize marketplace_data if it doesn't exist
        if 'marketplace_data' not in st.session_state:
            st.session_state.marketplace_data = pd.DataFrame(columns=["State", "Market", "Crop", "Quantity (Quintals)", "Price per Quintal (Rs)", "Seller Name", "Contact Number"])

        # Create a new listing
        new_listing = pd.DataFrame({
            "State": [selected_state],
            "Market": [selected_market],
            "Crop": [crop_name],
            "Quantity (Quintals)": [quantity],
            "Price per Quintal (Rs)": [price_per_unit],
            "Seller Name": [seller_name],
            "Contact Number": [contact_number]
        })

        # Concatenate the new listing with the existing marketplace data
        st.session_state.marketplace_data = pd.concat([st.session_state.marketplace_data, new_listing], ignore_index=True)

        st.success("Crop successfully listed on the marketplace!")

# --- Display Marketplace Listings ---
st.markdown("### 🛍️ Available Crops for Sale")

if 'marketplace_data' in st.session_state and not st.session_state.marketplace_data.empty:
    st.dataframe(st.session_state.marketplace_data)
else:
    st.warning("No crops listed yet. Add your crops to the marketplace!")
    




