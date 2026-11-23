# CloudMart: End-to-End AWS Lakehouse & GenAI Data Engineering Project

## 1. Project Overview & Business Value
**CloudMart** is a production-grade Modern Data Lakehouse pipeline designed to solve two core enterprise problems:
1. **Unmodeled, Multi-source Ingestion Bottlenecks:** Disconnected order and customer data causing slow analytics and inconsistent business metrics.
2. **Ad-hoc BI Delays:** Non-technical executives waiting days for data teams to write complex SQL queries.

This project implements the **Medallion Architecture (Bronze $\rightarrow$ Silver $\rightarrow$ Gold)** on the AWS Data ecosystem and augments it with **Amazon Bedrock (GenAI)** for self-service natural language analytics.

---

## 2. Architecture & Medallion Design

```
[Raw Sources: REST API / Events]
           │
           ▼
[Bronze Layer (Raw Storage)]
 • Raw JSON/CSV landed on S3
 • Unmodified audit history
           │
           ▼
[Silver Layer (Enriched & Validated)]
 • Schema enforcement & type casting
 • Deduplication using Window Functions
 • Stored as Parquet partitioned by date
           │
           ▼
[Gold Layer (Dimensional Star Schema)]
 • fact_orders (Transactional Fact)
 • dim_product (Conformed Dimension)
 • dim_customer (SCD Type 2 tracking)
           │
     ┌─────┴──────────────┐
     ▼                    ▼
[Amazon Athena]    [Amazon Bedrock (GenAI)]
 • Serverless SQL   • Text-to-SQL Copilot
 • Window Analytics • Narrative Business Insights
```

---

## 3. Project Directory Structure
```text
HCL-Cap01/
├── data/
│   ├── raw/                 # Bronze Layer: Ingested raw JSON feeds
│   ├── silver/              # Silver Layer: Cleaned Parquet tables
│   └── gold/                # Gold Layer: Star schema Parquet tables
├── docs/                    # Architecture diagrams and interview notes
├── sql/
│   └── analytical_queries.sql # Athena/Redshift DDL & Window Function queries
├── src/
│   ├── data_generator.py    # Generates realistic mock e-commerce stream
│   ├── pipeline_etl.py      # Bronze -> Silver -> Gold transformation engine
│   └── genai_copilot.py     # Bedrock/LLM Text-to-SQL & Insights engine
└── README.md                # Project documentation
```

---

## 4. How to Run the Project Locally
In your terminal, navigate to `c:\Users\yekka\Desktop\HCL-Cap01`:

1. **Generate Mock Source Data:**
   ```powershell
   python src/data_generator.py
   ```
2. **Execute Medallion ETL Pipeline:**
   ```powershell
   python src/pipeline_etl.py
   ```
3. **Run GenAI Data Copilot:**
   ```powershell
   python src/genai_copilot.py
   ```

---

## 5. 60-Second Interview Pitch (How to Speak About This)
> *"For my capstone, I engineered an end-to-end e-commerce Lakehouse pipeline called **CloudMart** targeting the AWS ecosystem. I ingested raw event streams into S3 (Bronze), applied schema enforcement, deduplication, and data quality checks using PySpark to produce a partitioned Parquet Silver layer. From there, I modeled a Star Schema in the Gold layer with transactional facts and SCD-ready customer and product dimensions. Finally, I connected Amazon Athena and integrated **Amazon Bedrock** to build a GenAI Text-to-SQL copilot that allows business stakeholders to ask questions in plain English and receive instant, validated SQL queries and executive insights."*
