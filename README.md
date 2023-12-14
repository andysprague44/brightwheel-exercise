# Andy Sprague - BrightWheel take home exercise

## Requirements & Choices

### Target Database

**Requirements**
- Queriable with SQL
- For analytical workflows and data enrichment

**Choice**
I decided to use Amazon Redshift as the target. This was largely due to it being the most recent OLAP database I have worked with, so will speed up development time. It also happens to be a decent choice for analytical use-cases.

**But**, I ran out of time so used SQLite for the purpose of the exercise (the default connection for the chosen ETL approach) - obviously would switch for prod use.

### ETL solution

**Requirements**

- Extract from s3 (single bucket)
- Schema transforms / mapping
- Track lineage
- Handle deletes, updates, inserts
- Handle duplications within a source and across sources (based on primary & secondary idenfifier columns)
- Normalize data types

The following are additional requirements for long-term, so should be considered in the technology choice:
- Roll-back or recover if a job fails 1/2 way through (ACID transactions)
- Re-play jobs (idempotence)
- Observability and alerting on failed jobs
- Run on a schedule
- Ingest new source files, all from the same s3 bucket (100+ source files)
- Schemas are subject to change at any time
- 'Self-serve' support for new sources?

**Options**

I thought about the following options and their pro / cons:

A) AWS Lamdba
- Pros: Simple to implement. Low cost. Auto-scale. Trigger on s3 object creation.
- Cons: Handling schema migrations. Handling complex data transforms. Job orchestration / Observability. Testing. Execution time limits.

B) AWS Glue
- Pros: Can handle more complex transforms. Auto-scale. Catalog.
- Cons: Cost can escalate if not managed. Flexibility (e.g. merging/flagging dupes between multiple sources?).

C) dbt
- Pros: Flexible data modeling. Built in testing. Lineage.
- Cons: ELT, not ETL -> raw data stored in redshift may be expensive & focus is more on downstream modeling than intial data ingestion. Learning curve.

D) Airflow
- Pro: Open source. No black magic (transforms in python).
- Cons: Possibly cost, if using Amazon MWAA. Set-up / configuration time. It's orchestration, the rest is on you.

E) Databricks / Snowflake
- Pros: Enterprise-ready data warehouse (e.g. think data governance).
- Cons: Cost management. Learning curve. Vendor lock-in. Set-up time.

**Choice**

If I had more than 2 hours, and full flexibility, I'd probably choose Databricks. It's the market leader in data warehouses (lake houses), and has support for everything required. It would also extend to streaming use-cases in the future.

But, it might be too big a lift (and negative ROI) to move from existing setups. In this case, dbt is a good choice (for flexible data models and schema changes, handling scenarios such as flagging duplicates, and for it's extensibilty to downstream data modeling and pre-aggregations in the data warehouse).

For a 2 hour exercise, I have chosen Airflow. to be able to work locally in 'just python' and to move fast (get immediate feedback).

### Tasks

These are the set of tasks to tackle the problem:
- Set up a basic instance of airflow running locally
- Connect it to s3 source
- Connect it to redshift target [EDIT - skipped]
- End-to-end for a single source file
- Extend to all source files [EDIT - ran out of time]


## Getting started

Create conda env:
- `conda env create --force -f environment.yml -n brightwheel-andy`
- `conda activate brightwheel-andy`


Run debug config in vs-code: 
- `Airflow: brightwheel_etl_nevada`


## Next steps

I got it firing for 1 source in the alloted time. The next set of tasks would be:
- define mapping and a DAG for each source (or define a single DAG that processes all files)
- some smarter source-specific transforms, for example in Nevada, could possibly break the 'Name' field into first name / last name, extract the zip from the address field, etc. 
- would want to keep "replaced" records and mark them as 'soft' deleted (connect to redshift and use MERGE operations for this)
- add unit testing of the DAG and tasks
- split the methods in common.py into sensible separate files, e.g. common, s3_utils.py, sqlite_utils.py

## Longer term thinking

- Could look at something like TextRazor to fuzzy match columns to target columns.
- A solution to self-serve new sources (airflow requires python expertise). Could use AI to parse new sources, or an off-the-shelf solution such as [oneschema](https://www.oneschema.co)
- Handling schema changes automatically lends to either alerting when this happens, so quick updates can happen, or moving to an off-the-shelf data provider that can handle this, such as FiveTran or talend (aka stitch data)
- Observability & alerting can be handled using CloudWatch in AWS
