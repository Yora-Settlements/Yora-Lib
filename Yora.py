import sys
import logging
import datetime
from time import sleep
from time import time

from lib import api_caller as caller
from lib import constants as c
from enum import Enum


logging.basicConfig(
    level=c.LOG_LEVEL,
    format=c.LOG_FORMAT,
    datefmt=c.LOG_DATE_FMT,
    filemode = 'w',
    filename = 'api.log'
)


class StatusCode(Enum):
    unknown_error = 1
    correspondence_required = 102
    resource_not_found = 103
    authentication_error = 1001
    invalid_transaction = 1009
    invalid_data = 1000
    ok = 0
    recaptcha_error = 1010
    email_taken = 1003
    missing_data = 1002
    request_too_large = 1008
    action_failed = 11
    server_prevented_action = 104
    transaction_did_not_settle = 105
    maintenance = 1005
    not_implemented = 1004
    wrong_protocol = 100
    invalid_action = 10
    rate_limit = 101
    insufficient_funds = 106
    amount_to_small = 107
    identity_not_verified = 1007
    account_locked = 1006
    

class TransactionTypes(Enum):
    yora_credit = 15
    basic = 0
    depost = 16
    deposit_pending = 11
    donation = 6
    transaction_failed = 14
    payment = 1
    refund = 13
    trade_created = 2
    trade = 5
    trade_cancelled = 3
    trade_failed = 4
    withdrawl = 10
    withdrawl_cancelled = 8
    withdrawl_failed = 9
    withdrawl_pending = 7


