# REST API Data Pipeline

A small Python project demonstrating how transaction data can be exposed through a REST API, consumed by a Python client, and processed as a data pipeline.

## Purpose

The project is intended as a practical exercise in building and consuming APIs while connecting application development with data engineering workflows.

## Technologies

- Python
- FastAPI
- SQLite
- SQL
- HTTP / REST
- JSON
- Requests
- PySpark

## Project Structure

```text
rest/
│
├── transactions_fastapi.py    # FastAPI server and SQLite database
├── transaction_client.py      # Python client for consuming the API
├── .gitignore
└── README.md
```

The SQLite database is generated automatically by the FastAPI application and is not committed to the repository.

## FastAPI Server

### Starting the FastAPI Server

```powershell
uvicorn transactions_fastapi:api.app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Get Transactions for a Customer

```text
GET /customers/{customer_id}/transactions
```

Example:

```text
GET /customers/111/transactions
```

### Get Transactions with Pagination

The API supports cursor-based pagination using the transaction ID.

Example:

```text
GET /transactions?after_id=0&limit=2
```

Returns transactions with IDs 1 and 2.

The next request can use the last returned transaction ID as the cursor:

```text
GET /transactions?after_id=2&limit=2
```

Returns transactions with IDs 3 and 4.

This allows the client to retrieve large datasets in smaller pages rather than requesting every record in a single response.

## Python Client

`transaction_client.py` consumes the REST API using the `requests` library.

The client has two levels of retrieval:

```python
get_transactions()
```

Retrieves a single page of transactions.

```python
get_all_transactions()
```

Automatically follows the pagination cursor until no more records are returned.

### Starting the Client

In a separate terminal:

```powershell
python transaction_client.py
```

### Data Processing

The retrieved JSON data is represented in Python as a list of dictionaries.

The next stage of the project will convert this data into a PySpark DataFrame for processing and analysis.

## Architecture

```text
SQLite
   ↓
FastAPI REST API
   ↓
JSON over HTTP
   ↓
Python client
   ↓
Cursor-based pagination
   ↓
PySpark
   ↓
Data processing and analysis
```

## Current Features

- SQLite transaction database
- FastAPI REST API
- HTTP GET endpoints
- Path parameters
- Query parameters
- Input validation
- HTTP error responses
- Cursor-based pagination
- Python API client
- Automatic retrieval of multiple API pages
- JSON-to-Python data conversion

## Planned Features

- PySpark DataFrame processing
- Data transformations and aggregations
- Additional API operations
- POST endpoint for creating transactions
- Larger test dataset
- Further analysis of the retrieved transaction data
  