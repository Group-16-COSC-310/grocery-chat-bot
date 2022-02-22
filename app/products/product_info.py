import os
from app.products.database import SQLiteDatabase, DatabaseType, MOCK_PRODUCT_DATA, STORE_INFO
import re


class StoreProductHandler:
    """
    A class used to represent a mini-bot to handle product queries.

    Attributes
    ----------
    runtime_mode : str
        The environment that the bot is running in (i.e. DEV or PRODUCTION).

    handler_map : dict
        The mapping from sub-topic and corresponding handler.

    Methods
    -------
    handle(message: str)
        Handle the message and return the proper response.
    """

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes for the ProductHandler object.
        """
        # Set the operation mode (i.e. DEV or PRODUCTION)
        self.runtime_mode = os.getenv("PYTHON_ENV", "DEV")

        # Initialize the mapping from sub-topic and handler
        self.handler_map = {
            "product_info": self.handle_product_info,
            "store_info": self.handle_store_info
        }

        # Create pattern matches
        self.create_match_paterns()

        # Initialize a mock database if development environment
        if self.runtime_mode == "DEV":
            self.db = SQLiteDatabase(DatabaseType.MEMORY)
            self.db.connect()  # Start a connection
            self.db.init_database()  # Initialize the database
        else:
            self.db = None

    def create_match_paterns(self):
        """
        This method is called when the class is initialized.
        """
        # Product-related patterns
        self.price_pattern = re.compile(
            r"(price|cost|how much)", re.IGNORECASE)
        self.stock_pattern = re.compile(r"(stock|how many)", re.IGNORECASE)

        # Store-related patterns
        self.location_pattern = re.compile(
            r"(where|location|address|street)", re.IGNORECASE)
        self.opening_pattern = re.compile(
            r"(when|open|close|opening|closing|hours)", re.IGNORECASE)
        self.phone_pattern = re.compile(r"(phone|number)", re.IGNORECASE)
        self.price_range_pattern = re.compile(
            r"(price range|range)", re.IGNORECASE)
        self.website_pattern = re.compile(r"(website|url|web)", re.IGNORECASE)
        self.city_pattern = re.compile(r"(city|town)", re.IGNORECASE)
        self.province_pattern = re.compile(r"(province|state)", re.IGNORECASE)
        self.country_pattern = re.compile(r"(country)", re.IGNORECASE)
        self.postal_code_pattern = re.compile(r"(postal|zip)", re.IGNORECASE)

    def dispose(self):
        """
        Call this methods to release any resources with this minibot (i.e. database connection).
        """
        self.db.close()

    def handle(self, message: str) -> str:
        """
        The entry point of the mini-bot. 

        Main bot will call this method to pass in the message to process.

        Parameters
        ----------

        message: str
            The message that the user sends to the bot.


        Returns
        ----------
        response: str
            The response string to the request message
        """

        response = None

        # Parse the query
        topic, kargs = self.parse_query(message=message)

        # Get the handler
        handler = self.handler_map.get(topic)

        # If there is a topic detected, we find the response
        # By calling the handler with the message (for convenience) and its necessary arguments
        if handler:
            response = handler(message, **kargs)

        return response

    def parse_query(self, message: str) -> tuple:
        """
        Method to parse the query and return the a tuple of (topic_name, arguments for handler).

        This method runs the message via a pipeline of parsers and return the first topic that is detected.

        Parameters
        ----------

        message : str
            The message that the user sends to the bot.
        """

        # Define a topic name and arguments for handler
        name = None
        kwargs = {}

        # Check if it a product query
        matched, name, kwargs = self.parse_product_info(message=message)

        # Check if it is a store query
        # This only runs if product request parser returns false on status.
        if not matched:
            _, name, kwargs = self.parse_store_info(message=message)

        return name, kwargs

    # @Paul @Thuan
    # TODO: Implement helper method to parse product information.
    # This method should return a tuple of (boolean, str, dict).
    # The first item indicates whether this request is about product information.
    def parse_product_info(self, message: str) -> tuple:
        is_prod = False
        prod_words = {"request": None, "product_name": None}

        # Check for keywords for prices
        if self.price_pattern.match(message):
            prod_words["request"] = "price"
        elif self.stock_pattern.match(message):
            prod_words["request"] = "stock"

        # If the request is truly about product
        if prod_words['request']:
            is_prod = True

        for prod in MOCK_PRODUCT_DATA:
            prod_name = prod["name"]
            prod_id = prod["id"]
            prod_names = prod["names"]

            if prod_name in message or prod_id in message or prod_names in message:
                prod_words["id"] = prod["id"]

        return (is_prod, "product_info", prod_words)

    # @Quan @Paul
    # TODO: Implement helper method to parse store information.
    # This method should return a tuple of (boolean, str, dict).
    # The first item indicates whether this request is about store information.
    # If false, the other items must be None.
    def parse_store_info(self, message) -> tuple:
        is_store = False
        store_words = {"request": None}

        if self.location_pattern.match(message):
            store_words["request"] = "address"
        elif self.opening_pattern.match(message):
            store_words["request"] = "opening_hours"
        elif self.price_range_pattern.match(message):
            store_words["request"] = "price"
        elif self.phone_pattern.match(message):
            store_words["request"] = "phone"
        elif self.website_pattern.match(message):
            store_words["request"] = "website"
        elif self.city_pattern.match(message):
            store_words["request"] = "city"
        elif self.province_pattern.match(message):
            store_words["request"] = "province"
        elif self.postal_code_pattern.match(message):
            store_words["request"] = "postal_code"
        elif self.country_pattern.match(message):
            store_words["request"] = "country"

         # If the request is truly about store
        if store_words["request"] is not None:
            is_store = True

        return (is_store, "store_info", store_words)

    # @Paul @Thuan
    # TODO: Implement the method to return proper response for product information.
    # Note: This is the signature for all handler methods.
    # If false, the other items must be None.
    def handle_product_info(self, message=None, **kwargs) -> str:
        # kwargs are arguments such as product_name, price, operators (<. >)
        # This really depends on how you define your parser
        prod_id = kwargs["id"]

        # Get the product information
        products = self.get_product("id", prod_id)

        # Since id is unique, we can assume there is only one product
        product = products[0]

        reply = None

        prod_msg_type = kwargs.get("requests")
        if prod_msg_type == "price":
            reply = "%s cost $%s %s." % (
                product['names'].capitalize(), product['price'], product['price_scale'])
        elif prod_msg_type == "stock":
            if product['in_stock']:
                reply = "%s are in stock." % (product['names'].capitalize())
            else:
                reply = "%s are out of stock." % (
                    product['names'].capitalize())

        return reply

    # @Quan @Paul
    # TODO: Implement the method to return proper response for product information.
    # Note: This is the signature for all handler methods.
    def handle_store_info(self, message=None, **kwargs) -> str:
        # kwargs are arguments such as product_name, price, operators (<. >)
        # This really depends on how you define your parser
        reply = "It is {}".format(STORE_INFO[kwargs["request"]])
        return reply

    # @Thuan @Paul @Quan
    # TODO: Once database is improved for use, we can have a more flexible way to retrieve data.
    # For now, only 1 attribute can be matched at a time.
    def get_product(self, attr: str, value=None) -> list:
        """
        Method to get the first product that has a matching attribute value.

        This is equivalent to SELECT * WHERE attr = value.

        Parameters
        ----------

        attr: str
            The attribute name.

        value: any
            The value to match for specified attribute.


        Returns
        ----------

        product: dict
            The information about the product.
        """

        # Define a list
        products = []

        # Create a query statement
        query = f"SELECT * FROM product WHERE {attr} = '{value}'"

        # Execute the query
        cursor = self.db.execute_query(query)

        for row in cursor:
            # Create a dictionary representing a product
            product = dict()
            product["id"] = row[0]
            product["name"] = row[1]
            product["names"] = row[2]
            product["price"] = row[3]
            product["price_scale"] = row[4]
            product["in_stock"] = True if row[5] > 0 else False

            # Add to the list
            products.append(product)

        return products
