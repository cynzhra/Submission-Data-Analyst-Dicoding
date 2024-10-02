import pandas as pd

# Function to calculate best-selling products by year
def get_best_selling_products(order_items, orders, products):
    orders['year'] = orders['order_purchase_timestamp'].dt.year
    order_items_df = pd.merge(order_items, orders[['order_id', 'year']], on='order_id')
    
    product_sales = order_items_df.groupby(['product_id', 'year']).size().reset_index(name='sales_count')
    product_sales = pd.merge(product_sales, products[['product_id', 'product_category_name']], on='product_id')

    # Find the best-selling products per year
    best_selling_products_per_year = product_sales.loc[product_sales.groupby('year')['sales_count'].idxmax()]

    # Pivot to visualize product sales trends per year
    product_sales_pivot = product_sales.pivot_table(index='product_category_name', columns='year', values='sales_count', fill_value=0)

    # Calculate percentage change (trend) year-over-year
    product_sales_pivot['trend'] = product_sales_pivot.pct_change(axis=1).mean(axis=1)
    
    increasing_trend = product_sales_pivot[product_sales_pivot['trend'] > 0]
    declining_trend = product_sales_pivot[product_sales_pivot['trend'] < 0]
    
    return best_selling_products_per_year, increasing_trend, declining_trend

# Function to group customers into spending tiers
def group_customers_by_spending(order_items, order_payments, orders):
    # Merge order items with payments and orders data
    order_items_payments = pd.merge(order_items, order_payments, on='order_id')
    order_items_payments_orders = pd.merge(order_items_payments, orders[['order_id', 'customer_id']], on='order_id')
    
    # Calculate total spending per customer
    customer_spending = order_items_payments_orders.groupby('customer_id')['payment_value'].sum().reset_index()
    customer_spending.rename(columns={'payment_value': 'total_spending'}, inplace=True)

    # Define spending tiers based on quantiles
    customer_spending['spending_tier'] = pd.qcut(customer_spending['total_spending'],
                                                q=[0, 0.33, 0.66, 1.0],
                                                labels=['Low Spenders', 'Medium Spenders', 'High Spenders'])

    # Summary statistics for each tier
    spending_summary = customer_spending.groupby('spending_tier').agg({
        'total_spending': ['mean', 'min', 'max', 'sum', 'count']
    }).reset_index()

    return customer_spending, spending_summary

# Function to find geographical location with most orders
def get_top_geographical_location(orders, geolocation, customers):
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])

    # Merge orders and customers
    orders_customers = pd.merge(orders, customers, on='customer_id')

    # Merge with geolocation using zip code prefix
    orders_geo = pd.merge(orders_customers, geolocation, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix')

    # Group by city and state to count the number of orders
    orders_by_geo = orders_geo.groupby(['geolocation_city', 'geolocation_state', 'geolocation_lat', 'geolocation_lng']).size().reset_index(name='order_count')

    # Sort by the number of orders to find the top locations
    top_locations = orders_by_geo.sort_values(by='order_count', ascending=False).head(10)
    
    return top_locations