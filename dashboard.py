import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

# Menyiapkan day_rent_df
def create_day_rent_df(df):
    day_rent_df = df.groupby(by="dteday").agg({
        "cnt": "sum"
    }).reset_index()
    return day_rent_df

# Menyiapkan day_casual_rent_df
def create_day_casual_rent_df(df):
    day_casual_rent_df = df.groupby(by="dteday").agg({
        "casual": "sum"
    }).reset_index()
    return day_casual_rent_df

# Menyiapkan day_registered_rent_df
def create_day_registered_rent_df(df):
    day_registered_rent_df = df.groupby(by="dteday").agg({
        "registered": "sum"
    }).reset_index()
    return day_registered_rent_df


# Load berkas bike_day_data.csv
bike_day_df = pd.read_csv("bike_day_data.csv")

# Mengubah kolom menjadi datetime untuk pembuatan filter
datetime_columns = ["dteday"]
bike_day_df.sort_values(by="dteday", inplace=True)
bike_day_df.reset_index(inplace=True)

for column in datetime_columns:
    bike_day_df[column] = pd.to_datetime(bike_day_df[column])

# Filter data, membuat komponen filter
min_date = bike_day_df["dteday"].min()
max_date = bike_day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# menyimpan data yang telah difilter
main_df = bike_day_df[(bike_day_df["dteday"] >= str(start_date)) & 
                (bike_day_df["dteday"] <= str(end_date))]


# menghasilkan dataframe dari helper function
day_df = create_day_rent_df(main_df)
casual_df = create_day_casual_rent_df(main_df)
registered_df = create_day_registered_rent_df(main_df)

# Melengkapi Dashboard dengan Visualisasi Data 
st.header("Dicoding Rental Bike Dashboard :sparkles:") #tampilan header

st.subheader("Rentals Harian")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    day_casual_rent = casual_df["casual"].sum()
    st.metric("Pengguna Casual", value=day_casual_rent)
 
with col2:
    day_rent_registered = registered_df["registered"]. sum()
    st.metric("Pengguna Registered ", value=day_rent_registered)

with col3:
    total_day_rent = day_df["cnt"].sum()
    st.metric("Jumlah seluruh pengguna", value=total_day_rent)

# === VISUALISASI RFM === 
st.subheader("Pengguna Terbaik Berdasarkan Parameter RFM (instant/record index)")  
# Hitung recency (hari sejak terakhir transaksi)
bike_day_df["recency"] = (bike_day_df["dteday"].max() - bike_day_df["dteday"]).dt.days

# Hitung frequency (jumlah transaksi)
bike_day_df["frequency"] = bike_day_df.groupby("cnt")["cnt"].transform("count")

# Hitung monetary (total nilai transaksi)
bike_day_df["monetary"] = bike_day_df["cnt"] * bike_day_df["registered"]

# Analisis RFM
rfm_data = bike_day_df[["instant", "recency", "frequency", "monetary"]]

col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_data.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_data.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_data.monetary.mean(), "AUD", locale="es_CO") 
    st.metric("Average Monetary", value=avg_frequency)

# Membuat subplot untuk menampung 3 histplot
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Visualisasi recency
sns.histplot(rfm_data["recency"], bins=20, color="skyblue", edgecolor="black", ax=axes[0])
axes[0].set_xlabel("Recency (days)")
axes[0].set_ylabel("Count")
axes[0].set_title("Distribution of Recency")

# Visualisasi frequency
sns.histplot(rfm_data["frequency"], bins=20, color="yellow", edgecolor="black", ax=axes[1])
axes[1].set_xlabel("Frequency")
axes[1].set_ylabel("Count")
axes[1].set_title("Distribution of Frequency")

# Visualisasi monetary
sns.histplot(rfm_data["monetary"], bins=20, color="orange", edgecolor="black", ax=axes[2])
axes[2].set_xlabel("Monetary Value")
axes[2].set_ylabel("Count")
axes[2].set_title("Distribution of Monetary")

