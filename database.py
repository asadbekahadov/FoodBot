import pymysql



class Database:
    def __init__(self, 
                name: str, 
                user: str, 
                password: str,
                port: int,
                host: str):
        self.db_name = name
        self.db_user = user
        self.db_password = password
        self.db_port = port
        self.db_host = host
    
    def connection(self):
        return pymysql.connect(
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
        )
    
    def execute(self, 
                sql: str, 
                params: tuple = None, 
                commit: bool = False, 
                fetchall: bool = False, 
                fetchone: bool = False):
        if not params:
            params = ()
        
        db = self.connection()
        cursor = db.cursor()
        
        cursor.execute(sql, params)
        data = None
        
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        if commit:
            db.commit()
        
        db.close()
        
        return data
    
    def create_user_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Users(
                id INT PRIMARY KEY AUTO_INCREMENT,
                telegram_id INT NOT NULL UNIQUE,
                fullname VARCHAR(255)
            )
        """
        self.execute(sql, commit=True)
    
    def create_categories_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Categories(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255),
                
                CONSTRAINT unique_category_name UNIQUE(name)
            )
        """
        self.execute(sql, commit=True)
    
    def create_products_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Products(
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(12, 2) NOT NULL,
                category INT NOT NULL, 
                image_path VARCHAR(255),
                description_path VARCHAR(255),
                
                CONSTRAINT unique_product_name UNIQUE(name),
                CONSTRAINT category_foreign_key FOREIGN KEY(category) REFERENCES Categories(id)
            )
        """
        self.execute(sql, commit=True)
    
    def create_cart_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Cart(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                product_price DECIMAL(12, 2) NOT NULL,
                quantity INT NOT NULL,
                total_price DECIMAL(12, 2),
                
                CONSTRAINT check_quantity CHECK(quantity > 0),
                CONSTRAINT user_id_foreign_key FOREIGN KEY(user_id) REFERENCES Users(id)
            )
        """
        self.execute(sql, commit=True)      
        '''
                                Cart
        id  user_id     product_name    product_price   quantity    total_price
        1   1           Lavash          19 000          1           19 000
        2   1           Burger          21 000          2           42 000
        3   2           Coca-cola 0.5   6 000           2           12 000
        4   2           Lavash          19 000          2           38 000
        '''  
    
    def create_orders_history_table(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Orders(
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT REFERENCES Users(id),
                product_name VARCHAR(255) NOT NULL,
                quantity INT NOT NULL,
                total_price DECIMAL(12, 2)
            )
        """
        self.execute(sql, commit=True)


    def register_user(self, telegram_id, fullname):
        sql = """
            INSERT INTO Users(telegram_id, fullname) 
            VALUES (%s, %s)
        """
        self.execute(sql, (telegram_id, fullname), commit=True)

    def register_product_in_cart(self, user_id, product_name, product_price, quantity):
        sql = """
            INSERT INTO Cart (user_id, product_name, product_price, quantity)
            VALUES (%s, %s, %s, %s)
        """
        self.execute(sql, (user_id, product_name, product_price, quantity), commit=True)

    def get_categories(self):
        sql = """
            SELECT * FROM Categories
            ORDER BY id
        """
        return self.execute(sql, fetchall=True)
    
    def get_products(self, category_id):
        sql = """
            SELECT * FROM Products
            WHERE category = %s
            ORDER BY id
        """
        return self.execute(sql, (category_id,), fetchall=True)
    
    def get_product(self, product_id):
        sql = """
            SELECT * 
            FROM Cart 
            WHERE id = %s
        """
        return self.execute(sql, (product_id,), fetchall=True)

    def get_users_cart(self, user_id):
        sql = """
            SELECT * FROM Cart 
            WHERE user_id = %s
        """
        return self.execute(sql, (user_id,), fetchall=True)
    
    def get_user(self, telegram_id):
        sql = """
            SELECT * FROM Users 
            WHERE telegram_id = %s
        """
        return self.execute(sql, (telegram_id,), fetchone=True)

    def get_product(self, product_id):
        sql = """
            SELECT * FROM Products
            WHERE id = %s
        """
        return self.execute(sql, (product_id,), fetchone=True)
    
    def register_order_history(self, user_id, product_name, quantity, total_price):
        sql = """
            INSERT INTO Orders (user_id, product_name, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """    
        self.execute(sql, (user_id, product_name, quantity, total_price), commit=True)


    def clear_users_cart(self, user_id):
        sql = """
            DELETE FROM Cart
            WHERE User_id = %s
        """
        self.execute(sql, (user_id,), commit=True)
    
db = Database(
    name="fastfood_bot",
    user="root",
    password="qwerty27",
    port=3306,
    host="127.0.0.1"
)

db.create_user_table()
db.create_categories_table()
db.create_products_table()
db.create_cart_table()
db.create_orders_history_table()

    
        
