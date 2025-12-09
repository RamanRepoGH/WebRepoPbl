# Game Event Tracking Pipeline

This project provides the skeleton for an event-driven data pipeline to track mobile game player behavior (installs and purchases).

## 1. Architectural Approach

Here is the data flow that has been assumed for sending the raw events with minimal schema validation to Snowflake Staging Table. This can ensure that we don't do a lot of processing at client side and capture almost all the events in our staging layer. This will ensure that the following overall flow is lightweight. 

Game SDK → API → Firehose → Snowpipe Streaming/S3 → Snowflake Staging Table (raw_events)

The business validations can be performed then in the snowflake and the different table can be created for rejected records. Here is the overall flow that can be implemented in Snowflake. 

Snowflake Staging Table (raw_events) → Snowflake Stream → Snowflake Task → Final Analytics Tables (events, purchases, etc.)

## 2. Other Design Decisions

| Component | Technology/Method                 | Rationale                                                                                                                                                            |
|---|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Frontend/SDK** | Python `dataclasses` & `requests` | Uses Python standard library features for clear data structure definition and simple HTTP communication. Focuses on immutability and easy JSON serialization.        |
| **Backend API** | FastAPI + Pydantic                | Provides automatic data validation (ensuring schema consistency), serialization, and built-in OpenAPI documentation, which are essential for a reliable API gateway. |
| **Backend Integration**| Amazon Data Firehose              | A simple put_record has been used to ingest data in Amazon Data (Kinesis) Firehose.                                                                                  
| **Authentication** | IAM Roles (Planned)               | The API should use an AWS IAM Role with minimal permissions (`firehose:PutRecordBatch`) to prevent credential leaks. This part is not handled in the code.           |
| **Communication** | `202 Accepted`                    | The API returns 202 because forwarding to Firehose is an asynchronous process. This prevents the client from blocking while the API attempts to connect to AWS.      |

## 3. Assumptions Made

1.  **Transport Layer:** All communication is secured using HTTPS (implied by API gateway setup, not shown in code).
2.  **Amazon Data Firehose:** Kinesis Firehose is configured to deliver data to Snowflake and is responsible for eventual delivery (high reliability).
4.  **Currency Data:** All purchase amounts are provided in the local currency of the transaction.

## 4. Snowflake Table Design (Handling Multiple Currencies)
    
1. Data can flow from Amazon data firehose into the following staging table:

    CREATE TABLE raw_events (
            ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw VARIANT
        );
2. Use streams for chage data capture, create intermediate tables e.g. using the below query: 

    SELECT
        raw:event_id::string,
        raw:event_type::string,
        raw:timestamp::timestamp,
        raw:user_id::string,
        raw:product_id::string,
        raw:currency::string,
        raw:amount::float,
        ingestion_time
    FROM raw_events_stream
    WHERE raw:event_type::string = 'purchase';
3. Perform the necessary business validations and route the final data and error records into fct tables
4. For managing the Forex rates, a separate table can be populated directly using lamda functions (or any other means) in Snowflake which can record the hourly forex rates for all the intended currencies. 
5. The final table for purchases may look like the following:
    CREATE TABLE fact_purchases (
    event_id STRING PRIMARY KEY,
    purchase_time TIMESTAMP,
    user_id STRING,
    product_id STRING,
    currency STRING,
    amount FLOAT,
    amount_usd FLOAT,
    fx_rate FLOAT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

## 5. Next Steps (Production Readiness)

To make this pipeline production-ready, I would implement the following:

1.  **API Scaling and Security:**
    * Deploy the FastAPI application behind an **API Gateway** (for throttling, WAF, and DDoS protection) and run it on a managed service (e.g., **AWS ECS/EKS ) for scalability.
3.  **Dead Letter Queue (DLQ) Integration:**
    * Implement an AWS Lambda function or a separate process to monitor Firehose's failed record delivery to the S3 bucket. This ensures failed records are inspected, fixed, and re-submitted (or permanently archived).
4.  **Batch based ingestion in firehose**
    * the data should be ingested in firehose in batches of events along with retries and error handling
4.  **Monitoring and Alerting:**
    * Set up CloudWatch/Prometheus metrics for the API (latency, error rates, throughput) and Firehose (delivery success rate, record count) with automatic alerting on anomalies.
5.  **Business validations in the Snowflake:**
    * Implement the business validations in Snowflake and move the data to final tables. 