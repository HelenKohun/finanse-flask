# 📈 Finance Tracker (Flask Web App)

## 📌 Description

Finance Tracker is a web application built with Flask that simulates a stock trading platform. Users can register, log in, view stock quotes, buy and sell shares, and track their transaction history.

The project demonstrates full-stack web development concepts including authentication, database management, and external API integration for stock data.

---

## ✨ Features

### 🔐 User Authentication

- User registration and login system
- Secure password hashing using Werkzeug
- Session-based authentication
- Password change functionality

---

### 📊 Portfolio Management

- View current stock portfolio
- Real-time stock price lookup
- Automatic portfolio valuation (including cash balance)

---

### 💰 Trading System

- Buy stocks using available cash
- Sell owned stocks
- Validation of share availability and user balance
- Transaction handling with proper database updates

---

### 📜 Transaction History

- Full history of all buy/sell operations
- Stores transaction type, price, and shares

---

### 🔍 Stock Quotes

- Real-time stock price lookup via external API
- Displays company name and current price

---

### 🔒 Security & Data Integrity

- Password hashing (Werkzeug)
- Protected routes using login_required decorator
- Input validation for all forms
- User-specific data isolation

---

## 🛠 Technologies Used

- Python
- Flask
- CS50 SQL (SQLite)
- HTML
- CSS
- JavaScript
- Jinja2 templates
- External stock API (lookup function)

---

## 📁 Project Structure

finance/
│
├── templates/
│ ├── layout.html
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── buy.html
│ ├── sell.html
│ ├── quote.html
│ ├── history.html
│ ├── change_password.html
│ └── apology.html
│
├── static/
│ └── styles.css
│
├── app.py
├── helpers.py
├── finance.db
├── requirements.txt
└── README.md

---

## ⚙️ How It Works

### 🔐 Authentication

Users register and log in to access the system. Sessions are stored securely, and all routes (except login/register) require authentication.

---

### 📊 Portfolio

The homepage displays:

- Owned stocks (grouped by symbol)
- Current market price
- Total portfolio value (stocks + cash)

---

### 💰 Buying Stocks

- User enters stock symbol and number of shares
- System validates input and available cash
- Transaction is recorded in database

---

### 💸 Selling Stocks

- User selects owned stock
- System checks available shares
- Updates cash balance and records transaction

---

### 📜 History

All transactions are stored and displayed with:

- Symbol
- Number of shares
- Price
- Buy/Sell type

---

### 🔑 Password Change

Users can securely update their password after verifying the current one.

---

## 🚀 Future Improvements

- Add portfolio charts and analytics
- Improve mobile responsiveness
- Add stock performance graphs
- Export transaction history (CSV/PDF)
- Improve UI/UX design

---

## 🌐 Deployment

This project can be deployed using platforms like Render or similar services supporting Flask applications.

---

## 👩‍💻 Author

**Helen Kohun**
