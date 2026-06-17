import httpx
import os
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI(title="Live Indian Gold Extractor")

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify ["http://127.0.0.1:8000"] for stricter control)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount templates directory as static files
template_dir = Path(__file__).parent.parent / "templates"
if template_dir.exists():
    app.mount("/templates", StaticFiles(directory=template_dir), name="templates")

# Your GoldAPI.io Key (use the GOLDAPI_KEY env var in production)
API_KEY = os.getenv("GOLDAPI_KEY", "goldapi-0fe4df5cc0dbf15d654646768817da80-io")
HEADERS = {"x-access-token": API_KEY}

@app.get("/")
async def root():
    return {"message": "Gold Live Rate API is running", "docs": "/docs", "endpoint": "/api/gold-rates", "ui": "/ui"}

@app.get("/ui")
async def get_ui():
    try:
        with open(Path(__file__).parent.parent / "templates" / "index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except:
        return HTMLResponse(content="<h1>UI not found</h1>", status_code=404)

@app.get("/health")
async def health():
    return {"status": "ok"}

async def fetch_historical_price(client, date_str):
    """Helper function to fetch real historical data from GoldAPI"""
    url = f"https://www.goldapi.io/api/XAU/INR/{date_str}"
    try:
        response = await client.get(url, headers=HEADERS)
        data = response.json()
        return data.get("price", 0)
    except:
        return 0

@app.get("/api/gold-rates")
async def get_live_gold_rates():
    today = datetime.now()
    
    async with httpx.AsyncClient() as client:
        # --- 1. EXTRACT REAL LIVE DATA (XAU to INR) ---
        live_url = "https://www.goldapi.io/api/XAU/INR"
        
        try:
            live_response = await client.get(live_url, headers=HEADERS)
            live_data = live_response.json()
            # This returns the real live price of 1 Troy Ounce in Indian Rupees
            live_price_ounce_inr = live_data["price"]
        except Exception as e:
            # If GoldAPI is unreachable, return a safe demo response so the UI still shows data
            demo_now = today
            demo_current = 152983.48
            demo_previous = [152883.48, 152783.48, 152430.00, 151980.00]
            previous_prices = []
            for i, p in enumerate(demo_previous, start=1):
                past_date = demo_now - timedelta(days=i)
                previous_prices.append({
                    'date': past_date.strftime('%d %b %Y'),
                    'price': round(p, 2)
                })

            # simple prediction: current + average change
            historical_trajectory = list(reversed(demo_previous))
            historical_trajectory.append(demo_current)
            fluctuations = [historical_trajectory[k] - historical_trajectory[k-1] for k in range(1, len(historical_trajectory))]
            if fluctuations:
                average_fluctuation = sum(fluctuations) / len(fluctuations)
            else:
                average_fluctuation = 0

            predicted_price = round(demo_current + average_fluctuation, 2)
            return {
                'current_price': round(demo_current, 2),
                'previous_prices': previous_prices,
                'predicted_price': predicted_price,
                'trend_status': 'Demo data (GoldAPI unreachable)',
                'last_updated': demo_now.strftime('%d %b %Y, %I:%M %p'),
                'sample': True,
                'error': 'Failed to connect to GoldAPI. Showing demo data.'
            }

        # --- 2. CONVERT TO INDIAN 10-GRAM STANDARD ---
        def convert_to_10g(ounce_price):
            # 1 Troy Ounce = 31.1034768 Grams
            gram_price = ounce_price / 31.1034768
            base_10g_price = gram_price * 10
            
            # Add India's 15% Import Duty (10% BCD + 5% AIDC)
            indian_retail_price = base_10g_price * 1.15
            
            return round(indian_retail_price, 2)

        # Now this will output ~₹1,51,000+ perfectly!
        live_price_10g_inr = convert_to_10g(live_price_ounce_inr)


        # --- 3. EXTRACT REAL PREVIOUS 5 DAYS DATA ---
        previous_prices = []
        historical_trajectory = []
        
        # We loop backward 5 days and make an API call for each specific date
        for i in range(1, 6):
            past_date = today - timedelta(days=i)
            # GoldAPI requires the date format to be YYYYMMDD
            date_str = past_date.strftime('%Y%m%d')
            
            # Fetch the real price for that specific day
            past_ounce_price = await fetch_historical_price(client, date_str)
            
            if past_ounce_price > 0:
                past_10g_price = convert_to_10g(past_ounce_price)
                previous_prices.append({
                    'date': past_date.strftime('%d %b %Y'),
                    'price': past_10g_price
                })
                historical_trajectory.append(past_10g_price)

        # Reverse the trajectory so it goes from oldest to newest for the math
        historical_trajectory.reverse()
        historical_trajectory.append(live_price_10g_inr)
        
        # --- 4. CALCULATE PREDICTION BASED ON REAL DATA ---
        fluctuations = [
            historical_trajectory[k] - historical_trajectory[k-1] 
            for k in range(1, len(historical_trajectory))
        ]
        
        if fluctuations:
            average_fluctuation = sum(fluctuations) / len(fluctuations)
            predicted_price = round(live_price_10g_inr + average_fluctuation, 2)
            trend_status = "Bullish (Upward Momentum)" if average_fluctuation > 0 else "Bearish (Downward Consolidation)"
        else:
            predicted_price = live_price_10g_inr
            trend_status = "Insufficient historical data"

    return {
        'current_price': live_price_10g_inr,
        'previous_prices': previous_prices,
        'predicted_price': predicted_price,
        'trend_status': trend_status,
        'last_updated': today.strftime('%d %b %Y, %I:%M %p')
    }