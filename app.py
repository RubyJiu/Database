from flask import Flask, render_template, request, redirect, url_for
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


def fetch_categories(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name FROM categories ORDER BY name ASC")
    cats = cur.fetchall()
    cur.close()
    return cats


def fetch_book_by_id(conn, book_id: int):
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT b.id, b.name, b.author, b.price, b.description, b.category_id
        FROM books b
        WHERE b.id = %s
        """,
        (book_id,),
    )
    row = cur.fetchone()
    cur.close()
    return row


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
        categories = fetch_categories(conn)
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


@app.route("/books/create", methods=["GET", "POST"])
def create_book():
    conn = None
    error = None
    try:
        conn = get_db_connection()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            author = request.form.get("author", "").strip()
            description = request.form.get("description", "").strip()
            price_raw = request.form.get("price", "").strip()
            category_id = request.form.get("category_id", "").strip()

            if not name or not author or not price_raw or not category_id:
                error = "Nama, Author, Harga, dan Kategori wajib diisi."
            else:
                try:
                    price = float(price_raw)
                except ValueError:
                    error = "Harga tidak valid."

            if error is None:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO books (name, description, author, price, category_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (name, description, author, price, int(category_id)),
                )
                conn.commit()
                cur.close()
                return redirect(url_for("index"))

        categories = fetch_categories(conn)
        return render_template(
            "form.html",
            mode="create",
            categories=categories,
            book=None,
            error=error,
        )
    except Exception as e:
        error = str(e)
        return render_template("form.html", mode="create", categories=[], book=None, error=error)
    finally:
        if conn:
            conn.close()


@app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id: int):
    conn = None
    error = None
    try:
        conn = get_db_connection()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            author = request.form.get("author", "").strip()
            description = request.form.get("description", "").strip()
            price_raw = request.form.get("price", "").strip()
            category_id = request.form.get("category_id", "").strip()

            if not name or not author or not price_raw or not category_id:
                error = "Nama, Author, Harga, dan Kategori wajib diisi."
            else:
                try:
                    price = float(price_raw)
                except ValueError:
                    error = "Harga tidak valid."

            if error is None:
                cur = conn.cursor()
                cur.execute(
                    """
                    UPDATE books
                    SET name=%s, description=%s, author=%s, price=%s, category_id=%s
                    WHERE id=%s
                    """,
                    (name, description, author, price, int(category_id), book_id),
                )
                conn.commit()
                cur.close()
                return redirect(url_for("index"))

        # GET or validation error -> render form with current values
        categories = fetch_categories(conn)
        book = fetch_book_by_id(conn, book_id)
        if not book:
            return redirect(url_for("index"))
        if book and book.get("price") is not None:
            try:
                # convert Decimal to float for safe formatting
                book["price"] = float(book["price"])
            except Exception:
                pass
        return render_template(
            "form.html",
            mode="edit",
            categories=categories,
            book=book,
            error=error,
        )
    except Exception as e:
        error = str(e)
        return render_template("form.html", mode="edit", categories=[], book=None, error=error)
    finally:
        if conn:
            conn.close()


@app.route("/books/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int):
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        cur.close()
    except Exception:
        # We can ignore error here and still redirect, or pass via query param if desired.
        pass
    finally:
        if conn:
            conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    
    app.run()
