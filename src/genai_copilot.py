"""
GenAI Copilot for Data Engineering: Amazon Bedrock Text-to-SQL & Automated Insights
Translates natural language questions to ANSI SQL against CloudMart Gold tables,
and generates narrative business insights.
"""

import json
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BedrockAssistant")

CATALOG_CONTEXT = """
Schema: cloudmart_analytics
Tables:
- fact_orders(order_id STRING, customer_key BIGINT, product_key BIGINT, order_date DATE, quantity INT, subtotal DOUBLE, tax DOUBLE, total_amount DOUBLE, status STRING, payment_method STRING)
- dim_product(product_key BIGINT, product_id STRING, product_name STRING, product_category STRING, unit_price DOUBLE)
- dim_customer(customer_key BIGINT, customer_id STRING, name STRING, city STRING, state STRING, email STRING, effective_start_date DATE, effective_end_date DATE, is_current BOOLEAN)
"""

def ask_data_copilot(user_query: str):
    """
    Simulates or calls Amazon Bedrock Anthropic Claude model.
    Includes fallbacks for testing offline without live AWS credentials.
    """
    logger.info(f"Received question: {user_query}")
    
    # Try AWS Bedrock Runtime if credentials exist, otherwise provide deterministic mock response
    try:
        import boto3
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        prompt = f"""
        Human: You are a Cloud Data Engineer. Given this AWS Athena schema:
        {CATALOG_CONTEXT}
        
        Convert this user query into an efficient ANSI SQL query and provide a brief executive insight:
        Question: "{user_query}"
        
        Respond ONLY in JSON format:
        {{
            "generated_sql": "<sql_string>",
            "explanation": "<short_business_explanation>"
        }}
        Assistant:
        """
        payload = {
            "prompt": prompt,
            "max_tokens_to_sample": 500,
            "temperature": 0.0
        }
        response = bedrock.invoke_model(
            modelId="anthropic.claude-v2",
            body=json.dumps(payload)
        )
        return json.loads(response["body"].read().decode())
    except Exception as e:
        logger.warning(f"AWS Bedrock client not connected ({e}). Providing pre-computed AI analysis response...")
        return {
            "user_query": user_query,
            "generated_sql": """
SELECT 
    p.product_category,
    COUNT(f.order_id) AS total_orders,
    ROUND(SUM(f.total_amount), 2) AS total_revenue
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
WHERE f.status IN ('COMPLETED', 'SHIPPED')
GROUP BY p.product_category
ORDER BY total_revenue DESC;
            """.strip(),
            "business_insight": "Aggregates fulfilled sales volume and revenue by category, enabling leadership to quickly identify core revenue drivers."
        }

if __name__ == "__main__":
    sample_question = "What are our top revenue-generating product categories for completed orders?"
    result = ask_data_copilot(sample_question)
    print("\n" + "="*50)
    print("GEN-AI DATA ASSISTANT OUTPUT")
    print("="*50)
    print(json.dumps(result, indent=2))
