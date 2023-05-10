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

insert into Users (name, username, email, password)
VALUES ("Gabriel", "gabe_is_cool23", "gabrielnewman23@gmail.com", "pbkdf2:sha256:260000$KqXkWOfYtbjLjTd4$69b9d203971cee50195b022963e8d753d12f5cc73e93b892a19685a4884bf8cc"),
		("Tyler", "tyler21", "tyler23@gmail.com", "pbkdf2:sha256:260000$KqXkWOfYtbjLjTd4$69b9d203971cee50195b022963e8d753d12f5cc73e93b892a19685a4884bf8cc");

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

insert into customers(user_id) values(1);
insert into customers(user_id) values(2);

CREATE TABLE IF NOT EXISTS Products (
	product_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    title VARCHAR(40) NOT NULL,
    description TEXT NOT NULL,
    product_image VARCHAR(255) NOT NULL,
    category VARCHAR(20) NOT NULL,
    PRIMARY KEY(product_id)
);

insert into products(title, description, product_image, category)
VALUES("Country Rustic Distressed Wood Bedframe1",
		"This clean design met with a retro style turns country into country sheek. No box spring required. ",
        "https://i.pinimg.com/originals/2e/ad/99/2ead99a8db781a700a5d1afb7e402e19.jpg", "Bedframes"),
	  ("Natural Mindi Side Table with Drawer",
		"Add a touch of rustic charm to your bedroom 
        with this Unfinished Natural Mindi Wood Side Table with Drawer. 
        The modern silhouette of this farmhouse-inspired nightstand 
        is both visually pleasing and functional, 
        providing ample space for all your before-bed necessities.",
        "https://ak1.ostkcdn.com/images/products/is/images/direct/5db6dac5b56fd7b10e390b62c9f4eb74b1db513d/Unfinished-Natural-Mindi-Wood-Side-Table-with-Drawer.jpg", 
        "End table");


CREATE TABLE IF NOT EXISTS Vendor_Products (
	vendor_product_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    product_id INT NOT NULL,
    vendor_id INT NOT NULL,
    qty INT NOT NULL DEFAULT 1,
    price DECIMAL(9,2) NOT NULL DEFAULT 0.00,
    warranty_length DATE DEFAULT NULL,
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
    product_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL,
    review_date DATETIME NOT NULL DEFAULT NOW(),
    message TEXT DEFAULT NULL,
    image VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY(review_id),
    FOREIGN KEY(product_id) REFERENCES Products(product_id),
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

insert into carts (customer_id) values(1), (2);

CREATE TABLE IF NOT EXISTS Cart_Items(
	cart_item_id INT NOT NULL UNIQUE AUTO_INCREMENT,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    qty INT NOT NULL DEFAULT 1,
    color VARCHAR(40) DEFAULT NULL,
    size VARCHAR(20) DEFAULT NULL,
    PRIMARY KEY(cart_item_id),
    FOREIGN KEY(cart_id) REFERENCES Carts(cart_id),
    FOREIGN KEY(product_id) REFERENCES Products(product_id)
);

insert into cart_items(cart_id, product_id, qty, color, size)
values	(1, 1, 1, "Vintage Brown", "King"),
		(2, 2, 1, "Natural", "1-Drawer");


select name, user_id, cart_id, product_id, title from users natural join products natural join cart_items;

-- select * from carts join cart_items join products using(product_id) where customer_id = current_user.user_id;

select * from carts join cart_items join products using(product_id);

select * from users;

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
    product_id INT NOT NULL,
    qty INT,
    color VARCHAR(40),
    size VARCHAR(20),
    PRIMARY KEY(order_item_id),
    FOREIGN KEY(order_id) REFERENCES Orders(order_id),
    FOREIGN KEY(product_id) REFERENCES Products(product_id)
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


# DESC Users;

# SELECT * FROM Users;

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
	("Framework Laptop", "The best laptop in the world!", "no_img_for_ye", "computers"),
    ("IPhone 12 Pro", "You wanted to be part of the apple ecosystem *shrug*", "no_img_for_ye", "phones"),
    ("Couch", "One of the best couches in North America! With over 4 million of these couches sold, you can be sure you will be satified!", "no_img_for_ye", "couches");

    
INSERT INTO Vendor_Products (product_id, vendor_id, qty, price, warranty_length) VALUES
	((SELECT product_id FROM Products WHERE title="Framework Laptop"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="jrhysiter12@gmail.com")), 4, 32.66, NULL),
    ((SELECT product_id FROM Products WHERE title="IPhone 12 Pro"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="jrhysiter12@gmail.com")), 87, 999.99, '2023-08-12'),
    ((SELECT product_id FROM Products WHERE title="Framework Laptop"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="breads23@gmail.com")), 4, 32.66, NULL),
    ((SELECT product_id FROM Products WHERE title="Couch"), (SELECT vendor_id FROM Vendors WHERE user_id=(SELECT user_id FROM Users WHERE email="breads23@gmail.com")), 7, 65.23, NULL);

DESC Vendor_Product_Colors;

SELECT * FROM Vendor_Products;

INSERT INTO Vendor_Product_Colors (vendor_product_id, color) VALUES
	(1, "Black"),
    (1, "Blue"),
    (1, "Orange"),
    (3, "Orange"),
    (3, "Black"),
    (2, "Silver"),
	(2, "Rose Gold");
    
DESC Vendor_Product_Sizes;
INSERT INTO Vendor_Product_Sizes (vendor_product_id, size) VALUES
	(1, '13\"'),
	(1, '15\"'),
    (1, '17\"'),
	(2, '15\"'),
    (2, '17\"'),
    (4, 'Large'),
    (4, 'Small');

SELECT color FROM Vendor_Product_Colors WHERE vendor_product_id=(SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id=1 AND product_id=1);

















