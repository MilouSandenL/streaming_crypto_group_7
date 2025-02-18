import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
import pandas as pd
from constants import (
    POSTGRES_USER,
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
)
from charts import line_chart

# Koppla dashboarden upp till databasen
connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"
engine = create_engine(connection_string)

# Funktion för att hämta data
def load_data(symbol):
    query = f"SELECT * FROM trx WHERE symbol = '{symbol}' ORDER BY timestamp DESC LIMIT 100"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
    return df

# Funktion för att formatera stora siffror till mer lättläst format
def format_number(value, suffix=""):
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B{suffix}"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M{suffix}"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K{suffix}"
    return f"{value:.2f}{suffix}"

# Layout för dashboard
def layout():
    st.title("📊 Crypto Live Dashboard")

    # Dropdowns för val av kryptovaluta och valuta
    crypto_choice = st.selectbox("Välj kryptovaluta", ["TRX", "BTC", "ETH"])  
    currency_choice = st.selectbox("Välj valuta", ["SEK", "NOK", "DKK", "EUR", "ISK"])

    df = load_data(crypto_choice)

    if df.empty:
        st.warning("Ingen data tillgänglig ännu. Vänta på uppdateringar...")
        return

    latest = df.iloc[0]

    # Nyckeltal
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"💰 Pris ({currency_choice})", f"{latest[f'price_{currency_choice.lower()}']:.2f} {currency_choice}")
    col2.metric("📉 Prisändring 24h", format_number(latest["percent_change_24h"], "%"), delta=latest["percent_change_24h"])
    col3.metric("📊 24h Volym", format_number(latest["volume_24h"]))
    col4.metric("📈 Volymändring 24h", format_number(latest["volume_change_24h"], "%"), delta=latest["volume_change_24h"])

    # Prisutveckling
    st.markdown(f"### 📈 {crypto_choice} Pris i {currency_choice}")
    fig_price = line_chart(df.index, df[f"price_{currency_choice.lower()}"], title="Pris över tid", xlabel="Tid", ylabel=f"Pris ({currency_choice})")
    st.pyplot(fig_price)

    # Handelsvolym
    st.markdown(f"### 📊 Handelsvolym för {crypto_choice}")
    fig_volume = line_chart(df.index, df["volume_24h"], title="Volym över tid", xlabel="Tid", ylabel="Volym")
    st.pyplot(fig_volume)

if __name__ == "__main__":
    layout()
