from database import db, Orders, User

""" tää pitää korjata joskus"""

def main():
    db.create_all()

    #add order to database
    user_1 = User(username="mikkomallikas", api_public="79z47uUikMoPe2eADqfJzRBu",
                    api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd")

    order = Orders(order_id='00000000-0000-0000-0000-000000000000',
                    order_size=1, order_side='Buy',
                    order_symbol="XBTUSD", user=user_1)

    db.session.add(user_1)
    db.session.add(order)
    db.session.commit()

    user = User.query.first()
    order = Orders(order_id='00000000-0000-0000-0000-000dsd000000',
                    order_size=1123, order_side='sell',
                    order_symbol="XBTUSD", user=user)

    db.session.add(order)
    db.session.commit()

    user = User.query.first()
    for order in user.orders:
        print(order.order_id)




    """
    #read database, and print order size
    order1 = Orders.query.first()
    print("Order size of the queried object before the modification is %d\n" % order1.Order_size)

    #modify order size
    modify(order1)
    #print order size again
    order1 = Orders.query.first()
    print("Order size of the queried object after the modification is %d\n" % order1.Order_size)

    ordertest = Orders.query.first()
    delete(ordertest)

    #Deletion, print is None which means that the database is empty
    ordertest = Orders.query.first()
    print("Print of the queried object:")
    print(ordertest)
    print("It is None because the database is empty after deletion of the single model")
    """
if __name__ == '__main__':
    main()