class API:
    # public interface
    BUY = 0
    SELL = 1

    SEC = 1
    MIN = 60
    HOUR = 60 * MIN
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 30 * DAY
    YEAR = 365 * DAY
    FOREVER = 200 * YEAR


    def __init__(self, email, password, tfa_flag=False):    # logs the user in, set flag to 'True' to use 2fa login 
        response = {}
        if tfa_flag == False:
            response = self.__login_user(email, password)
            self.__check_http_code(response)
            status_code = response.get('data').get('status_code')
            if status_code != StatusCode.ok.value:
                print('Returned status_code' + str(status_code) + ': ' + StatusCode(status_code).name)

        elif tfa_flag == True:
            response = self.__login_user_2fa(email, password)
            self.__check_http_code(response)
            status_code = response.get('data').get('status_code')
            if status_code != StatusCode.ok.value:
                print('Returned status_code' + str(status_code) + ': ' + StatusCode(status_code).name)


        self.__tkn = response.get('data').get('response').get('token')
        print(response)


    def get_supported_currencies(self):                   
        """Get all the currencies of the Yora platform

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        currencies : dict or None
            Dictionary of currencies and relevent values accessed by dictname['ticker']['info']
        """
        response = self.__get_currencies(self.__tkn)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None
        
        currencies = {}
        for coin in response.get('data').get('response'):
            currencies[coin.get('ticker')] = {
                'name' : coin.get('name'), 
                'min_deposit' : coin.get('min_deposit'),
                'wdr_fee' : coin.get('wdr_fee'), 
                'tx_fee' : coin.get('tx_fee'),
                'market' : coin.get('market'),
                'version' : coin.get('version'),
                'source_code' : coin.get('source_code'),
                'website' : coin.get('website'),
                'description' : coin.get('description')
            }
        return status_code, currencies


    def get_user_balances(self):                          
        """Gets the users balances

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        balances : dict or None
            Dictionary of currencies and their values, along with the sum in aud accessed by dictname['ticker']['info'] or dictname['sum_aud'] to get total bal.
        """

        response = self.__get_balances(self.__tkn)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None
        
        balances = {}
        for coin in response.get('data').get('response').get('currencies'):
            balances[coin.get('ticker')] = {
                'balance' : coin.get('balance'),
                'reserved' : coin.get('reserved'),
                'sum_aud' : coin.get('sum_aud')
            }
        balances['sum_aud'] = response.get('data').get('response').get('sum_aud')
        return status_code, balances


    def get_markets(self):                              
        """Gets information on the markets

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        markets : dict or None
            Dictionary of market information accessed via dictname['ticker']['info']
        """

        response = self.__get_markets(self.__tkn)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        markets = {}
        for mkt in response.get('data').get('response'):
            markets[mkt.get('ticker')] = {
                'change' : mkt.get('change'),
                'currency' : mkt.get('currency'),
                'market_id' : mkt.get('market_id'),
                'price' : mkt.get('price'),
                'price_max' : mkt.get('price_max'),
                'price_min' : mkt.get('price_min'),
                'vol' : mkt.get('vol')
            }
        return status_code, markets

    
    def get_order_book(self, market):               
        """Get the current market orders

        Parameters
        ----------
        market : int or str
            The market ID or name, eg 'GRC/AUD'
        
        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        orders : dict or None
            Indexed dictionary of all the orders on the market (open and closed) accessed via dictname['buy'][ordernum]['info'] or dictname['sell'][ordernum]['info']
        """

        response = {}
        if isinstance(market, int):
            response = self.__get_market_orders(self.__tkn, market)
        elif isinstance(market, str):
            markets = self.get_markets()
            if markets[0] != StatusCode.ok.value:
                return markets[0], None
            m_id = markets[1][market]['market_id']
            response = self.__get_market_orders(self.__tkn, m_id)
        
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None
  
        
        orders = response.get('data').get('response')
        return status_code, orders


    def get_order_history(self, page=None):      
        """Get the current user's order history

        Parameters
        ----------
        page : int, optional
            Specifies the page to display
        
        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        own_orders : dict or None
            Indexed dictionary of all the users orders (open and closed) accessed by dictname['open'][ordernum]['info'] or dictname['closed'][ordernum]['info']
        """

        response = self.__get_self_orders(self.__tkn, page)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None


        own_orders = response.get('data').get('response')  
        for i in range(len(own_orders.get('open'))):
            own_orders['open'][i]['time_created'] = self.__unixtime_to_datetime(own_orders.get('open').get(i).get('time_created')) 

        for i in range(len(own_orders.get('closed'))):
            own_orders[i]['time_created'] = self.__unixtime_to_datetime(own_orders.get('closed').get(i).get('time_created') / 1000)           # CHECK THIS FOR UNIXTIME
            own_orders[i]['time_completed'] = self.__unixtime_to_datetime(own_orders.get('closed').get(i).get('time_completed') / 1000)       # CHECK THIS FOR UNIXTIME

        return status_code, own_orders       


    def trade(self, market, direction, amount, price): 
        """Create a new trade 

        Parameters
        ----------
        market : str or int
            The ticker for the market, eg. 'GRC/AUD'
        direction : int or str
            Whether the order is a buy or sell order specified by YoraLib.BUY, or YoraLib.SELL constants
        amount : float
            The amount of the currency to buy or sell
        price : float
            The price to buy or sell at

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        response : dict or None
            Dictionary containing the trade ID and transaction ID accessed by dictname['trade_id'] or dictname['tx_id']
        """

        m_id = 0
        dirct = 0
        if isinstance(market, int):
            m_id = market
        elif isinstance(market, str):
            markets = self.get_markets()
            if markets[0] != StatusCode.ok.value:
                return markets[0], None
            m_id = markets[1][market]['market_id']

        response = self.__make_trade(self.__tkn, m_id, dirction, amount, price)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        return status_code, response.get('data').get('response')


    def cancel_trade(self, trade_id):
        """Cancel an active trade

        Parameters
        ----------
        trade_id : int 
            The ID of the active trade 

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        """

        response = self.__cancel_trade(self.__tkn, trade_id)
        self.__check_http_code(response)

        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code


    def get_address(self, currency):
        """Get the current user's crypto address for the requested currency

        Parameters
        ----------
        currency : str
            The ticker for the currency e.g. 'GRC'

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        address : str or None
            User's crypto address
        """

        response = self.__get_address(self.__tkn, currency)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        address = response.get('data').get('response').get('address')
        return status_code, address   

    
    def get_price(self, market):
        """Return the current price of the requested market

        Parameters
        ----------
        market : str or int
            The market can be either a str e.g "GRC/AUD" or the ID of the market 

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        price : float or None
            Current price of the market
        """

        m_id = 0
        if isinstance(market, int):
            m_id = market
        elif isinstance(market, str):
            markets = self.get_markets()
            if markets[0] != StatusCode.ok.value:
                return markets[0], None
            m_id = markets[1][market]['market_id']
        
        response = self.__get_price(m_id)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None


        price = response.get('data').get('response').get('price')
        return status_code, price
        

    def cancel_withdrawal(self, txid):
        """Cancel a withdrawl request 

        Parameters
        ----------
        txid : str
            Transaction ID

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        """

        response = self.__cancel_withdrawal(self.__tkn, txid)
        self.__check_http_code(response)

        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code


    def withdraw_crypto(self, currency, amount, address):
        """Withdraw cryptocurrency to an external wallet

        Parameters
        ----------
        currency : str
            The currency to withdraw, eg. 'GRC'
        amount : float
            The amount of the specified currency to withdraw
        address : str
            The wallet address to withdraw to
        
        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        tx_id : str or None
            The transaction ID of the withdrawal
        """

        response = self.__make_withdrawal_crypto(self.__tkn, currency, amount, address)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        return status_code, response.get('data').get('response').get('tx_id')


    def __make_withdrawal_fiat(self, currency, amount, bsb, account_num, addressee, message=""):
        """Withdraw fiat currency, eg. 'AUD' to a bank account

        Parameters
        ----------
        currency : str
            The currency to withdraw, eg. 'AUD'
        amount : float
            The amount of the specified currency to withdraw
        bsb : int
            The bank account BSB
        account_num : int
            The bank account number
        addressee : str
            The name of the account holder
        message : str, optional
            Tthe message that appears on the transaction
        
        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        tx_id : str or None
            The transaction ID of the withdrawal
        """

        response = self.__make_withdrawal_fiat(self.__tkn, currency, amount, bsb, account_num, addressee, message)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        return status_code, response.get('data').get('response').get('tx_id')


    def get_chart(self, market, interval, from_time, to_time, page=0):
        """Gets the information required to create a chart

        Parameters
        ----------
        market : str or int
            Enter the market id or the market name, eg. 'GRC/AUD'
        interval : int
            The charts time interval, use the constants YoraLib.SEC, MIN, DAY, ...
        from_time : str or int
            Enter a from time in either unix time or in date time format yyyy-mm-dd hh:mm:ss
        to_time : str or int
            Enter a from time in either unix time or in date time format yyyy-mm-dd hh:mm:ss

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        candles : dict or None
            Indexed dictionary of candle sticks accessed by dictname[index]['info'] or dictname[index] to get the entire candle
        """

        m_id = 0
        if isinstance(market, int):
            m_id = market
        elif isinstance(market, str):
            markets = self.get_markets()
            if markets[0] != StatusCode.ok.value:
                return markets[0], None
            m_id = markets[1][market]['market_id']

        ft = 0
        if isinstance(from_time, int):
            ft = from_time
        elif isinstance(from_time, str):
            ft = self.__datetime_to_unixtime(from_time)

        tt = 0
        if isinstance(to_time, int):
            tt = to_time
        elif isinstance(to_time, str):
            tt = self.__datetime_to_unixtime(to_time)

        response = self.__get_chart(self.__tkn, m_id, interval, ft, tt, page)
        self.__check_http_code(response)
        
        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        candles = response.get('data').get('response').get('candles')
        for i in range(len(candles)):
            candles[i]['time'] = self.__unixtime_to_datetime(candles.get(i).get('time') / 1000)         # CHECK THIS FOR UNIXTIME

        return status_code, candles       # indexed


    def market_history(self, market, page=0):
        """Gets all previous orders on the market specified

        Parameters
        ----------
        market : str or int
            Enter the market id or the market name, eg. 'GRC/AUD'
        page : int
            Optional value, specifies the page to display

        Returns
        -------
        status_code : int
            Status code of response, 0 on success
        orders : dict or None
            Indexed dictionary of orders
        """

        m_id = 0
        if isinstance(market, int):
            m_id = market
        elif isinstance(market, str):
            markets = self.get_markets()
            if markets[0] != StatusCode.ok.value:
                return markets[0], None
            m_id = markets[1][market]['market_id']

        response = self.__get_market_history(self.__tkn, m_id, page)     
        self.__check_http_code(response)

        status_code = response.get('data').get('status_code')
        if status_code != StatusCode.ok.value:
            return status_code, None

        orders = response.get('data').get('response') 
        for i in range(len(orders)):
            orders[i]['time'] = self.__unixtime_to_datetime(orders.get(i).get('time') / 1000)         # CHECK THIS FOR UNIXTIME

        return status_code, orders




    # private members
    def __check_http_code(self, response):                  # helper
        if response.get('http-code') != 200:
            print("Bad HTTP response: " + str(response.get("http-code")))
            logging.error("Bad HTTP response: " + str(response.get("http-code")))
            sys.exit(1)

    def __datetime_to_unixtime(dt):                         # helper
        return datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S").timestamp()

    def __unixtime_to_datetime(ut):                         # helper
        return datetime.datetime.fromtimestamp(ut)


    def __login_user(self, email, password):
        data = {
            'email' : email,
            'password' : password,
            'override_recaptcha' : 1                        # WARNING REMOVE THIS LATER
        }
        return caller.api_call_post('login', payload=data)


    def __login_user_2fa(self, email, password):
        data = {
            'email' : email,
            'password' : password,
            '2fa' : int(input('2FA code: '))
        }
        return caller.api_call_post('login', payload=data)


    def __get_currencies(self, token):
        return caller.api_call_get('currency', payload={'token' : token})


    def __get_balances(self, token):
        return caller.api_call_get('balances', payload={'token' : token})

    
    def __get_markets(self, token):
        return caller.api_call_get('markets', payload={'token' : token})

    
    def __get_market_orders(self, token, market):
        return caller.api_call_get('marketorders',
            payload={
                'token' : token,
                'market_id' : market
            }
        )

    
    def __get_self_orders(self, token, page=None):
        payload={'token' : token}
        if page is not None:
            payload['page'] = page
        return caller.api_call_post('orders',payload=payload)

    
    def __make_trade(self, token, market_id, direction, amount, price):
        return caller.api_call_post('trade',
        payload={
            'token' : token,
            'market_id' : market_id,
            'direction' : direction,
            'amount' : amount,
            'price' : price
        }
    )


    def __cancel_trade(self, token, trade_id):
        return caller.api_call_post('canceltrade',
        payload={
            'token' : token,
            'trade_id' : trade_id
        }
    )


    def __cancel_withdrawal(self, token, txid):
        return caller.api_call_post('cancelwithdrawal',
        payload={
            'token' : token,
            'txid' : txid
        }
    )


    def __get_price(self, market):
        return caller.api_call_get('price',
        payload={
            'market_id' : market
        }
    )


    def __get_address(self, token, currency):
        return caller.api_call_get('address',
        payload={
            'token' : token,
            'currency' : currency
        }
    )


    def __make_withdrawal_crypto(self, token, currency, amount, address):
        return caller.api_call_post('withdraw',
            payload={
                'token' : token,
                'currency' : currency,
                'amount' : amount,
                'instructions' : {'address' : address}
            }
        )


    def __make_withdrawal_fiat(self, token, currency, amount, bsb, account_num, addressee, message=""):
        return caller.api_call_post('withdraw',
            payload={
                'token' : token,
                'currency' : currency,
                'amount' : amount,
                'instructions' : {'message' : message, 'bsb' : bsb, 'account_num' : account_num, 'addressee' : addressee}
            }
        )


    def __get_chart(self, token, market, interval, from_time, to_time, page=0):
        return caller.api_call_get('chart',
            payload={
                'market_id' : market,
                'interval' : interval,
                'from_time' : from_time,
                'to_time' : to_time,
                'page' : page,
                'token' : token
            }
        )


    def __get_market_history(self, token, market_id, page=0):
        return caller.api_call_get('markethistory',
            payload={
                'market_id' : market_id,
                'page' : page,
                'token' : token
            }
        )

    __tkn = ''
