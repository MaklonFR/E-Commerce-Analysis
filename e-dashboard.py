# Menyiapkan DataFrame
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# create_daily_orders_df() digunakan untuk menyiapkan daily_orders_df
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# create_sum_order_items_df() bertanggung jawab untuk menyiapkan sum_orders_items_df
def create_sum_order_items_df(df):
    sum_order_items_df =  df.groupby(df["product_category_name_english"])["order_id"].nunique().reset_index().sort_values("order_id", ascending=False).head(10)
    return sum_order_items_df

# create_bycities_df() digunakan untuk menyiapkan bycities_df
def create_bycity_df(df):
    bycity_df = df['customer_city'].value_counts().reset_index().head(10)
    # Mengganti nama kolom
    bycity_df.columns = ['customer_city', 'customer_count']
    
    return bycity_df

# create_bystate_df() digunakan untuk menyiapkan bystate_df
def create_bystate_df(df):
    bystate_df = df['customer_state'].value_counts().reset_index().head(10)
    # Mengganti nama kolom
    bystate_df.columns = ['customer_state', 'customer_count']
    
    return bystate_df


# create_rfm_df() bertanggung jawab untuk menghasilkan rfm_df
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df


all_df = pd.read_csv("all_data_df.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Membuat Komponen Filter
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Dicoding Collection Dashboard :sparkles:')

st.subheader('A. Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.write("")

st.subheader("B. Jumlah Tingkat Kepuasan Pelanggan")

# Mapping nilai 1-5 ke kategori
rating_mapping = {
    1: "Sangat Buruk(1)",
    2: "Buruk(2)",
    3: "Cukup(3)",
    4: "Baik(4)",
    5: "Sangat Baik(5)"
}

rating_counts = all_df['review_score'].map(rating_mapping).value_counts().sort_index()

# Membuat Pie Chart
fig, ax = plt.subplots(figsize=(6, 6))
ax.pie(
    rating_counts, 
    labels=rating_counts.index, 
    autopct='%1.1f%%', 
    colors=plt.cm.Paired.colors,  # Palet warna
    startangle=90
)

# Menampilkan di Streamlit
st.pyplot(fig)

st.write("")

st.subheader("C. Pemesanan Kategori Produk yang paling banyak dan paling sedikit")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 10))

# Highest no. of orders
toporders_productcat = all_df.groupby(all_df["product_category_name_english"])["order_id"].nunique().reset_index().sort_values("order_id", ascending=False).head(10)

sns.barplot(x = "order_id", y = "product_category_name_english", data = toporders_productcat, palette='Spectral', ax=ax[0], legend=False, hue='product_category_name_english')
ax[0].set_xlabel("Jumlah Order")
ax[0].set_ylabel("Kategori Produk")
ax[0].set_title("Kategori Produk yang paling banyak Order")

# Lowest no. of orders
loworders_productcat = all_df.groupby(all_df["product_category_name_english"])["order_id"].nunique().reset_index().sort_values("order_id", ascending=True).head(10)

sns.barplot(x = "order_id", y = "product_category_name_english", data = loworders_productcat, palette='Spectral', ax=ax[1], legend=False, hue='product_category_name_english')
ax[1].set_xlabel("Jumlah Order")
ax[1].set_ylabel("Kategori Produk")
ax[1].set_title("Kategori Produk yang paling Sedikit Order")
ax[1].yaxis.set_label_position("right")

# Menampilkan di Streamlit
st.pyplot(fig)

st.write("")

st.subheader("D. Customer Demographics")
st.markdown('**1. PELANGGAN BERDASARKAN KOTA**')
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="customer_count", 
    y="customer_city",
    data= bycity_df.sort_values(by="customer_count", ascending=False),
    palette='Spectral',
    ax=ax 
)
ax.set_title("Jumlah pelanggan berdasarkan kota", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.markdown('**2. PELANGGAN BERDASARKAN TEMPAT**')
fig, ax = plt.subplots(figsize=(24, 12))
sns.barplot(
    x="customer_count", 
    y="customer_state",
    data= bystate_df.sort_values(by="customer_count", ascending=False),
    palette='Spectral',
    ax=ax 
)
ax.set_title("Jumlah pelanggan berdasarkan tempat (state)", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
 
sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(3), palette='dark:#5A9_r', legend=False, hue='customer_unique_id', ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_unique_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

# Mengatur teks sumbu X agar menurun (tegak lurus)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=90, ha="right")
 
sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(3), palette='dark:#5A9_r', legend=False, hue='customer_unique_id', ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_unique_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
# Mengatur teks sumbu X agar menurun (tegak lurus)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=90, ha="right")

sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(3), palette='dark:#5A9_r', legend=False, hue='customer_unique_id', ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_unique_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
# Mengatur teks sumbu X agar menurun (tegak lurus)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=90, ha="right")

st.pyplot(fig)


st.caption('Copyright (c) Dicoding 2025')