st.pyplot(fig)

# === VISUALISASI Trend Jumlah total rental bike 2011 dan 2012 ===
st.subheader("Trend Jumlah Rental Bike tahun 2011 dan 2012")
bike_day_df["mnth"] = pd.Categorical(bike_day_df["mnth"], categories=
    ["January","February","March","April","May","June","July","August","September","October","November","December"],
    ordered=True)

bike_month = bike_day_df.groupby(by=["yr", "mnth"], observed=False).agg({
    "cnt": "sum"
})

fig = plt.figure(figsize=(10, 5))
sns.lineplot(
    data = bike_month,
    x = "mnth",
    y = "cnt",
    hue = "yr",
    palette = "bright",
    marker = "o"
)
plt.xlabel(None)
plt.ylabel(None)
plt.xticks(fontsize=10, rotation=45)
plt.yticks(fontsize=10)
plt.legend(title = "Tahun", loc = "upper right")
plt.gca().xaxis.grid(False)
st.pyplot(fig)

# === VISUALISASI Jumlah Rata-rata Rental Bike Berdasarkan Kondisi Cuaca dan Musim ===
st.subheader("Jumlah Rata-rata Rental Bike Berdasarkan Kondisi Cuaca dan Musim")
fig = plt.figure(figsize=(12, 6))
 
sns.barplot(
    y="cnt", 
    x="season",
    data=bike_day_df.groupby(by=["season", "weathersit"]).agg({
    "cnt": "mean",}),
    hue="weathersit",
    palette="deep"
)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis="both", labelsize=12)
plt.legend(title = "Kondisi Cuaca")
st.pyplot(fig)

# === VISUALISASI Perbandingan Jumlah Rental Bike Antara Pengguna Casual dan Registered ===
st.subheader("Perbandingan Jumlah Rental Bike Antara Pengguna Casual dan Registered")

users = bike_day_df.groupby(by=["yr"]).agg({
    "casual": "mean",
    "registered": "mean"
}).reset_index()

fig = plt.figure(figsize=(8, 6))
sns.lineplot(data=users, x=users["yr"], y=users["casual"], marker="o", label="Pengguna Casual", linewidth=3)
sns.lineplot(data=users, x=users["yr"], y=users["registered"], marker="o", label="Pengguna Registered", linewidth=3)
plt.xlabel("Tahun")
plt.ylabel("Rata-rata Pengguna Setiap Hari")
plt.ylim(0)
plt.legend()
st.pyplot(fig)

# === VISUALIASI Perbandingan Jumlah Rental Bike Berdasarkan Holiday dan Working Day ===
st.subheader("Perbandingan Jumlah Rental Bike Berdasarkan Holiday dan Working Day")
holiday = bike_day_df.groupby(by=["holiday"]).agg({
    "cnt": "sum"
})

working_day = bike_day_df.groupby(by=["workingday"]).agg({
    "cnt": "sum"
})

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10, 10))
palette_color = sns.color_palette("pastel") 
ax[0].pie(holiday["cnt"], labels=holiday.index, autopct="%1.1f%%", explode=[0.05, 0], colors=palette_color)
ax[0].set_title("Perbandingan Rental Bike Berdasarkan Holiday")

ax[1].pie(working_day["cnt"], labels=working_day.index, autopct="%1.1f%%", explode=[0.05, 0], colors=palette_color)
ax[1].set_title("Perbandingan Rental Bike Berdasarkan Working Day")

st.pyplot(fig)

# === VISUALISASI Perbandingan Rental Pada weekday ===
st.subheader("Perbandingan Rental Bike pada Weekday")
bike_day_df.groupby(by=["weekday"], observed=False).agg({
    "cnt": "sum"
})

fig = plt.figure(figsize=(12, 6))
 
sns.barplot(
    y="cnt", 
    x="weekday",
    data=bike_day_df.groupby(by=["weekday"], observed=False).agg({
    "cnt": "mean"})
)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis="both", labelsize=12)
st.pyplot(fig)