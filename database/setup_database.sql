CREATE DATABASE IF NOT EXISTS CSET_180_FINAL_PROJECT;
USE CSET_180_FINAL_PROJECT;

DROP TABLE IF EXISTS Admins;
DROP TABLE IF EXISTS Vendor_Product_Colors;
DROP TABLE IF EXISTS Vendor_Product_Sizes;
DROP TABLE IF EXISTS Discounts;
DROP TABLE IF EXISTS Reviews;
DROP TABLE IF EXISTS Complaints;
DROP TABLE IF EXISTS Cart_Items;
DROP TABLE IF EXISTS Order_Items;
DROP TABLE IF EXISTS Chat_Users;
DROP TABLE IF EXISTS Chat_Messages;
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Carts;
DROP TABLE IF EXISTS Chats;
DROP TABLE IF EXISTS Vendor_Products;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Customers;
DROP TABLE IF EXISTS Vendors;
DROP TABLE IF EXISTS Users;

CREATE TABLE IF NOT EXISTS Users(
	user_id INT UNIQUE NOT NULL AUTO_INCREMENT,
    name VARCHAR(60) NOT NULL,
    username VARCHAR(20) NOT NULL,
    email VARCHAR(40) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS Admins (
	admin_id INT NOT NULL UNIQUE AUTO_INCREMENT,
	user_id INT UNIQUE NOT NULL,
    PRIMARY KEY(admin_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Vendors (
	vendor_id INT NOT NULL UNIQUE AUTO_INCREMENT,
	user_id INT UNIQUE NOT NULL,
    PRIMARY KEY(vendor_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Customers (
	customer_id INT NOT NULL UNIQUE AUTO_INCREMENT,
	user_id INT UNIQUE NOT NULL,
    PRIMARY KEY(customer_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Products (
	product_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    title VARCHAR(40) NOT NULL,
    description TEXT NOT NULL,
    product_image VARCHAR(255) NOT NULL,
    category VARCHAR(20) NOT NULL,
    PRIMARY KEY(product_id)
);

CREATE TABLE IF NOT EXISTS Vendor_Products (
	vendor_product_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    product_id INT NOT NULL,
    vendor_id INT NOT NULL,
    qty INT NOT NULL DEFAULT 1,
    price DECIMAL(9,2) NOT NULL DEFAULT 0.00,
    warranty_length DATE DEFAULT NULL,
    date_created DATETIME NOT NULL DEFAULT NOW(),
    PRIMARY KEY(vendor_product_id),
    FOREIGN KEY(product_id) REFERENCES Products(product_id),
    FOREIGN KEY(vendor_id) REFERENCES Vendors(vendor_id)
);

CREATE TABLE IF NOT EXISTS Vendor_Product_Colors (
	vendor_product_id INT NOT NULL,
    color VARCHAR(40) NOT NULL,
    FOREIGN KEY(vendor_product_id) REFERENCES Vendor_Products(vendor_product_id)
);

CREATE TABLE IF NOT EXISTS Vendor_Product_Sizes (
	vendor_product_id INT NOT NULL,
    size VARCHAR(20) NOT NULL,
    FOREIGN KEY(vendor_product_id) REFERENCES Vendor_Products(vendor_product_id)
);

CREATE TABLE IF NOT EXISTS Discounts (
	discount_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    vendor_product_id INT NOT NULL,
    discount_price DECIMAL(9,2) NOT NULL DEFAULT 0.00,
    from_date DATETIME NOT NULL DEFAULT NOW(),
    to_date DATETIME NOT NULL,
    PRIMARY KEY(discount_id),
    FOREIGN KEY(vendor_product_id) REFERENCES Vendor_Products(vendor_product_id)
);

CREATE TABLE IF NOT EXISTS Reviews (
	review_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    vendor_product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL,
    review_date DATETIME NOT NULL DEFAULT NOW(),
    message TEXT DEFAULT NULL,
    image VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY(review_id),
    FOREIGN KEY(vendor_product_id) REFERENCES Vendor_Products(vendor_product_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    CHECK (rating >= 1 AND rating <= 5)
);

CREATE TABLE IF NOT EXISTS Complaints (
	complaint_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    user_id INT NOT NULL,
    admin_id INT DEFAULT NULL,
    complaint_date DATETIME NOT NULL DEFAULT NOW(),
    title VARCHAR(40) NOT NULL,
    description TEXT NOT NULL,
    demand TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    PRIMARY KEY(complaint_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY(admin_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Carts (
	cart_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    customer_id INT NOT NULL UNIQUE,
    PRIMARY KEY(cart_id),
    FOREIGN KEY(customer_id) REFERENCES Customers(customer_id)
);

CREATE TABLE IF NOT EXISTS Cart_Items(
	cart_item_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    cart_id INT NOT NULL,
    vendor_product_id INT NOT NULL,
    qty INT NOT NULL DEFAULT 1,
    color VARCHAR(40) DEFAULT NULL,
    size VARCHAR(20) DEFAULT NULL,
    PRIMARY KEY(cart_item_id),
    FOREIGN KEY(cart_id) REFERENCES Carts(cart_id),
    FOREIGN KEY(vendor_product_id) REFERENCES Vendor_Products(vendor_product_id)
);

CREATE TABLE IF NOT EXISTS Orders(
	order_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    customer_id INT NOT NULL,
    cart_id INT NOT NULL,
    order_date DATETIME NOT NULL DEFAULT NOW(),
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    PRIMARY KEY(order_id),
    FOREIGN KEY(customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY(cart_id) REFERENCES Carts(cart_id)
);

CREATE TABLE IF NOT EXISTS Order_Items(
	order_item_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    order_id INT NOT NULL,
    vendor_product_id INT NOT NULL,
    qty INT,
    color VARCHAR(40),
    size VARCHAR(20),
    PRIMARY KEY(order_item_id),
    FOREIGN KEY(order_id) REFERENCES Orders(order_id),
    FOREIGN KEY(vendor_product_id) REFERENCES Vendor_Products(vendor_product_id)
);

CREATE TABLE IF NOT EXISTS Chats(
	chat_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    PRIMARY KEY(chat_id)
);

CREATE TABLE IF NOT EXISTS Chat_Users(
	chat_id INT NOT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY(chat_id) REFERENCES Chats(chat_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
);

CREATE TABLE IF NOT EXISTS Chat_Messages(
	chat_message_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    chat_id INT NOT NULL,
    user_id INT NOT NULL,
    message_date DATETIME NOT NULL DEFAULT NOW(),
    message TEXT NOT NULL,
    PRIMARY KEY(chat_message_id),
    FOREIGN KEY(chat_id) REFERENCES Chats(chat_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
);

INSERT INTO Users (name, username, email, password) VALUES
	("Justin Koch", "Code12", "jdkoch2855@gmail.com", "pbkdf2:sha256:600000$wv32rCrCar3DBGgk$5d1f75a96ba5cd1e8ec9c5fea90946767e1b35d6e8df55c190d570528af5690f"),
    ("Hank Williams", "Hank", "hankwilliams86@gmail.com", "pbkdf2:sha256:600000$wv32rCrCar3DBGgk$5d1f75a96ba5cd1e8ec9c5fea90946767e1b35d6e8df55c190d570528af5690f"),
    ("Jack Rhysiter", "Hackerman", "jrhysiter12@gmail.com", "pbkdf2:sha256:600000$wv32rCrCar3DBGgk$5d1f75a96ba5cd1e8ec9c5fea90946767e1b35d6e8df55c190d570528af5690f"),
    ("Bart Reeds", "BartReeds23", "breads23@gmail.com", "pbkdf2:sha256:600000$wv32rCrCar3DBGgk$5d1f75a96ba5cd1e8ec9c5fea90946767e1b35d6e8df55c190d570528af5690f");
    
INSERT INTO Customers (user_id) VALUES
	((SELECT user_id FROM Users WHERE email="jdkoch2855@gmail.com"));
    
INSERT INTO Admins (user_id) VALUES
	((SELECT user_id FROM Users WHERE email="hankwilliams86@gmail.com"));

INSERT INTO Vendors (user_id) VALUES
	((SELECT user_id FROM Users WHERE email="jrhysiter12@gmail.com"));    

INSERT INTO Vendors (user_id) VALUES
	((SELECT user_id FROM Users WHERE email="breads23@gmail.com"));


INSERT INTO Products (title, description, product_image, category) VALUES
	("Framework Laptop", "The best laptop in the world!", "framework-laptop.png", "computers"),
    ("IPhone 12 Pro", "You wanted to be part of the apple ecosystem *shrug*", "no_img_for_ye", "phones"),
    ("Couch", "One of the best couches in North America! With over 4 million of these couches sold, you can be sure you will be satified!", "no_img_for_ye", "couches");

    
INSERT INTO Vendor_Products (product_id, vendor_id, qty, price, warranty_length) VALUES
	((SELECT product_id FROM Products WHERE title="Framework Laptop"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="jrhysiter12@gmail.com")), 4, 32.66, NULL),
    ((SELECT product_id FROM Products WHERE title="IPhone 12 Pro"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="jrhysiter12@gmail.com")), 87, 999.99, '2023-08-12'),
    ((SELECT product_id FROM Products WHERE title="Framework Laptop"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="breads23@gmail.com")), 4, 29.95, NULL),
    ((SELECT product_id FROM Products WHERE title="Couch"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="breads23@gmail.com")), 7, 65.23, NULL);

INSERT INTO Vendor_Product_Colors (vendor_product_id, color) VALUES
	(1, "Black"),
    (1, "Blue"),
    (1, "Orange"),
    (3, "Orange"),
    (3, "Black"),
    (2, "Silver"),
	(2, "Rose Gold");
    
INSERT INTO Vendor_Product_Sizes (vendor_product_id, size) VALUES
	(1, '13\"'),
	(1, '15\"'),
    (1, '17\"'),
	(2, '15\"'),
    (2, '17\"'),
    (4, 'Large'),
    (4, 'Small');

INSERT INTO Reviews(vendor_product_id, user_id, rating, message, image) VALUES
	(1, 1, 3, "Great laptop! I've been able to upgrade it! A wonder for laptops.", "framework-internals.jpg");

INSERT INTO Complaints (user_id, title, description, demand) VALUES
	(1, "REFUND ME", "I purchased a couch 24 days ago, and it still hasn't arrived!", "REFUND");


# DESC Carts;
INSERT INTO Carts (customer_id) VALUES (1);


# DESC Cart_Items;
INSERT INTO Cart_Items (cart_id, vendor_product_id, qty, color, size) VALUES
	(1, 1, 2, "Orange", '15"');


# DESC Orders;
INSERT INTO Orders (customer_id, cart_id) VALUES
	(1, 1);
    

# DESC Order_Items;
INSERT INTO Order_Items (order_id, vendor_product_id, qty, color, size) VALUES
	(1, 1, 2, "Orange", '15"');

# SELECT * FROM Order_Items WHERE order_id = LAST_INSERT_ID();
SELECT * FROM Orders;
SELECT * FROM Order_Items WHERE order_id=2;































