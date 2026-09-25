"""
flask.py

A small Flask REST API that retrieves customer transactions
from a SQLite database.
"""

import sqlite3
from flask import Flask, jsonify, Response #, Request




class TransactionAPI :

    def __init__(self) -> None:
        # Create the Flask application.
        self.app: Flask = Flask(__name__)

        # SQLite database file used by the application.
        self.database: str = "transactions.db"

        # Prepare the database and register the API routes.
        self.create_database()
        self.setup_routes()


    def create_database(self) -> None:
        """
        Create the transactions table and add test data.
        """

        # Open a connection to the SQLite database.
        connection: sqlite3.Connection = sqlite3.connect(self.database)

        # Create the table if it does not already exist.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                transaction_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                transaction_time TEXT NOT NULL
            )
        """)

        # Insert some test transactions.
        # INSERT OR IGNORE prevents duplicate primary-key errors
        # if the application is started mroe than once.
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

        # Save the cahnges to the database.
        connection.commit()

        # Close the database connection.
        connection.close()


    def setup_routes(self) -> None:
        """
        Register the API endpoints with Flask.
        """

        # Register:
        # GET /customers/<customer_id>/transacionts
        #
        # <int:customer_id> tells Flask to:
        # 1. Expect an integer in this part of the URL.
        # 2. Pass that integer to get_customer_transactions().
        self.app.add_url_rule(
            "/customers/<int:customer_id>/transactions",
            "get_customer_transactions",
            self.get_customer_transactions,
            methods=["GET"]
        )

        self.app.add_url_rule(
            "/transactions",
            "get_all_transactions",
            self.get_all_transactions,
            methods=["GET"]
        )


    def get_customer_transactions(self, customer_id: int) -> Response | tuple[Response, int]:
        """
        Return all transactions belonging to a customer.
        """

        # Reject invalid customer IDs before querying the database.
        if customer_id <= 0:
            return jsonify({
                "error": "customer_id must be positive"
            }), 400

        
        # Open a connection to the SQLite database.
        connection = sqlite3.connect(self.database)


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
        # It does NOT reuturn the actual rows yet.
        cursor: sqlite3.Cursor = connection.execute(query, (customer_id,))

        # fetchall() retrieves all rows returned by the query.
        #
        # Example:
        # [
        #     (1, 11.0, "2026-09-20 10:15:00"),
        #     (3, 35.5, "2026-09-21 09:20:00")
        # ]
        rows: list[tuple] = cursor.fetchall()

        # Display the query results while developing/debugging
        print("customer_id:", customer_id)
        print("rows:", rows)

        # An empty list means the query found no transactions
        # for this customer.
        if not rows:
            connection.close()
            return jsonify({"error": "no transactions found"}), 200

        # We have finished using the database connection.
        connection.close()


        # Convert each database row into a dictionary.
        #
        # This gives us a structure that can easily be converted
        # into JSON by Flask's jsonify().
        transactions = [
            {
                "transaction_id": row[0],
                "amount": row[1],
                "transaction_time": row[2]
            }
            for row in rows
        ]

        # Return the list of dictionaries as a JSON response.
        return jsonify(transactions)


    def get_all_transactions(self):
        """
        Return all transactions.
        """

        connection:sqlite3.Connection = sqlite3.connect(self.database)

        query: str = """
            SELECT
                transaction_id,
                customer_id,
                amount,
                transaction_time
            FROM
                transactions
            ORDER BY
                transaction_time
        """

        cursor: sqlite3.Cursor = connection.execute(query) 

        rows: list[tuple] = cursor.fetchall()

        connection.close()

        transactions: list[dict] = [
            {
                "transaction_id"   : row[0],
                "customer_id"      : row[1],
                "amount"           : row[2],
                "transaction_time" : row[3],
            }
            for row in rows
        ]

        return jsonify(transactions)




if __name__ == "__main__":
    api = TransactionAPI()
    api.app.run(debug=True)

