"""
main.py
"""

from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

connection = sqlite3.connect("transactions.db")

connection.execute("DROP TABLE IF EXISTS transactions")

connection.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        transaction_time TEXT NOT NULL
    )
""")

connection.executemany("""
    INSERT INTO transactions (
        transaction_id,
        customer_id,
        amount,
        transaction_time
    )
    VALUES (? ,? ,? ,?)
""", [
    (1, 111, 11.00, "2026-09-20 10:15:00"),
    (2, 222, 22.00, "2026-09-20 11:30:00"),
    (3, 111, 35.50, "2026-09-21 09:20:00"),
    (4, 111, 18.75, "2026-09-22 14:10:00"),
])

connection.commit()
connection.close()


@app.route("/transactions", methods=["GET"])
def get_transactions():
    customer_id = request.args.get("customer_id")

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    # Get/filter data here
    transactions = [
        {"id": 1, "customer_id": 123, "amount": 50.0},
        {"id": 2, "customer_id": 456, "amount": 75.0},
    ]

    if customer_id:
        transactions = [
            t for t in transactions
            if str(t["customer_id"]) == customer_id
        ]

    return jsonify(transactions)


@app.route("/customers/<int:customer_id>/transactions", methods=["GET"])
def get_customer_transactions(customer_id):

    if customer_id <= 0:
        return jsonify({"error": "customer_id must be positive"}), 400

    connection = sqlite3.connect("transactions.db")

    query = """
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

    customer = connection.execute(query, (customer_id,))

    if customer is None:
        connection.close()
        return jsonify({"error": "Customer not found."}), 404

    rows = customer.fetchall()

    if not rows:
        return jsonify({"error": "No transactions found."}), 200

    connection.close()

    transactions = [
        {
            "transaction_id": row[0],
            "amount": row[1],
            "transaction_time": row[2]   
        }
        for row in rows
    ]

    return jsonify(transactions)

    

if __name__ == "__main__":
    app.run(debug=True)
