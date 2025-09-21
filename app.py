from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# MySQL configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "booksdb",
}


def get_db_connection():
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
    )


@app.route("/")
def index():
    conn = None
    cursor = None
    books = []
    error = None
    categories = []
    # Read filters and sorting from query params
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    sort = request.args.get("sort", "id").strip().lower()
    order = request.args.get("order", "asc").strip().lower()

    # Avoid SQL injection
    sortable = {
        "id": "b.id",
        "name": "b.name",
        "author": "b.author",
        "price": "b.price",
        "category": "c.name",
    }
    sort_col = sortable.get(sort, "b.id")
    order_dir = "DESC" if order == "desc" else "ASC"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Build dynamic WHERE with parameters
        query = (
            "SELECT b.id, b.name, b.author, b.price, b.description, c.name AS category "
            "FROM books b "
            "JOIN categories c ON b.category_id = c.id "
            "WHERE 1=1 "
        )
        params = []
        if q:
            query += "AND (b.name LIKE %s OR b.author LIKE %s) "
            like_q = f"%{q}%"
            params.extend([like_q, like_q])
        if category_id.isdigit():
            query += "AND b.category_id = %s "
            params.append(int(category_id))
        if min_price:
            try:
                mp = float(min_price)
                query += "AND b.price >= %s "
                params.append(mp)
            except ValueError:
                pass
        if max_price:
            try:
                xp = float(max_price)
                query += "AND b.price <= %s "
                params.append(xp)
            except ValueError:
                pass

        query += f"ORDER BY {sort_col} {order_dir}"
        cursor.execute(query, params)
        books = cursor.fetchall()
        # Ensure price is a float for safe formatting in templates
        for b in books:
            if "price" in b and b["price"] is not None:
                try:
                    b["price"] = float(b["price"])  # convert Decimal to float
                except Exception:
                    pass

        # Load categories for filter dropdown
        cursor2 = conn.cursor(dictionary=True)
        cursor2.execute("SELECT id, name FROM categories ORDER BY name ASC")
        categories = cursor2.fetchall()
        cursor2.close()
    except Exception as e:
        error = str(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template(
        "index.html",
        books=books,
        error=error,
        categories=categories,
        q=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort=sort,
        order=order,
    )


if __name__ == "__main__":
    
    app.run()
