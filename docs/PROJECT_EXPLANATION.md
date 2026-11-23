# CloudMart Project: Clear & Direct Technical Explanation

## 1. What is this project in one sentence?
An automated data pipeline that takes raw customer orders and product files, cleans and organizes them into a database format designed for business reporting, and adds an AI that writes SQL queries when asked questions in plain English.

---

## 2. Why do we need this pipeline? (The Problem & Solution)

| The Problem (Raw Data) | The Solution (This Pipeline) |
| :--- | :--- |
| Data comes in as messy JSON files from apps. | Reads and standardizes all files automatically. |
| Duplicate orders exist due to network retries. | Removes duplicates and keeps only the latest status. |
| Dates and numbers are stored as text strings. | Converts text into actual numbers and date types. |
| Customer details and order numbers are mixed together. | Separates them into clean **Orders**, **Customers**, and **Products** tables. |
| Business managers don't know SQL to ask questions. | An AI converts questions like *"Which category sold the most?"* into SQL. |

---

## 3. The 3-Step Workflow

```
[STEP 1: GET DATA]          -->  [STEP 2: CLEAN & ORGANIZE]     -->  [STEP 3: ANALYZE & AI]
Orders & Customers Files         Clean errors, remove dupes,          Run SQL queries &
(Raw JSON format)                split into 3 structured tables       AI writes queries from text
```

### Step 1: Ingest Data (`src/data_generator.py`)
- Simulates an e-commerce website generating purchases.
- Creates two files:
  - `orders_raw.json` (Order ID, product bought, price, date, payment method)
  - `customers_raw.json` (Customer ID, name, city, state, email)

### Step 2: Clean and Structure (`src/pipeline_etl.py`)
This is where the main work happens. The script does two things:
1. **Cleaning:**
   - Drops rows with missing IDs.
   - Converts dates from text (`"2026-10-01"`) to real dates.
   - Calculates total price (`subtotal + tax`).
   - Removes duplicate orders using order timestamps.
2. **Structuring (Separating into Tables):**
   Instead of keeping everything in one giant messy file, it splits the data into 3 neat tables:
   - **`fact_orders` Table:** The transaction numbers (Order ID, Customer Key, Product Key, Quantity, Total Amount).
   - **`dim_customer` Table:** Who bought it (Customer Name, City, State, and tracking for address changes).
   - **`dim_product` Table:** What was bought (Product Name, Category, Unit Price).

### Step 3: Analytics & GenAI (`src/genai_copilot.py` & `sql/analytical_queries.sql`)
1. **Analytical SQL:**
   - Queries calculate high-value metrics like *top-selling products per category* using SQL window functions (`DENSE_RANK()`, `LAG()`).
2. **GenAI Assistant:**
   - A business user asks: *"What are our top revenue-generating product categories?"*
   - The AI checks the database schema, automatically writes the SQL query, and explains the answer in simple English.

---

## 4. How the Files in your Folder Map to this Workflow

```text
HCL-Cap01/
├── src/
│   ├── data_generator.py   --> Step 1: Generates the raw order & customer files
│   ├── pipeline_etl.py     --> Step 2: Cleans errors, deduplicates, and splits into tables
│   └── genai_copilot.py    --> Step 3: AI assistant that turns English into SQL
│
├── sql/
│   └── analytical_queries.sql --> Ready-made SQL queries for business reports
│
└── data/
    ├── raw/    --> Where the initial messy JSON files sit
    ├── silver/ --> Where the cleaned intermediate files sit
    └── gold/   --> Where the final structured tables (Orders, Customers, Products) sit
```

---

## 5. How to Explain this Project in an Interview (Simple & Direct)

> *"I built an end-to-end data pipeline for an e-commerce platform called CloudMart.*
>
> *First, it takes raw JSON orders and customer data from source applications.*
> 
> *Second, using Python and SQL concepts, the pipeline cleans the data—removing duplicate orders, fixing missing values, and formatting dates. It then organizes the data into a standard analytical model: an orders table for transaction amounts, linked to customer and product tables for business context.*
> 
> *Third, I built analytical SQL queries using window functions for business reporting, and integrated an AI model using AWS Bedrock that allows non-technical managers to ask questions in plain English and automatically receive the correct SQL query and business insights."*
