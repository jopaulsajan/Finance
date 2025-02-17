import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Query database for user's cash
    rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    if len(rows) != 1:
        return apology("could not find user", 400)
    cash = rows[0]["cash"]

    # Query database for user's stock holdings
    holdings = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING total_shares > 0
    """, session["user_id"])

    portfolio = []
    total_portfolio_value = 0

    # Loop over each holding and get the current price using lookup
    for holding in holdings:
        stock = lookup(holding["symbol"])
        if stock is None:
            return apology("error looking up stock", 400)

        # Calculate the total value of the shares
        total_value = stock["price"] * holding["total_shares"]
        total_portfolio_value += total_value

        # Add the stock info to the portfolio
        portfolio.append({
            "symbol": stock["symbol"],
            "name": stock["name"],
            "shares": holding["total_shares"],
            "price": usd(stock["price"]),
            "total": usd(total_value)
        })

    # Calculate grand total (stocks' total value + cash)
    grand_total = total_portfolio_value + cash

    # Render the index.html with portfolio and cash details
    return render_template("index.html", portfolio=portfolio, cash=usd(cash), grand_total=usd(grand_total))



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        # Ensure the stock symbol was provided
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("must provide stock symbol", 400)

        # Look up stock price using the lookup helper function
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        # Ensure the number of shares was provided
        try:
            shares = int(request.form.get("shares"))
            if shares <= 0:
                return apology("must provide a positive number of shares", 400)
        except:
            return apology("shares must be a positive integer", 400)

        # Query the user's cash balance
        rows = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        if len(rows) != 1:
            return apology("user not found", 400)
        cash = rows[0]["cash"]

        # Calculate total price for the shares
        total_price = stock["price"] * shares

        # Check if the user can afford the shares
        if cash < total_price:
            return apology("cannot afford", 400)

        # Deduct the total price from user's cash
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_price, session["user_id"])

        # Record the purchase in the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   session["user_id"], stock["symbol"], shares, stock["price"])

        # Redirect to the homepage
        return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transactions_db = db.execute("SELECT symbol, shares, price, date FROM transactions WHERE user_id = ?", user_id)

    # Ensure prices are correctly formatted as floats
    for transaction in transactions_db:
        transaction["price"] = float(transaction["price"])

    return render_template("history.html", transactions=transactions_db)






@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        # Ensure symbol is not blank
        if symbol == "":
            return apology("input is blank", 400)

        stock_quote = lookup(symbol)

        if not stock_quote:
            return apology("INVALID SYMBOL", 400)
        else:
            return render_template("quoted.html", symbol=stock_quote)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check if username already exists
        if len(rows) != 0:
            return apology("username already exists", 400)

        # Hash the user's password
        hash = generate_password_hash(request.form.get("password"))

        # Insert the new user into the database
        new_user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                                 request.form.get("username"), hash)

        # Remember which user has logged in
        session["user_id"] = new_user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")




@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (form submission)
    if request.method == "POST":

        # Get the symbol and number of shares from the form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate the symbol
        if not symbol:
            return apology("must select a stock", 400)

        # Validate the number of shares
        try:
            shares = int(shares)
            if shares <= 0:
                return apology("must provide a positive number of shares", 400)
        except:
            return apology("shares must be a positive integer", 400)

        # Query database for user's stock holdings
        rows = db.execute("""
            SELECT SUM(shares) AS total_shares
            FROM transactions
            WHERE user_id = ? AND symbol = ?
            GROUP BY symbol
        """, session["user_id"], symbol)

        # Ensure the user owns the stock and has enough shares
        if len(rows) != 1 or rows[0]["total_shares"] < shares:
            return apology("not enough shares", 400)

        # Lookup current price of the stock
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        # Calculate sale value
        sale_value = shares * stock["price"]

        # Update user's cash balance
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", sale_value, session["user_id"])

        # Update the transactions table (record the sale as a negative number of shares)
        db.execute("""
            INSERT INTO transactions (user_id, symbol, shares, price)
            VALUES (?, ?, ?, ?)
        """, session["user_id"], symbol, -shares, stock["price"])

        # Redirect to home page
        return redirect("/")

    # User reached route via GET (rendering the form)
    else:
        # Query database for user's stock holdings
        rows = db.execute("""
            SELECT symbol, SUM(shares) AS total_shares
            FROM transactions
            WHERE user_id = ?
            GROUP BY symbol
            HAVING total_shares > 0
        """, session["user_id"])

        # Render the sell form with the list of stocks
        return render_template("sell.html", stocks=rows)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user password"""

    # User reached route via POST (form submission)
    if request.method == "POST":
        # Get the current and new passwords from the form
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Ensure current password was submitted
        if not current_password:
            return apology("must provide current password", 400)

        # Ensure new password was submitted
        elif not new_password:
            return apology("must provide new password", 400)

        # Ensure confirmation was submitted
        elif not confirmation:
            return apology("must provide password confirmation", 400)

        # Ensure new password and confirmation match
        elif new_password != confirmation:
            return apology("new passwords do not match", 400)

        # Query database for the current user's password hash
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Ensure current password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], current_password):
            return apology("invalid current password", 403)

        # Hash the new password
        new_hash = generate_password_hash(new_password)

        # Update the user's password in the database
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hash, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (rendering the form)
    else:
        return render_template("change_password.html")
