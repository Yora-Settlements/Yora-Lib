# Yora Lib #
Yora Lib is an open-source wrapper library for the Yora Settlements trading API designed to assist programmers in creating automated/algorithmic traders with great simplicity.

The documentation for the Yora public API can be accessed [here](https://api.yora.tech/openapi).

* [Wiki](https://github.com/Yora-Settlements/Yora-Lib/wiki)
* [Getting started](https://github.com/Yora-Settlements/Yora-Lib#getting-started)
* [Making a trade](https://github.com/Yora-Settlements/Yora-Lib#making-a-trade)


## Getting Started ##
To start using the wrapper library, simply create a new file in the root directory and import the Yora.py module and create an API object. 

Note: In all following examples the name ```yora_api``` will be used to refer to the created API object.
```python
import Yora
yora_api = Yora.API('email@email.com', 'password')
```

If your account uses 2FA, set the optional flag in the constructor to True to be prompted for the 2FA code required to access your account.
```python
import Yora
yora_api = Yora.API('email@email.com', 'password', True)
```


## Return Codes ##
All API requests return a [Yora status code](https://github.com/Yora-Settlements/Yora-Lib#getting-started) and a response from the server. If the status code is non zero the resposne will be ```None``` indicating an error with the request.


The library includes an Enum type for these codes to make error codes easier to read and properly handle.

```python
markets_response = yora_api.get_markets()
if markets_response[0] == Yora.StatusCode.ok.value:
    markets = marketResponse[1]
```

Return codes can differ from ```Yora.StatusCode.ok.value```. For example, if the required balance to make a trade is not met the value of ```Yora.StatusCode.insufficient_funds.value``` will be returned instead. It is up to the programmer to check for relevent status codes and determine what actions are to be taken if one is returned.

```python
trade_response = yora_api.trade('GRC/AUD', yora_api.BUY, 100, 0.5)
if trade_response[0] == Yora.StatusCode.insufficient_funds.value:
  handle_error()
```

This is done so the user has complete control over what happens to their program if an unexpected error occurs instead of the library simply exiting the program.


## Making a Trade ##
The library allows to open an order for a market by either the ticker or it's id, the order type is specified by the constants BUY = 0 and SELL = 1, the amount in this example is 100 and for the price of $0.5.

A successful trade will return the trade id and the transaction id inside a dictionary. 
```python
trade_response = yora_api.trade('GRC/AUD', yora_api.BUY, 100, 0.5)
if trade_response[0] == Yora.StatusCode.ok.value:
  trade_details = trade_response[1]
  trade_id = trade_details['trade_id']
  transaction_id = trade_details['tx_id']
```

More information and aditional doccumentation can be found on the [Wiki](https://github.com/Yora-Settlements/Yora-Lib#getting-started).
