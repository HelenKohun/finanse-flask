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

    user_purchases = db.execute(
        "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING shares > 0", session["user_id"])

    total = 0

    for purchase in user_purchases:
        quote = lookup(purchase["symbol"])
        purchase["current_price"] = quote["price"]
        purchase["total"] = purchase["shares"] * purchase["current_price"]
        total += purchase["total"]

    cash_row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cash_row[0]["cash"]
    total += cash

    return render_template("index.html", user_purchases=user_purchases, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        # Ensure user input is not blank
        if not symbol:
            return apology("Please type a symbol")

        # Ensure user input is a valid symbol
        user_input = lookup(symbol)
        if not user_input:
            return apology("Invalid symbol")

        # Ensure the input is not a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares < 1:
                return apology("Number of shares must be positive")
        except ValueError:
            return apology("Shares must be an integer")

        # Ensure user can afford the purchase
        cash_row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

        if not cash_row:
            return apology("User not found")

        cash = cash_row[0]["cash"]

        # What the total price for the purchase
        total_price = user_input["price"] * shares

        if cash < total_price:
            return apology("You  cannot afford this purchase")

        # Add transaction to the transactions table
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(?, ?, ?, ?)",
                   session["user_id"], user_input["symbol"], shares, user_input["price"])

        # Update the user cash value
        cash -= total_price
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        transaction_type = "bought"

        db.execute("INSERT INTO history (user_id, symbol, shares, price, transaction_type) VALUES(?,?,?,?,?)",
                   session["user_id"], symbol, shares, user_input["price"], transaction_type)

        flash("Bought!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    history_db = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])

    return render_template("history.html", history_db=history_db)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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

    if request.method == "POST":
        user_request = lookup(request.form.get("symbol"))
        if not user_request:
            return apology("Invalid symbol")

        return render_template("quote.html", name=user_request["name"], price=user_request["price"])

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        # Ensure username was provided

        if not username:
            return apology("Missing name")

        check_username = db.execute("SELECT username FROM users WHERE username = ?", username)
        # Ensure username is not already taken

        if check_username:
            return apology("Username is already taken")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Ensure password and confirmation were provided

        if not password or not confirmation:
            return apology("Missing password or confirmation")
        # Ensure password and confirmation match

        if password != confirmation:
            return apology("Passwords do not match")

        # Add new user to the database

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, generate_password_hash(password))

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # Store the user's ID in session to keep them logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        # Taking data
        sold_symbol = request.form.get("symbol")
        sold_shares = request.form.get("shares")

        # Update the transactions after sell
        if not sold_symbol or sold_symbol.strip() == "":
            return apology("Please select an option")
        if not sold_shares or not sold_shares.isdigit():
            return apology("Number of shares must be a positive integer")

        sold_shares = int(sold_shares)

        if sold_shares <= 0:
            return apology("Number of shares must be a positive integer")

        # All user's purchases
        user_purchases = db.execute(
            "SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING symbol = ?", session["user_id"], sold_symbol)

        if not user_purchases:
            return apology("You don't have any quotes available")

        total_shares = user_purchases[0]["shares"]

        if sold_shares > total_shares:
            return apology("You don't have that many shares to sell")

        quote = lookup(sold_symbol)

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES(?,?,?,?)",
                   session["user_id"], sold_symbol, -sold_shares, quote["price"])

        cash_row = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        user_cash = cash_row[0]["cash"]

        proceeds = sold_shares * quote["price"]

        cash = user_cash + proceeds

        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        # Insert data into the history table
        transaction_type = "sold"

        db.execute("INSERT INTO history (user_id, symbol, shares, price, transaction_type) VALUES(?,?,?,?,?)",
                   session["user_id"], sold_symbol, sold_shares, quote["price"], transaction_type)

        return redirect("/")

    else:
        user_purchases = db.execute(
            "SELECT symbol, shares FROM (SELECT symbol, SUM(shares) AS shares FROM transactions WHERE user_id = ? GROUP BY symbol) WHERE shares > 0", session["user_id"])
        if not user_purchases:
            return apology("You don't have any quotes available")

        return render_template("sell.html", user_purchases=user_purchases)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation_password = request.form.get("confirmation")

        if not old_password:
            return apology("Missing current password")

        if not new_password or not confirmation_password:
            return apology("Missing password or confirmation")

        if new_password != confirmation_password:
            return apology("Passwords do not match")

        row = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        check_password = check_password_hash(row[0]["hash"], old_password)

        if not row or not check_password:
            return apology("Invalid current password")

        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(new_password), session["user_id"])

        flash("Password was changed!")
        return redirect("/")

    else:
        return render_template("change_password.html")
