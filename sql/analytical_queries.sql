-- CloudMart Analytical Data Warehouse (Amazon Athena & Redshift Compatible)
-- DDL and Analytical Window Function Queries

-- 1. Dimension Tables
CREATE EXTERNAL TABLE IF NOT EXISTS dim_product (
    product_key BIGINT,
    product_id STRING,
    product_name STRING,
    product_category STRING,
    unit_price DOUBLE
)
STORED AS PARQUET
LOCATION 's3://cloudmart-data-lakehouse/gold/dim_product/';

CREATE EXTERNAL TABLE IF NOT EXISTS dim_customer (
    customer_key BIGINT,
    customer_id STRING,
    name STRING,
    city STRING,
    state STRING,
    email STRING,
    effective_start_date DATE,
    effective_end_date DATE,
    is_current BOOLEAN
)
STORED AS PARQUET
LOCATION 's3://cloudmart-data-lakehouse/gold/dim_customer/';

-- 2. Transactional Fact Table
CREATE EXTERNAL TABLE IF NOT EXISTS fact_orders (
    order_id STRING,
    customer_key BIGINT,
    product_key BIGINT,
    order_date DATE,
    quantity INT,
    subtotal DOUBLE,
    tax DOUBLE,
    total_amount DOUBLE,
    status STRING,
    payment_method STRING
)
PARTITIONED BY (order_date STRING)
STORED AS PARQUET
LOCATION 's3://cloudmart-data-lakehouse/gold/fact_orders/';

-- =========================================================================
-- HIGH-YIELD ANALYTICAL QUERIES (WINDOW FUNCTIONS & CTEs)
-- =========================================================================

-- Q1: Top 2 best-selling products per category using DENSE_RANK()
WITH category_sales AS (
    SELECT 
        p.product_category,
        p.product_name,
        SUM(f.total_amount) AS revenue,
        DENSE_RANK() OVER (PARTITION BY p.product_category ORDER BY SUM(f.total_amount) DESC) as category_rank
    FROM fact_orders f
    JOIN dim_product p ON f.product_key = p.product_key
    WHERE f.status IN ('COMPLETED', 'SHIPPED')
    GROUP BY p.product_category, p.product_name
)
SELECT * FROM category_sales WHERE category_rank <= 2;

-- Q2: Customer purchasing trend using LAG() to calculate time between purchases
WITH order_sequence AS (
    SELECT 
        c.customer_id,
        c.name,
        f.order_id,
        f.order_date,
        f.total_amount,
        LAG(f.order_date, 1) OVER (PARTITION BY c.customer_id ORDER BY f.order_date) AS previous_order_date
    FROM fact_orders f
    JOIN dim_customer c ON f.customer_key = c.customer_key
)
SELECT 
    customer_id,
    name,
    order_id,
    order_date,
    previous_order_date,
    DATE_DIFF('day', previous_order_date, order_date) AS days_between_orders
FROM order_sequence;
