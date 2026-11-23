"""
CloudMart Lakehouse ETL Engine:
Executes Bronze -> Silver (cleansing, deduplication, schema enforcement)
and Silver -> Gold (Dimensional Modeling: Fact and Dimensions with Surrogate Keys).
Uses pandas/PySpark compatible transformation logic ready for AWS Glue.
"""

import os
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ETL_Pipeline")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
SILVER_DIR = os.path.join(BASE_DIR, "data", "silver")
GOLD_DIR = os.path.join(BASE_DIR, "data", "gold")

def run_bronze_to_silver():
    """Reads raw JSON from Bronze, enforces schema, cleans, and saves to Silver."""
    logger.info("Starting Bronze -> Silver transformation...")
    os.makedirs(SILVER_DIR, exist_ok=True)
    
    orders_path = os.path.join(RAW_DIR, "orders_raw.json")
    with open(orders_path, "r") as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    
    # Data Quality: drop null IDs, parse dates, deduplicate
    df = df.dropna(subset=["order_id", "customer_id", "product_id"])
    df["order_timestamp"] = pd.to_datetime(df["order_timestamp"])
    df["order_date"] = df["order_timestamp"].dt.date
    df["subtotal"] = df["subtotal"].astype(float)
    df["tax"] = df["tax"].astype(float)
    df["total_amount"] = (df["subtotal"] + df["tax"]).round(2)
    
    # Deduplicate keeping most recent timestamp
    df = df.sort_values("order_timestamp").drop_duplicates(subset=["order_id"], keep="last")
    
    silver_orders_path = os.path.join(SILVER_DIR, "orders_cleaned.parquet")
    df.to_parquet(silver_orders_path, index=False)
    logger.info(f"Silver Orders written to: {silver_orders_path} (Records: {len(df)})")
    return df

def run_silver_to_gold(df_orders):
    """Transforms cleaned Silver data into a Star Schema (Fact + Dimension tables)."""
    logger.info("Starting Silver -> Gold Dimensional Modeling...")
    os.makedirs(GOLD_DIR, exist_ok=True)
    
    # 1. Dimension: dim_product
    dim_product = df_orders[["product_id", "product_name", "product_category", "unit_price"]].drop_duplicates(subset=["product_id"]).copy()
    dim_product.reset_index(drop=True, inplace=True)
    dim_product["product_key"] = dim_product.index + 1001  # Surrogate Key
    dim_product.to_parquet(os.path.join(GOLD_DIR, "dim_product.parquet"), index=False)
    logger.info(f"Gold dim_product generated with {len(dim_product)} rows.")
    
    # 2. Dimension: dim_customer (Demonstrates SCD Type 2 foundation)
    customers_path = os.path.join(RAW_DIR, "customers_raw.json")
    with open(customers_path, "r") as f:
        cust_data = json.load(f)
    dim_customer = pd.DataFrame(cust_data)
    dim_customer.reset_index(drop=True, inplace=True)
    dim_customer["customer_key"] = dim_customer.index + 5001  # Surrogate Key
    dim_customer["effective_start_date"] = "2026-01-01"
    dim_customer["effective_end_date"] = "9999-12-31"
    dim_customer["is_current"] = True
    dim_customer.to_parquet(os.path.join(GOLD_DIR, "dim_customer.parquet"), index=False)
    logger.info(f"Gold dim_customer generated with {len(dim_customer)} rows.")

    # 3. Fact: fact_orders
    merged = df_orders.merge(dim_product[["product_id", "product_key"]], on="product_id", how="inner")
    merged = merged.merge(dim_customer[["customer_id", "customer_key"]], on="customer_id", how="inner")
    
    fact_orders = merged[[
        "order_id",
        "customer_key",
        "product_key",
        "order_date",
        "quantity",
        "subtotal",
        "tax",
        "total_amount",
        "status",
        "payment_method"
    ]].copy()
    
    fact_orders.to_parquet(os.path.join(GOLD_DIR, "fact_orders.parquet"), index=False)
    logger.info(f"Gold fact_orders generated with {len(fact_orders)} rows.")

if __name__ == "__main__":
    df_clean = run_bronze_to_silver()
    run_silver_to_gold(df_clean)
    print("\nETL Pipeline Execution Complete! Bronze -> Silver -> Gold created successfully.")
