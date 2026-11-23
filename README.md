# CloudMart: End-to-End AWS Lakehouse & GenAI Data Engineering Project

## 1. Project Overview & Business Problem
**CloudMart** is an enterprise data lakehouse pipeline developed to solve common operational and analytics challenges in digital commerce:
- **Disjointed Event Ingestion:** Raw clickstreams and transactional orders arrive in semi-structured JSON with variable schemas, missing records, and duplicate payloads from network retries.
- **Reporting Inefficiencies:** Analytical queries executed directly on flat raw logs suffer from slow full-table scans, high cloud compute costs, and inconsistent metrics across teams.
- **The Self-Service Bottleneck:** Business stakeholders and executives require rapid ad-hoc insights but lack SQL proficiency, creating constant engineering request backlogs.

This pipeline automates ingestion, data hygiene, dimensional star schema modeling, date-partitioned columnar storage, and an integrated LLM-based Text-to-SQL copilot for self-service business reporting.

---

## 2. End-to-End Architectural Flow

```
[Raw Sources: REST API / Events]
           │
           ▼
[Bronze Layer (Raw Landing)]
 • Unaltered JSON and CSV data landed into storage
 • Preserves raw payloads for audit and reprocessing
           │
           ▼
[Silver Layer (Data Quality & Cleansing)]
 • Schema enforcement, null filtering, data type casting
 • Deduplication using SQL window ranking (ROW_NUMBER over order_id)
 • Conversion from JSON to compressed, columnar Apache Parquet
           │
           ▼
[Gold Layer (Dimensional Star Schema)]
 • fact_orders (Transactional Fact table with financial measures)
 • dim_product (Conformed Dimension with surrogate keys)
 • dim_customer (SCD Type 2 tracking for geographic/attribute changes)
           │
     ┌─────┴──────────────┐
     ▼                    ▼
[Amazon Athena]    [Amazon Bedrock (GenAI)]
 • Serverless SQL   • Text-to-SQL Semantic Layer
 • Window Analytics • Automated Executive Insights
```

---

## 3. Deep-Dive Engineering Implementation

### A. Data Cleansing & Deduplication Strategy
- **Null & Corrupt Record Handling:** Incoming payloads without critical identifiers (`order_id`, `customer_id`, `product_id`) are isolated and discarded during the initial validation pass.
- **Window-Based Deduplication:** E-commerce systems frequently encounter duplicate network hits. The pipeline applies a window function partitioned by `order_id` and ordered by `order_timestamp DESC`. Selecting only `row_number = 1` guarantees that only the latest state of each transaction reaches downstream tables without losing unique orders.
- **Type Coercion & Schema Standardization:** Dates are parsed from ISO text strings into native `DATE` and `TIMESTAMP` formats. Currency and tax attributes are strictly cast to floating-point and double types to avoid downstream aggregation arithmetic errors.

### B. Dimensional Modeling & Warehouse Schema
- **Star Schema Design:** The modeling layer separates transactional metrics from entity attributes to minimize multi-table join overhead during analytical queries:
  - **`fact_orders`:** Holds additive measures including `quantity`, `subtotal`, `tax`, and `total_amount`, indexed by foreign surrogate keys.
  - **`dim_product`:** Stores product metadata (`product_name`, `product_category`, `unit_price`) mapped to unique surrogate keys (`product_key`).
  - **`dim_customer`:** Implements **Slowly Changing Dimensions (SCD Type 2)** using `effective_start_date`, `effective_end_date`, and `is_current` flags. This ensures historical revenue remains tied to a customer's location at the time of purchase even if their profile updates later.
- **Surrogate Keys vs. Natural Keys:** Business keys (e.g., alphanumeric strings like `PROD-01`) are swapped for dense integer surrogate keys (`1001`, `1002`). This speeds up database hash joins and protects analytics tables from upstream operational ID changes.

### C. Storage Optimization & Query Performance
- **Apache Parquet Storage:** Migrating from flat JSON to Parquet enables snappy columnar compression, reducing physical disk utilization by up to 70%.
- **Partition Pruning:** Fact tables are physically partitioned on `order_date`. Analytical engines like Amazon Athena skip non-relevant date folders during query execution, minimizing both query runtime and data scan expenses ($5 per TB scanned).

### D. GenAI Text-to-SQL Integration (Amazon Bedrock)
- **Zero-Data Leakage Architecture:** To protect customer confidentiality, raw record data is never sent to the LLM. Only table DDL schemas, column names, and data types are injected into the prompt context.
- **Semantic Translation:** The model translates natural language business questions (e.g., *"Which product category drove the highest sales this month?"*) into ANSI SQL queries optimized for Amazon Athena.
- **Automated Synthesis:** Beyond returning the executable SQL query, the copilot provides an executive business explanation of what the metric signifies, making data directly actionable for non-technical leadership.

---

## 4. Analytical Capabilities & Query Patterns
The warehouse contains pre-built analytical queries showcasing advanced SQL techniques:
- **Rankings:** `DENSE_RANK()` over product categories to identify top-tier performers without skipping rank numbers on ties.
- **Time-Series Analysis:** `LAG()` functions over customer order sequences to calculate customer purchase frequency and average days between transactions.
- **Conditional Aggregations:** CTEs and `CASE` statements to separate gross, net, and canceled transaction volumes in a single execution scan.

---

## 5. Project Directory Structure
```text
HCL-Cap01/
├── data/
│   ├── raw/                   # Raw landing files (orders_raw.json, customers_raw.json)
│   ├── silver/                # Cleaned & deduplicated Parquet datasets
│   └── gold/                  # Star Schema tables (fact_orders, dim_product, dim_customer)
├── docs/                      # Architectural breakdowns and workflow documentation
│   ├── BEGINNER_WORKFLOW_GUIDE.md
│   └── PROJECT_EXPLANATION.md
├── sql/
│   └── analytical_queries.sql # Athena/Redshift DDL & Window Function analytical scripts
├── src/
│   ├── data_generator.py      # Simulates upstream e-commerce events and customer streams
│   ├── pipeline_etl.py        # Core ETL engine executing cleansing, validation & modeling
│   └── genai_copilot.py       # Amazon Bedrock integration for natural language Text-to-SQL
├── .gitignore
└── README.md                  # Comprehensive technical documentation
```

---

## 6. Local Setup and Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnirudhY-025/cloudmart-lakehouse.git
   cd cloudmart-lakehouse
   ```

2. **Install dependencies:**
   ```bash
   pip install pandas pyarrow fastparquet boto3
   ```

3. **Run the pipeline stages:**
   ```bash
   # Generate raw streaming data
   python src/data_generator.py

   # Run data quality, cleansing, and dimensional modeling
   python src/pipeline_etl.py

   # Run the GenAI Text-to-SQL Assistant
   python src/genai_copilot.py
   ```
