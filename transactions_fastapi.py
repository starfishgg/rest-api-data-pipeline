"""
fastapi.py

A small FastAPI API that retrieves customer transactions
from a SQLite database.
"""

import sqlite3
import uvicorn

from fastapi import FastAPI, HTTPException, Response




class TransactionAPI:

    def __init__(self) -> None:
        # Create the FastAPI application
        self.app: FastAPI = FastAPI()

        # SQLite database file used by the application.
        self.database: str = "transactions.db"

        # Prepare the database and register the API routes.
        self.create_database()
        self.setup_routes()



    def create_database(self) -> None:
        """
        Create the transactions table and add test data.
        """

        # Open a connection to the SQLite database
        connection: sqlite3.Connection = sqlite3.connect(self.database)

        # Create the table if it does not already exist.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_time TEXT NOT NULL
            )
        """)

        # Insert some test transactions
        #
        # INSERT OR IGNORE prevents duplicate primary-key errors
        # if the application is started more than once.
        connection.executemany("""
            INSERT OR IGNORE INTO transactions (
                transaction_id,
                customer_id,
                amount,
                transaction_time
            )
            VALUES (?, ?, ?, ?)
        """, [
            (1, 111, 11.00, "2026-09-20 10:15:00"),
            (2, 222, 22.00, "2026-09-20 11:30:00"),
            (3, 111, 35.50, "2026-09-21 09:20:00"),
            (4, 111, 18.75, "2026-09-22 14:10:00"),
        ])

        #  Save the changes to the database.
        connection.commit()

        # Close the database connection
        connection.close()


    def setup_routes(self) -> None:
        """
        Register the API endpoints with FastAPI.
        """

        # Register:
        # GET /customers/<customer_id>/transactions
        #
        # FastAPI will take the customer id from the URL
        # and pass it to get_customer_transactions().
        self.app.add_api_route(
            "/customers/{customer_id}/transactions",
            self.get_customer_transactions,
            methods=["GET"]
        )

        # Register:
        # GET /transactions
        self.app.add_api_route(
            "/transactions",
            self.get_all_transactions,
            methods=["GET"]
        )

        # Get rid of annoying favicon.ico errors
        self.app.add_api_route(
            "/favicon.ico",
            self.favicon,
            methods=["GET"]
        )


    def favicon(self) -> Response:
        """
        Handle browser requests for the favicon.
        """

        return Response(status_code=204) # 204 = no content


    def get_customer_transactions(
            self,
            customer_id: int
    ):
        """"
        Return all transactions belonging to a customer.
        """

        # Reject invalid customer IDs before querying the database.
        if customer_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="customer_id must be positive"
            )

        # Open a connection to the SQLite database.
        connection: sqlite3.Connection = sqlite3.connect(
            self.database
        )

        # SQL query to retrieve this customer's transactions.
        #
        # The ? is a parameter placeholder.
        # The actual customer_id is supplied separately below.
        query: str = """
            SELECT
                transaction_id,
                amount,
                transaction_time
            FROM
                transactions
            WHERE
                customer_id = ?
            ORDER BY
                transaction_time
        """

        # Execute the query using a parameterized value.
        #
        # execute() returns a Cursor object.
        # It does NOt return the actual rows yet.
        cursor: sqlite3.Cursor = connection.execute(
            query,
            (customer_id,)
        )

        #fetchall() retrieves all rows returned by the query.
        rows: list[tuple] = cursor.fetchall()

        # Display the query results while developing/debugging.
        print("customer_id:", customer_id)
        print("rows:", rows)

        # An empty list m eans the query found no transactions
        # for this customer.
        if not rows:
            connection.close()

            raise HTTPException(
                status_code=404,
                detail="no transactions found"
            )

        # We have finished using the database connection.
        connection.close()

        # Convert each database row into a disctionary
        #
        # Fast API will automatically convert this into JSON.
        transactions: list[dict] = [
            {
                "transaction_id": row[0],
                "amount": row[1],
                "transaction_time": row[2],
            }
            for row in rows
        ]

        return transactions


    def get_all_transactions(
            self,
            after_id: int = 0,
            limit: int = 100
    ):
        """
        Return all transactions after a specified transaction ID.
        """

        # Reject invalid starting IDs.
        if after_id < 0:
            raise HTTPException(
                status_code=400,
                detail="after_id must be 0 or greater"
            )

        # Reject invalid limits.
        if limit < 1:
            raise HTTPException(
                status_code=400,
                detail="limit must be 1 or greater"
            )

        # Open a connection to the SQLite databaase.
        connection: sqlite3.Connection = sqlite3.connect(
            self.database
        )

        # Using a limit and id starting point for pagination.
        query: str = """
            SELECT
                transaction_id,
                customer_id,
                amount,
                transaction_time
            FROM
                transactions
            WHERE
                transaction_id > ?
            ORDER BY
                transaction_id
            LIMIT ?
        """

        # Execute the query using parameterized values.
        cursor: sqlite3.Cursor = connection.execute(
            query,
            (after_id, limit)
        )

        # Retrieve all rows from teh query.
        rows: list[tuple] = cursor.fetchall()

        # Close the database connection
        connection.close()

        # Convert each database row into a dictionary.
        transactions: list[dict] = [
            {
                "transaction_id": row[0],
                "customer_id": row[1],
                "amount": row[2],
                "transaction_time": row[3],
            }
            for row in rows
        ]

        # FastAPI converts the returned Python list into JSON
        return transactions




# Create the API object outside of the main, then updates can be 
# implemented without shutting down the server at the command line with 
# this command:
#   uvicorn transactions_fastapi:api.app --reload
api = TransactionAPI()




if __name__ == "__main__":

    # Start the FastAPI development server.
    uvicorn.run(
        api.app,
        host="127.0.0.1",
        port=8000
    )
