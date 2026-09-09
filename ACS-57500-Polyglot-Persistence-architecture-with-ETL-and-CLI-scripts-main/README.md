Lead Architect: Myles Edwards   

Course: ACS575 Advanced Database Systems, Spring 2026   


📌 Project Overview
This project implements a Polyglot Persistence architecture to resolve resource contention in modern e-commerce systems. Traditional architectures force mission-critical transactions (OLTP) and heavy analytical workloads (OLAP) to compete for the same CPU and I/O resources. This prototype decouples these concerns into a hybrid system, ensuring that high-velocity behavioral event streams do not impact financial data integrity.  


🏗️ System Architecture
PostgreSQL (OLTP): A strict 3NF relational schema enforcing ACID compliance for financial ledgers and inventory using the Olist dataset.  


MongoDB Atlas (OLAP): A distributed NoSQL document cluster built to absorb unstructured, high-velocity behavioral event logs from the Electronics dataset.  


Python Middleware: A custom application layer that orchestrates the ETL pipeline and merges disparate datasets in-memory to generate hybrid business intelligence.  

🚀 Technical Highlights
The Data Bridge: Successfully resolved the Primary Key Divergence problem, merging 32-character Hex UUIDs (SQL) with 18-digit Numeric IDs (NoSQL) through an application-layer positional merge.  


Integrity Enforcement: Utilized sequential orchestration in the ETL pipeline to respect strict foreign-key constraints during bulk-loading of un-sanitized CSV sources.  


Advanced Metrics: The system calculates unique hybrid metrics such as "Revenue per View," extracting insights impossible to find in a single-database silo.  

💻 Tech Stack
Languages: Python 3   

Databases: PostgreSQL (Local), MongoDB Atlas (Cloud)   

Libraries: pandas, psycopg2, pymongo   

🛠️ Setup
Clone the repository and install dependencies from requirements.txt.

Place raw Kaggle CSV datasets into a local /data directory (ignored by Git due to file size limits).

Run etl_pipeline.py to populate the databases.

Run presentation_demo.py to launch the interactive CLI.
