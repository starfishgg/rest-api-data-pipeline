"""
transaction_client.py

A small Python client that retrieves transaction data
from the FastAPI REST API.
"""

import requests

from pyspark.sql import SparkSession, DataFrame




class TransactionClient:

    def __init__(self) -> None:
        # URL of the  FastAPI server.
        self.base_url: str = "http://127.0.0.1:8000"


    def get_transactions(
            self,
            after_id: int = 0,
            limit: int = 100,
    ) -> list[dict]:
        """
        Retrieve one page of transactions from the API.
        """

        response: requests.Response = requests.get(
            f"{self.base_url}/transactions",
            params={
                "after_id": after_id,
                "limit": limit
            }
        )

        # Raise an exception if the API returned an error status.
        response.raise_for_status()

        # Convert the JSON response into python objects.
        transactions: list[dict] = response.json()

        return transactions


    """
    limit in this case does not mean retrieve only 2 transactions overall. It means retrieve the data in pages of 2 transactions at a time.
    """
    def get_all_transactions(
            self,
            limit: int = 100
    ) -> list[dict]:
        """
        Retrieve all transactions from the API using pagination.
        """
        
        after_id = 0
        all_transactions: list[dict] = []

        while True:
            transactions: list[dict] = self.get_transactions(
                after_id=after_id,
                limit=limit
            )

            # TEST PRINT TO CONFIRM WORKING
            # print("Retrieved:", transactions)

            # if transactions are empty, we are finished 
            # populating all_transactions
            if not transactions:
                break

            # .extend adds all items from transactions to 
            # all_transactions
            all_transactions.extend(transactions)

            # transactions[-1] gets the last item in the current page.
            after_id = transactions[-1]["transaction_id"]

        return all_transactions


    def create_dataframe(
            self,
            transactions: list[dict]
    ) -> DataFrame:
        """
        Convert transaction data into a PySpark DataFrame.
        """

        # Create a Spark session, which is the entry point for
        # working with DataFrames and other Spark functionality.
        spark: SparkSession = (
            SparkSession.builder
            .appName("TransactionAnalysis")
            .getOrCreate()
        )

        # Convert the list of Python dictionaries into a Spark DataFrame.
        dataframe: DataFrame = spark.createDataFrame(
            transactions
        )

        return dataframe


if __name__ == "__main__":

    # Create the API client.
    client = TransactionClient()

    # Retrieve one page of transactions.
    transactions = client.get_all_transactions(
        limit=2
    )

    # Convert the API data into a Spark DataFrame
    dataframe = client.create_dataframe(transactions)

    # Display the DataFrame
    dataframe.show()

    # Stop the Spark session when processing is complete.
    dataframe.sparkSession.stop()

