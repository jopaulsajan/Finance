# Finance
Finance

Technologies:  
- Python  
- Flask with session authentication  
- SQL  
- HTML  
- CSS  
- Bootstrap  

Summary:
Finance is a web application that enables registered users to simulate buying and selling stocks using virtual currency. Users can view real-time stock prices through the IEX API, track their portfolio, and review their transaction history.  

How to Run:
1. Clone the repository and navigate to the project directory.  
2. Activate a virtual environment:  
   ```bash
   python3 -m venv .venv
   ```
   Select the virtual environment as the active workspace.  
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
4. Set the Flask environment variable:  
   ```bash
   export FLASK_APP=application.py
   ```
5. Configure and export your IEX API key following the provided instructions.  
6. Run the application:  
   ```bash
   flask run
   ```
7. Open the site in your browser and register for a new account to manage your stock portfolio.  

---

### App Features:

1. Register: 
- Allows new users to sign up.  
- Displays an error message if the username already exists or if the form is incomplete.  

2. Index (Homepage):
- Shows the user's current stock holdings in a table.  
- Includes the number of shares, current stock price, and the total value of each holding.  
- Displays the available cash balance and the combined value of cash and stock.  

3. Quote:
- Lets users search for a stock's current price using real-time data from the IEX API.  
- Displays an error if the stock symbol is invalid.  

4. Buy:
- Allows users to purchase stocks by entering a valid stock symbol and the number of shares.  
- Ensures the user has sufficient funds and records the transaction in the database.  

5. Sell:
- Enables users to sell shares of any stock they currently own.  

6. History:
- Displays a table of all past transactions (both buys and sells).  
- Includes the stock symbol, number of shares, price, and date/time of each transaction.  

---

![image](https://github.com/user-attachments/assets/6ffce6b5-c8c4-48c0-851d-882ca8f08d9a)
![image](https://github.com/user-attachments/assets/8a265bd2-860a-4422-8e1b-1a5258e63300)
![image](https://github.com/user-attachments/assets/900c6a3e-4d24-42db-8f8a-cc7c91dfcd39)


Note:
The login, logout, and helper functions were part of the assignment's starter code, created by David J. Malan/Harvard ©2020.
