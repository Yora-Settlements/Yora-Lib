# Yora Lib #
Yora Lib is an open-source wrapper library for the Yora Settlements trading API designed to assist programmers in creating automated/algorithmic traders with great simplicity.

The documentation for the Yora public API can be accessed [here](https://api.yora.tech/openapi).

* [Wiki](https://github.com/Yora-Settlements/Yora-Lib/wiki/)
* [Getting started](https://github.com/Yora-Settlements/Yora-Lib#getting-started)
* [API Responses](https://github.com/Yora-Settlements/Yora-Lib#api-responses)
* [Making a trade](https://github.com/Yora-Settlements/Yora-Lib#making-a-trade)


## Getting Started ##
A [Yora account](https://yora.tech/) is required to use the library along with a generated API token.

> An API token can be generated from Account Settings > Logged-in Devices > Generate API token


To start using the wrapper library, simply create a new file in the root directory and import the Yora.py module and create an API object. 

> Note: In all following examples the name ```yora_api``` will be used to refer to the created API object.
```python
import Yora
yora_api = Yora.API('API_TOKEN')
```

## API Responses ##
All API requests return a [Yora status code](https://github.com/Yora-Settlements/Yora-Lib/wiki/Yora-Status-Code) and a response from the server. If the status code is non zero the resposne will be ```None``` indicating an error with the request. The Yora module includes a `StatusCode` Enum to make it easier to work with.

> A list of status codes along with their Enum name are listed in the [Wiki](https://github.com/Yora-Settlements/Yora-Lib/wiki/Yora-Status-Code)

The status code and response are returned together in a tuple, which can be accessed using subscript `status_code = api_response[0]` and `response = api_response[1]`.

### Example
```python
markets_response = yora_api.get_markets()
status_code = markets_response[0]
if status_code == Yora.StatusCode.ok.value:
    markets = marketResponse[1]
```

## Making a Trade ##
The library allows to open an order for a market by either the ticker or it's id, the order type is specified by an Enum within the Yora module `OrderType`, BUY or SELL, the amount in this example is 100 and for the price of $0.5.

A successful trade will return the trade id and the transaction id inside a dictionary. 
```python
trade_response = yora_api.trade('GRC/AUD', Yora.OrderType.BUY, 100, 0.5)
if trade_response[0] == Yora.StatusCode.ok.value:
  trade_details = trade_response[1]
  trade_id = trade_details['trade_id']
  transaction_id = trade_details['tx_id']
```

More information and aditional doccumentation can be found on the [Wiki](https://github.com/Yora-Settlements/Yora-Lib/wiki/Yora-Lib).
