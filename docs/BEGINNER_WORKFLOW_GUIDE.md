# CloudMart Data Lakehouse: Beginner's Complete Guide & Workflow

Welcome! If you are new to Data Engineering, modern architectures like "Lakehouse", "Medallion Design", and "Star Schema" can sound intimidating. 

This guide breaks down **CloudMart** into plain English using real-world analogies, step-by-step visuals, and a clear daily mental model.

---

## 💡 The Real-World Story: What are we building?

Imagine you own a supermarket chain called **CloudMart**. 
- Every second, customers are buying items online and in-store.
- The cash registers dump messy, unstructured receipt slips (JSON files) into a storage room.
- Some slips have typos, some are duplicates, and prices don't have tax calculated yet.
- The CEO walks in and asks: *"Which product category made the most profit in California last month?"*

If you try to read through millions of messy paper slips directly, it will take hours, cost a fortune, and probably give wrong answers.

**Your job as a Data Engineer:** Build an automated pipeline that takes messy raw receipts, cleans them, organizes them into neat tables, and attaches an AI assistant that can answer the CEO's questions in seconds.

---

## 🏗️ The 4-Stage Project Workflow

We use the industry standard **Medallion Architecture**, which refines data through 3 stages (Bronze $\rightarrow$ Silver $\rightarrow$ Gold), ending with an **AI Serving Layer**:

```
[Stage 1: Bronze (Raw)]
   │  • Messy JSON receipts from website/app
   │  • Kept untouched for auditing
   ▼
[Stage 2: Silver (Cleaned)]
   │  • Remove duplicates, fix corrupt data
   │  • Convert dates & numbers
   │  • Saved as high-speed Parquet files
   ▼
[Stage 3: Gold (Modeled)]
   │  • Split into Facts (Numbers/Sales) & Dimensions (Who/What)
   │  • Add Surrogate Keys & SCD-2 for address changes
   ▼
[Stage 4: Serving & GenAI]
      • Amazon Athena queries the Gold tables
      • Amazon Bedrock AI turns plain English questions into SQL
```

---

## 🔍 Step-by-Step Breakdown for Beginners

### Stage 1: Ingestion $\rightarrow$ The "Bronze" Layer (Raw Data)
* **What is it?** This is the "landing dock." Whatever the source app produces, we store it here as-is, untouched.
* **Why not clean it immediately?** If your cleaning code has a bug, you can always re-read the original raw files without losing data.
* **Our Project File:** `src/data_generator.py`
* **What it does:** Creates `orders_raw.json` and `customers_raw.json` inside `data/raw/`.

---

### Stage 2: Refinement $\rightarrow$ The "Silver" Layer (Cleaned Data)
* **What is it?** Think of this as the water filtration plant. We take murky lake water and filter out the mud and bacteria.
* **Key Tasks Done Here:**
  1. **Schema Validation:** Ensure `order_id` is never blank (`DROP NULL`).
  2. **Type Casting:** Convert string timestamps (`"2026-10-01 09:30:00"`) into real DateTime objects, and amounts into decimals.
  3. **Deduplication:** If an order was sent twice due to network lag, keep only the latest one using Window Functions (`ROW_NUMBER()`).
  4. **Format Conversion:** Convert JSON to **Apache Parquet**. Parquet is columnar, compressed, and 10x faster to query in AWS Athena.
* **Our Project File:** The `run_bronze_to_silver()` function in `src/pipeline_etl.py`.

---

### Stage 3: Structuring $\rightarrow$ The "Gold" Layer (Star Schema)
* **What is it?** Business-ready data modeled for high-speed reporting. We split the data into **Facts** and **Dimensions** (The Star Schema):
  - **Fact Table (`fact_orders`):** Contains numbers and events. (e.g., `quantity`, `subtotal`, `tax`, `total_amount`).
  - **Dimension Tables (`dim_product`, `dim_customer`):** Contains context. Who bought it? What was the item? What category?
* **Surrogate Keys:** Instead of natural strings like `"PROD01"`, we generate clean integer keys like `1001`. Integers join 5x faster in databases.
* **SCD Type 2 (Slowly Changing Dimensions):** We include `effective_start_date`, `effective_end_date`, and `is_current` flags so if a customer moves from Seattle to Austin, historical orders still reflect Seattle, while future ones reflect Austin!
* **Our Project File:** The `run_silver_to_gold()` function in `src/pipeline_etl.py`.

---

### Stage 4: Analytics & GenAI $\rightarrow$ The "Brain" Layer
* **What is it?** Enabling self-service analytics so non-technical users can interact with the warehouse.
* **How it works:**
  1. We feed the schema of our Gold tables to an LLM on **Amazon Bedrock**.
  2. The user types a question in plain English: *"What are our top revenue categories?"*
  3. The LLM translates it to accurate ANSI SQL with window functions.
  4. The query runs on **Amazon Athena** against the Parquet files in S3.
  5. The LLM summarizes the output into an executive takeaway.
* **Our Project File:** `src/genai_copilot.py`.

---

## 🏃 How to Run and Test This Yourself (In 3 Minutes)

Open PowerShell, navigate to your project, and run these three commands:

```powershell
cd C:\Users\yekka\Desktop\HCL-Cap01

# Step 1: Create raw mock data
python src/data_generator.py

# Step 2: Run Bronze -> Silver -> Gold ETL
python src/pipeline_etl.py

# Step 3: Test the GenAI Assistant
python src/genai_copilot.py
```

---

## 💬 How to Explain This in an Interview (Simple Script)

> *"In this project, I built an e-commerce Lakehouse pipeline using the **Medallion Architecture**.*
>
> *1. **Ingestion (Bronze):** I ingest raw JSON order feeds into an S3 raw landing zone.*
> *2. **Cleansing (Silver):** I use a transformation pipeline to enforce schemas, cast types, remove duplicates via window ranking, and store clean data in Parquet format.*
> *3. **Modeling (Gold):** I design a Star Schema containing a transactional fact table (`fact_orders`) and conformed dimension tables (`dim_customer`, `dim_product`) equipped with surrogate keys and SCD Type 2 tracking.*
> *4. **Serving & GenAI:** Finally, I configured Amazon Athena for serverless querying and built a Text-to-SQL copilot using Amazon Bedrock, allowing business users to ask ad-hoc questions in natural language and receive instant SQL queries and executive insights."*
