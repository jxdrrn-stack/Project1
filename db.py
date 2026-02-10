import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vyo231106",
        database="vyok"
    )

def insert_product(platform, name, price, currency, scrape_time, item_type, product_url=None):
    """
    Insert product into database with optional product_url
    """
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO products (platform, product_name, price, currency, scrape_time, item_type, product_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (platform, name, price, currency, scrape_time, item_type, product_url))
    conn.commit()
    conn.close()