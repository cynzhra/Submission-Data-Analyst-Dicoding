import streamlit as st
import pandas as pd
import func  # Import functions from func.py
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
orders = pd.read_csv('orders_dataset.csv', parse_dates=['order_purchase_timestamp'])
order_items = pd.read_csv('order_items_dataset.csv')
products = pd.read_csv('products_dataset.csv')
geolocation = pd.read_csv('geolocation_dataset.csv')
order_payments = pd.read_csv('order_payments_dataset.csv')
customers = pd.read_csv('customers_dataset.csv')

st.title("E-commerce Analytics Dashboard")

# Sidebar for navigation
tab1, tab2, tab3 = st.tabs(['Best-Selling Products', 'Customer Spending Tiers', 'Top Geographical Location'])

with tab1:

    # Get the data for best-selling products
    best_selling_products, increasing_trend, declining_trend = func.get_best_selling_products(order_items, orders, products)
    
    st.subheader("Best-Selling Products Per Year")
    st.dataframe(best_selling_products[['year', 'product_category_name', 'sales_count']])
    # Plot of the best-selling products every year
    
    plt.figure(figsize=(10,6))
    plt.bar(best_selling_products['year'], best_selling_products['sales_count'], color='skyblue')
    plt.title('Best-Selling Products Per Year')
    plt.xlabel('Year')
    plt.ylabel('Sales Count')
    plt.show()
    st.pyplot(plt)
    
    # Visualize sales trends
    st.subheader("Sales Trend of Products by Month")
    
    # Add month column for monthly analysis
    orders['month'] = orders['order_purchase_timestamp'].dt.to_period('M')
    order_items_df = pd.merge(order_items, orders[['order_id', 'month']], on='order_id')
    order_items_df = pd.merge(order_items_df, products[['product_id', 'product_category_name']], on='product_id')

    # Group product sales by month and product category
    product_sales_monthly = order_items_df.groupby(['product_category_name', 'month']).size().unstack().fillna(0)
    
    # Convert index 'month' from Period to string so matplotlib can handle
    product_sales_monthly.columns = product_sales_monthly.columns.astype(str)

    example_product_category = st.selectbox('Select Product Category to Visualize', product_sales_monthly.index)
    
    product_sales_monthly.columns = product_sales_monthly.columns.astype(str)

    # Visualization of product sales trends by month
    plt.figure(figsize=(10,6))
    plt.plot(product_sales_monthly.columns, product_sales_monthly.loc[example_product_category], marker='o')
    plt.title(f'Sales Trend of Product Category {example_product_category} by Month')
    plt.xlabel('Month')
    plt.ylabel('Sales Count')
    plt.xticks(rotation=45)
    plt.show()
    st.pyplot(plt)

    st.subheader("Products with Increasing Trend")
    st.dataframe(increasing_trend.head())

    st.subheader("Products with Declining Trend")
    st.dataframe(declining_trend.head())

with tab2:
    st.header("Customer Spending Tiers")

    # Get spending tiers and summary statistics
    customer_spending, spending_summary = func.group_customers_by_spending(order_items, order_payments, orders)
    
    st.subheader("Customer Spending Distribution")
    st.dataframe(customer_spending.head())

    st.subheader("Spending Tier Summary")
    st.dataframe(spending_summary)

    # Visualize spending distribution
    plt.figure(figsize=(8, 6))
    sns.countplot(data=customer_spending, x='spending_tier', palette='coolwarm')
    plt.title('Customer Distribution Across Spending Tiers')
    plt.xlabel('Spending Tiers')
    plt.ylabel('Number of Customers')
    plt.show()
    st.pyplot(plt)
    
    # Bar plot of average spending in each tier
    plt.figure(figsize=(8, 6))
    sns.barplot(data=spending_summary, x='spending_tier', y=('total_spending', 'mean'), palette='viridis')
    plt.title('Average Spending per Tier')
    plt.xlabel('Spending Tiers')
    plt.ylabel('Average Spending ($)')
    plt.show()
    st.pyplot(plt)

with tab3:
    st.header("Top Geographical Locations")

    # Get top geographical locations
    top_location = func.get_top_geographical_location(orders, geolocation, customers)
    
    st.subheader("Geographical Location with Most Orders")
    st.dataframe(top_location.head())

    # Visualize top locations
    st.subheader("Top Cities by Orders")
    top_cities = top_location.groupby('geolocation_city')['order_count'].sum().sort_values(ascending=True).head(10)
    plt.figure(figsize=(10, 6))
    top_cities.plot(kind='barh', color='skyblue')
    plt.title('Top Cities by Orders')
    plt.xlabel('Number of Orders')
    plt.ylabel('City')
    st.pyplot(plt)
    
    # Map visualization for top locations
    st.subheader('Map of Top 10 Locations by Order Count')

    # Select only relevant columns for mapping
    top_locations_map = top_location[['geolocation_lat', 'geolocation_lng']].rename(columns={
        'geolocation_lat': 'lat',
        'geolocation_lng': 'lon'
    })

    # Plot map using Streamlit's map function
    st.map(top_locations_map)


st.caption('Copyright (C) Cynthia Nur Azzahra 2024')