
# Create your views here.
# views.py
import os
import pandas as pd
import numpy as np
from django.shortcuts import render
from sklearn.linear_model import LinearRegression
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_monthly(df, date_col, group_col, value_col): #mengelompokan data menjadi per bulan
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    grouped = df.groupby([group_col, 'year', 'month'])[value_col].sum().reset_index()
    return grouped

def forecast_and_plot(grouped_df, entity_col, value_col, title): #untuk membuat prediksi
    plots = []
    for name, group in grouped_df.groupby(entity_col):
        group = group.sort_values(['year', 'month'])
        group['t'] = np.arange(len(group))
        X = group[['t']] 
        y = group[value_col]

        if len(X) < 2:
            continue  # Skip entitas dengan data terlalu sedikit

        model = LinearRegression().fit(X, y)     #prediksi
        group['prediction'] = model.predict(X)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=group['t'], y=group[value_col], mode='lines+markers', name='Actual'))
        fig.add_trace(go.Scatter(x=group['t'], y=group['prediction'], mode='lines+markers', name='Predicted'))
        fig.update_layout(title=f"{title}: {name}", xaxis_title="Time", yaxis_title=value_col)
        plots.append(fig.to_html(full_html=False))

    return plots

def chart_view(request):
    gabungan_path = os.path.join(BASE_DIR, 'buin_gabungan.csv')
    df = pd.read_csv(gabungan_path)

    # Pastikan kolom 'Order Date' bisa diparse
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Order Date'])

    # --- Visualisasi 1: Most Used Payment Methods ---
    if 'PaymentMode' in df.columns:
        payment_counts = df['PaymentMode'].value_counts().reset_index()
        payment_counts.columns = ['PaymentMode', 'count']
        payment_chart = px.bar(payment_counts, x='PaymentMode', y='count', title='Most Used Payment Methods')
        payment_chart_html = payment_chart.to_html(full_html=False)
    else:
        payment_chart_html = "<p>Kolom 'PaymentMode' tidak ditemukan.</p>"

    # --- Visualisasi 2: Quantity by Product Category ---
    if 'Category' in df.columns and 'Quantity' in df.columns:
        category_group = df.groupby('Category')['Quantity'].sum().reset_index()
        category_chart = px.bar(category_group, x='Category', y='Quantity', title='Quantity Sold by Product Category')
        category_chart_html = category_chart.to_html(full_html=False)
    else:
        category_chart_html = "<p>Kolom 'Category' atau 'Quantity' tidak ditemukan.</p>"

    # --- Visualisasi 3: Sales by State and City ---
    if all(col in df.columns for col in ['State', 'City', 'Quantity']):
        df['CityFull'] = df['City'] + ', ' + df['State']
        location_group = df.groupby(['State', 'City'])['Quantity'].sum().reset_index()
        location_chart = px.sunburst(location_group, path=['State', 'City'], values='Quantity',
                                     title='Quantity Sold by State and City')
        location_chart_html = location_chart.to_html(full_html=False)
    else:
        location_chart_html = "<p>Kolom lokasi atau jumlah tidak lengkap.</p>"

    # === PREDIKSI ===
    payment_monthly = generate_monthly(df, 'Order Date', 'PaymentMode', 'Quantity')
    payment_forecasts = forecast_and_plot(payment_monthly, 'PaymentMode', 'Quantity', 'Forecast: Payment Mode Usage')

    category_monthly = generate_monthly(df, 'Order Date', 'Category', 'Quantity')
    category_forecasts = forecast_and_plot(category_monthly, 'Category', 'Quantity', 'Forecast: Product Category Sales')

    city_monthly = generate_monthly(df, 'Order Date', 'CityFull', 'Quantity')
    city_forecasts = forecast_and_plot(city_monthly, 'CityFull', 'Quantity', 'Forecast: Sales by City')

    context = {
        'payment_chart': payment_chart_html,
        'category_chart': category_chart_html,
        'location_chart': location_chart_html,
        'payment_forecasts': payment_forecasts,
        'category_forecasts': category_forecasts,
        'city_forecasts': city_forecasts,
    }

    return render(request, 'buin/chart.html', context)
