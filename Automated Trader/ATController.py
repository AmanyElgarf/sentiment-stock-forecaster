"""
To begin, let's start with a simple AT that doesn't take in any prediction data.
"""
from alpha_vantage.timeseries import TimeSeries
import mysql.connector as ms


class AutomatedTrader:
    def __init__(self, balance, stock_portfolio):
        """Creates a new Automated Trader

        :param balance: the user's current account balance
        :param stock_portfolio: list of stock tickers

        """
        assert isinstance(balance, float)
        self.balance = balance
        self.stock_portfolio = stock_portfolio
        # key: stock_symbol
        # value: stock_amount

    def check_initial_deposit(self):
        while True:
            print("\nWelcome! Please enter an initial deposit for your AutoTrader account balance:")
            user_input = input()
            try:
                initial_deposit = round(float(user_input), 2)
                if initial_deposit < 0:
                    print("Invalid input. Starting balance cannot be negative - please try again!")
                else:
                    print("You have successfully deposited $" + str(initial_deposit) + " to your AutoTrader account.\n")
                    self.balance += initial_deposit
                    return
            except ValueError:
                print("Invalid input. You must input some starting balance - please try again!")

    def initial_stock_selection(self):
        print("Let's begin by building a portfolio of companies that you're interested in investing in.")
        while True:
            print("Enter the stock ticker of a company that you are interested in (or 'done' when finished):\n")
            stock_symbol = input()
            if stock_symbol.lower() == "done":
                return
            self.search_stock_symbol(stock_symbol)

    # search database for if the stock_symbol exists
    def search_stock_symbol(self, stock_symbol):
        # connect to database
        cnx = ms.connect(user='root', password='mypassword', host='mydb.cwtgu3tqnwx8.us-east-2.rds.amazonaws.com',
                         database='mydb')
        my_cursor = cnx.cursor()

        query = "SELECT stock_code FROM stock"
        my_cursor.execute(query)
        result = my_cursor.fetchall()

        search_success = False
        for x in result:
            # if x == ('A',):
            if x[0] == stock_symbol:
                print("This stock exists. Adding stock to stock portfolio.")
                search_success = True
                # add stock symbol to portfolio with zero initial stocks
                self.stock_portfolio[stock_symbol] = 0

        if not search_success:
            print("This stock doesn't exist. Please try again.")

    # called in print_portfolio_prices(); returns the price of the requested stock
    def get_stock_price(self, stock_symbol):
        for stock_name in self.stock_portfolio.keys():
            if stock_name == stock_symbol:
                # connect to database
                cnx = ms.connect(user='root', password='mypassword',
                                 host='mydb.cwtgu3tqnwx8.us-east-2.rds.amazonaws.com',
                                 database='mydb')
                my_cursor = cnx.cursor()

                ts = TimeSeries(key='9YJC3VY3APE01WTD')
                data, meta_data, = ts.get_intraday(symbol='NYSE:' + stock_symbol, interval='5min', outputsize='compact')
                # print(list(data.values())[0])  # print current equity information
                # print(meta_data)

                dictvalue = list(data.values())[0]
                open_value = dictvalue.get('1. open')
                current_price = round(float(open_value), 2)
                return current_price

    # display current price information for stocks in portfolio
    def print_portfolio_prices(self):
        for stock_name in self.stock_portfolio.keys():
            print("\n" + stock_name + " ")
            print("The current price of this stock is $" + str(self.get_stock_price(stock_name)))

    # display list of stocks and corresponding shares
    def print_portfolio(self):
        print("Number of companies in your portfolio: " + str(len(self.stock_portfolio)))
        for k, v in self.stock_portfolio.items():
            print("You currently own " + str(v) + " " + str(k) + " shares.")

    def purchase_shares_manually(self):
        print("\nTo begin purchasing shares, first select a stock from your portfolio.")
        # self.print_balance()
        # self.print_portfolio()
        while True:
            print("Enter a stock symbol (or 'done' when finished):\n")
            stock_symbol = input()
            if stock_symbol.lower() == "done":
                return
            elif stock_symbol not in self.stock_portfolio.keys():
                print("You do not currently have '" + stock_symbol + "' in your portfolio.\n"
                      "Would you like to add " + stock_symbol + " to your portfolio? (yes/no)")
                user_response = input()
                if user_response.lower() == "yes":
                    self.search_stock_symbol(stock_symbol)
                else:
                    continue
            else:
                print("How many shares would you like to purchase for " + stock_symbol + "?")
                user_input = input()
                try:
                    shares_purchased = int(user_input)
                    if shares_purchased < 0:
                        print(
                            "Invalid input. You cannot purchase negative shares - please try again!")
                    else:
                        if round((self.get_stock_price(stock_symbol))*shares_purchased, 2) > self.balance:
                            print("You don't have enough money to purchase that many shares.")
                        else:
                            print("You have successfully purchased " + str(
                            shares_purchased) + " " + stock_symbol + " shares.")
                            self.stock_portfolio[stock_symbol] = self.stock_portfolio[stock_symbol] + shares_purchased
                            self.balance -= (self.get_stock_price(stock_symbol))*shares_purchased
                except ValueError:
                    print("Invalid input. You must input a number - please try again!")

    def sell_shares_manually(self):
        print("To begin selling, first select a stock from your portfolio:\n")
        # self.print_balance()
        # self.print_portfolio()
        while True:
            print("\nEnter a stock symbol (or 'done' when finished):")
            stock_symbol = input()
            if stock_symbol.lower() == "done":
                return
            elif stock_symbol not in self.stock_portfolio.keys():
                print("You do not currently have " + stock_symbol + " in your portfolio.\n")
                continue
            else:
                print("How many shares would you like to sell for " + stock_symbol + "?")
                user_input = input()
                try:
                    shares_sold = int(user_input)
                    if shares_sold < 0:
                        print(
                            "Invalid input. You cannot sell negative shares - please try again!")
                    else:
                        if shares_sold > self.stock_portfolio[stock_symbol]:
                            print("You do not own that many " + stock_symbol + " shares.")
                        else:
                            print("You have successfully sold " + str(shares_sold) + " " + stock_symbol + " shares.")
                            self.stock_portfolio[stock_symbol] = self.stock_portfolio[stock_symbol] - shares_sold
                            self.balance += (self.get_stock_price(stock_symbol))*shares_sold
                except ValueError:
                    print("Invalid input. You must input a number - please try again!")

    def begin_trader(self):
        self.print_balance()
        self.print_portfolio()
        print("\nI will now arbitrarily choose to buy or sell stocks.\n")
        # for each stock in portfolio
        # insert prediction input
        # test: sell one stock
        # to be implemented later
        print("The trading period has ended. Here is your updated balance and portfolio:\n")
        self.print_balance()
        self.print_portfolio()

    def print_balance(self):
        print("You have $" + str(round(self.balance, 2)) + " in your account balance.")

    def connect_to_database(self):
        # TO-DO (optional)
        return

    def deposit_money(self):
        print("Enter the amount of money to deposit:")
        user_input = input()
        try:
            deposit = round(float(user_input), 2)
            if deposit < 0:
                print("Invalid input. Deposit cannot be negative - please try again!")
            else:
                print("You have successfully deposited $" + str(deposit) + " to your AutoTrader account.\n")
                self.balance += deposit
        except ValueError:
            print("Invalid input. Deposit is not a number.")

    def withdraw_money(self):
        print("Enter the amount of money to withdraw:")
        user_input = input()
        try:
            withdrawal = round(float(user_input), 2)
            if withdrawal < 0:
                print("Invalid input. Withdrawal cannot be negative - please try again!")
            else:
                if withdrawal > self.balance:
                    print("You do not have that much money to withdraw.")
                else:
                    print("You have successfully withdrawn $" + str(withdrawal) + " from your AutoTrader account.\n")
                    self.balance -= withdrawal
        except ValueError:
            print("Invalid input. Withdrawal is not a number.")


# testing functionality
my_account = AutomatedTrader(0.0, {})
my_account.check_initial_deposit()
my_account.initial_stock_selection()
my_account.print_balance()
my_account.print_portfolio()
my_account.print_portfolio_prices()
my_account.purchase_shares_manually()
my_account.print_balance()
my_account.print_portfolio()
my_account.deposit_money()
my_account.withdraw_money()
my_account.print_balance()
