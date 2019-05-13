import json
import requests
import sys, os
import time
API_URL = "http://localhost:5000"

def prompt_from_schema(ctrl):
    """ Function used to get inputs from the user based on the schema
        Based on the function introduced in exercise 4.
        Takes in the Mason control for POST/PUT request
    """
    body = {}
    if "schema" in ctrl:
        schema = ctrl["schema"]
    required = schema["required"]
    # field is the variable, props is the object under it which contains description and type.
    for field, props in schema["properties"].items():
        if field in required:
            inputvalue = input(props["description" + ":"]) #
            if inputvalue is not None:
                inputvalue = convert_value(inputvalue, props)
            body[field] = inputvalue

    return body

def convert_value(value, schema_props):
    """ Function used to convert user input strings to right format.
        Based on the function introduced in exercise 4
    """
    if schema_props["type"] == "number":
            try:
                value = int(value)
            except ValueError:
                value = float(value)
    if schema_props["type"] == "integer":
        value = int(value)
    return value

def submit_data(s, ctrl, data, headers):
    """ Function used for sending post and put requests.
        Based on the function introduced in exercise 4
        takes in session, mason control, data and headers
    """
    resp = s.request(
        ctrl["method"],
        API_URL + ctrl["href"],
        data=json.dumps(data),
        headers = headers)
    return resp

def mainmenu():
    """ This menu has has option to go for price action or account related part of the api """
    os.system("clear")
    print("Hello, this is the client application for Cryptotrading API")
    print("Select (1) if you want to use existing account")
    print("Select (2) if you want to make a new account")
    print("Select (3) if you want to get the most recent trade")

    while True:
        choice = int(input("Give your selection please: "))
        if choice == 1:
            #positionsmenu("79z47uUikMoPe2eADqfJzRBu")
            ordersmenu("79z47uUikMoPe2eADqfJzRBu")
            pass
        if choice == 2:
            # prompt from account schema
            pass
        if choice == 3:
            priceactionmenu()



def priceactionmenu():
    """ This menu has option to get price action data"""
    os.system("clear")
    print("Input a trading pair to get its most recent pair or press (q) to go back to mainmenu")
    try:
        str = input()
        if str == 'q':
            mainmenu()
        else:
            connected = True
            prev_response = {}
            while(connected == True):
                response = requests.get(API_URL + '/priceaction/', params={"symbol" : str})
                response = json.loads(response.text)

                print("PRICE: {}, SIZE: {}, SIDE: {}".format(response["price"], response["size"], response["side"]))
                time.sleep(2)
    except TypeError:
        print("")


def create_account():
    """ Creates account by prompting from account schema and
        submitting data, might need some parameters like session idk.
    """
    pass

def accountmenu():
    """ Option to delete account
        Options to go for orders menu or to positions menu
        Option to go to main menu (log out)
    """
    pass

def positionsmenu(apikey):
    """ get positions, give functionality to select one or to go back to accountmenu

    """
    response = json.loads(requests.get(API_URL + "/accounts/" + apikey + "/positions/",
                            headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}).text)

    positions = response["items"]
    for position in positions:
        if position["leverage"] == 0:
            leverage = "Cross"
        else:
            leverage = position["leverage"]
        print("Symbol: {}, Size {}, Leverage: {}, Entry price: {}, Liquidation price : {}".format(position["symbol"],
                                                                                                    position["size"],
                                                                                                    leverage,
                                                                                                    position["avgEntryPrice"],
                                                                                                    position["liquidationPrice"]))

    print("Select position to modify by entering position symbol or enter(q) to return:")
    str = input()
    if str == 'q':
        mainmenu()
    positionmenu(str, apikey)

    pass

def positionmenu(symbol, apikey):
    """ Show one position, give functionality to change leverage or to go back to positionsmenu

    """
    response = json.loads(requests.get(API_URL + "/accounts/" + apikey + "/positions/" + symbol + "/",
                            headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}).text)

    if response["leverage"] == 0:
        leverage = "Cross"
    else:
        leverage = response["leverage"]
    print("Symbol: {}, Size {}, Leverage: {}, Entry price: {}, Liquidation price : {}".format(response["symbol"],
                                                                                                response["size"],
                                                                                                leverage,
                                                                                                response["avgEntryPrice"],
                                                                                                response["liquidationPrice"]))
    print("Input desired leverage for the position:")
    try:
        float_leverage = 0.0
        leverage = input()
        if leverage == 'Cross':
            float_leverage = 0.0
        else:
            float_leverage = float(leverage)

        response = requests.patch(API_URL + "/accounts/" + apikey + "/positions/" + symbol + "/",
                                    headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"},
                                    json={"leverage": float_leverage})

    except ValueError:
        print("Invalid type: leverage must be a float or 'Cross'")

def ordersmenu(apikey):
    """ Options for adding new order and for selecting one and deleting it or back to account """


    while True:
        orders = json.loads(requests.get(API_URL + "/accounts/" + apikey + "/orders/",
                                    headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}).text)

        print("\n")
        for order in orders["items"]:
            print("Order ID: {}, Symbol: {}, Price: {}, Size: {}, Side: {}".format(order["id"], order["symbol"], order["price"], order["size"], order["side"]))

        print("\nSelect order to modify by entering the order ID, create a new order by entering(c) or enter(q) to return:")

        str = input()

        if not next((order for order in orders["items"] if order['id'] == str), None) and str != 'c':
            print("\nInvalid Order ID given\n\n")
        else:
            ordermenu(str, apikey)

        if str == 'q':
            break
        if str == 'c':
            createorder(apikey)





def ordermenu(id,apikey):
    """ Show one order, option to delete it or to go back to ordersmenu  """
    order = json.loads(requests.get(API_URL + "/accounts/" + apikey + "/orders/" + id + "/",
                            headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}).text)

    print("Symbol: {}, Price: {}, Size: {}, Side: {}".format( order["symbol"], order["price"], order["size"], order["side"]))

    print("Enter (d) to delete, or (q) to return:")
    while True:
        str = input()
        if str == 'q':
            break
        if str == 'd':
            deleteorder(id, apikey)
            break

def createorder(apikey):
    try:
        print("Input order symbol:")
        symbol = input()
        print("Input order price:")
        price = float(input())
        print("Input order size:")
        size = int(input())
        print("Input order side (Buy/Sell):")
        side = input()
        response = requests.post(API_URL + "/accounts/" + apikey + "/orders/",
                                 headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"},
                                 json={"symbol" : symbol, "price" : price, "size" : size, "side" : side})
        print(response.text)
    except TypeError:
        print("Price must be float, size must be integer")

def deleteorder(id, apikey):
    response = requests.delete(API_URL + "/accounts/" + apikey + "/orders/" + id + "/",
                    headers={"api_secret" : "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"})
    if response.status_code == 204:
        print("Order succesfully deleted.\n\n")

def main():
    mainmenu()
    # vois mahollisesti käyttää ilma sessionia nii ois simppelimpi ehkä, emt
    with requests.Session() as s:
        resp = s.get(API_URL)
        body = resp.json()


if __name__ == '__main__':
    main()
