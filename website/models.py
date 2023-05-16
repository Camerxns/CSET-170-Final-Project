from sqlalchemy import CheckConstraint, Column, DECIMAL, DateTime, ForeignKey, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from . import db


Base = db.Model
metadata = Base.metadata


class Chat(Base):
    __tablename__ = 'Chats'

    chat_id = Column(Integer, primary_key=True, unique=True)

    users = relationship('User', secondary='Chat_Users')


class Product(Base):
    __tablename__ = 'Products'

    product_id = Column(Integer, primary_key=True, unique=True)
    title = Column(String(40), nullable=False)
    description = Column(Text, nullable=False)
    product_image = Column(String(255), nullable=False)
    category = Column(String(20), nullable=False)


class User(Base, UserMixin):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(60), nullable=False)
    username = Column(String(20), nullable=False)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String(40), nullable=False)

    def account_type(self):
        admin = Admin.query.filter_by(user_id=self.user_id).first()
        if admin:
            return "ADMIN"
        else:
            vendor = Vendor.query.filter_by(user_id=self.user_id).first()
            if vendor:
                return "VENDOR"
            else:
                customer = Customer.query.filter_by(user_id=self.user_id).first()
                if customer:
                    return "CUSTOMER"
                else:
                    return None
    
    @property
    def id(self):
        return self.user_id

    
class Admin(Base):
    __tablename__ = 'Admins'

    admin_id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(ForeignKey('Users.user_id'), nullable=False, unique=True)

    user = relationship('User')


class ChatMessage(Base):
    __tablename__ = 'Chat_Messages'

    chat_message_id = Column(Integer, primary_key=True, unique=True)
    chat_id = Column(ForeignKey('Chats.chat_id'), nullable=False, index=True)
    user_id = Column(ForeignKey('Users.user_id'), nullable=False, index=True)
    message_date = Column(DateTime, nullable=False,
                          server_default=text("CURRENT_TIMESTAMP"))
    message = Column(Text, nullable=False)

    chat = relationship('Chat')
    user = relationship('User')


t_Chat_Users = Table(
    'Chat_Users', metadata,
    Column('chat_id', ForeignKey('Chats.chat_id'), nullable=False, index=True),
    Column('user_id', ForeignKey('Users.user_id'), nullable=False, index=True)
)


class Complaint(Base):
    __tablename__ = 'Complaints'

    complaint_id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(ForeignKey('Users.user_id'), nullable=False, index=True)
    admin_id = Column(ForeignKey('Users.user_id'), index=True)
    complaint_date = Column(DateTime, nullable=False,
                            server_default=text("CURRENT_TIMESTAMP"))
    title = Column(String(40), nullable=False)
    description = Column(Text, nullable=False)
    demand = Column(Text, nullable=False)
    status = Column(String(20), nullable=False,
                    server_default=text("'pending'"))

    admin = relationship(
        'User', primaryjoin='Complaint.admin_id == User.user_id')
    user = relationship(
        'User', primaryjoin='Complaint.user_id == User.user_id')


class Customer(Base):
    __tablename__ = 'Customers'

    customer_id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(ForeignKey('Users.user_id'), nullable=False, unique=True)

    user = relationship('User')


class Review(Base):
    __tablename__ = 'Reviews'
    __table_args__ = (
        CheckConstraint('((`rating` >= 1) and (`rating` <= 5))'),
    )

    review_id = Column(Integer, primary_key=True, unique=True)
    product_id = Column(ForeignKey('Products.product_id'),
                        nullable=False, index=True)
    user_id = Column(ForeignKey('Users.user_id'), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    review_date = Column(DateTime, nullable=False,
                         server_default=text("CURRENT_TIMESTAMP"))
    message = Column(Text)
    image = Column(String(255))

    product = relationship('Product')
    user = relationship('User')


class Vendor(Base):
    __tablename__ = 'Vendors'

    vendor_id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(ForeignKey('Users.user_id'), nullable=False, unique=True)

    user = relationship('User')


class Cart(Base):
    __tablename__ = 'Carts'

    cart_id = Column(Integer, primary_key=True, unique=True)
    customer_id = Column(ForeignKey('Customers.customer_id'),
                         nullable=False, unique=True)

    customer = relationship('Customer')


class VendorProduct(Base):
    __tablename__ = 'Vendor_Products' 

    vendor_product_id = Column(Integer, primary_key=True, unique=True)
    product_id = Column(ForeignKey('Products.product_id'),
                        nullable=False, index=True)
    vendor_id = Column(ForeignKey('Vendors.vendor_id'),
                       nullable=False, index=True)
    qty = Column(Integer, nullable=False, server_default=text("'1'"))
    price = Column(DECIMAL(9, 2), nullable=False,
                   server_default=text("'0.00'"))
    warranty_length = Column(Integer)

    product = relationship('Product')
    vendor = relationship('Vendor')


class CartItem(Base):
    __tablename__ = 'Cart_Items'

    cart_item_id = Column(Integer, primary_key=True, unique=True)
    cart_id = Column(ForeignKey('Carts.cart_id'), nullable=False, index=True)
    product_id = Column(ForeignKey('Products.product_id'),
                        nullable=False, index=True)
    qty = Column(Integer, nullable=False, server_default=text("'1'"))
    color = Column(String(40))
    size = Column(String(20))

    cart = relationship('Cart')
    product = relationship('Product')


class Discount(Base):
    __tablename__ = 'Discounts'

    discount_id = Column(Integer, primary_key=True, unique=True)
    vendor_product_id = Column(ForeignKey(
        'Vendor_Products.vendor_product_id'), nullable=False, index=True)
    discount_price = Column(DECIMAL(9, 2), nullable=False,
                            server_default=text("'0.00'"))
    from_date = Column(DateTime, nullable=False,
                       server_default=text("CURRENT_TIMESTAMP"))
    to_date = Column(DateTime, nullable=False)

    vendor_product = relationship('VendorProduct')


class Order(Base):
    __tablename__ = 'Orders'

    order_id = Column(Integer, primary_key=True, unique=True)
    customer_id = Column(ForeignKey('Customers.customer_id'),
                         nullable=False, index=True)
    cart_id = Column(ForeignKey('Carts.cart_id'), nullable=False, index=True)
    order_date = Column(DateTime, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    status = Column(String(40), nullable=False,
                    server_default=text("'pending'"))

    cart = relationship('Cart')
    customer = relationship('Customer')


t_Vendor_Product_Colors = Table(
    'Vendor_Product_Colors', metadata,
    Column('vendor_product_id', ForeignKey(
        'Vendor_Products.vendor_product_id'), nullable=False, index=True),
    Column('color', String(40), nullable=False)
)


t_Vendor_Product_Sizes = Table(
    'Vendor_Product_Sizes', metadata,
    Column('vendor_product_id', ForeignKey(
        'Vendor_Products.vendor_product_id'), nullable=False, index=True),
    Column('size', String(20), nullable=False)
)


class OrderItem(Base):
    __tablename__ = 'Order_Items'

    order_item_id = Column(Integer, primary_key=True, unique=True)
    order_id = Column(ForeignKey('Orders.order_id'),
                      nullable=False, index=True)
    vendor_product_id = Column(ForeignKey(
        'Vendor_Products.vendor_product_id'), nullable=False, index=True)
    qty = Column(Integer)
    color = Column(String(40))
    size = Column(String(20))

    order = relationship('Order')
    vendor_product = relationship('VendorProduct')