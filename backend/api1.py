from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re
import jwt
from functools import wraps
import bcrypt
from price_predictor import price_predictor

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Simple CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": ["http://localhost:3000"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }
     })

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'data'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Anasanas.1'),
            port=os.getenv('DB_PORT', '5432')
        )
        return conn
    except Exception as e:
        print("Database connection error:", str(e))
        return None

def initialize_database():
    """Initialize the database with required tables"""
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                # Create users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                print("Database initialized successfully")
    except Exception as e:
        print("Database initialization error:", str(e))
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# Initialize database when the app starts
initialize_database()

@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')

        # Validate username
        if not username:
            return jsonify({"error": "Username is required"}), 400
        if len(username) < 2:
            return jsonify({"error": "Username must be at least 2 characters long"}), 400

        # Validate email
        if not email:
            return jsonify({"error": "Email is required"}), 400
        if not '@' in email:
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password
        if not password:
            return jsonify({"error": "Password is required"}), 400
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400
        if not any(c.isupper() for c in password):
            return jsonify({"error": "Password must contain at least one uppercase letter"}), 400
        if not any(c.islower() for c in password):
            return jsonify({"error": "Password must contain at least one lowercase letter"}), 400
        if not any(c.isdigit() for c in password):
            return jsonify({"error": "Password must contain at least one number"}), 400

        # Validate password confirmation
        if not confirm_password:
            return jsonify({"error": "Please confirm your password"}), 400
        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Check if username or email already exists
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
                    existing_user = cur.fetchone()
                    if existing_user:
                        return jsonify({"error": "Username or email already exists"}), 400

                    # Hash password
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    
                    # Insert new user
                    cur.execute(
                        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id, username, email",
                        (username, email, hashed_password.decode('utf-8'))
                    )
                    new_user = cur.fetchone()
                    conn.commit()
                    
                    # Generate token
                    token = jwt.encode(
                        {'user_id': new_user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)},
                        app.config['SECRET_KEY']
                    )
                    
                    return jsonify({
                        "message": "Registration successful",
                        "token": token,
                        "user": {
                            "id": new_user['id'],
                            "username": new_user['username'],
                            "email": new_user['email']
                        }
                    }), 201
            except Exception as e:
                print("Database error:", str(e))
                conn.rollback()
                return jsonify({"error": "Database error occurred"}), 500
            finally:
                conn.close()
        else:
            return jsonify({"error": "Database connection failed"}), 500
    except Exception as e:
        print("Registration error:", str(e))
        return jsonify({"error": str(e)}), 500
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Special handler for OPTIONS requests
@app.route('/auth/login', methods=['OPTIONS'])
def login_options():
    response = jsonify({"message": "Preflight accepted"})
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:3000")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # First check if user exists
                cur.execute("""
                    SELECT id, username, email, password 
                    FROM users 
                    WHERE username = %s
                """, (username,))
                
                user = cur.fetchone()
                
                if not user:
                    return jsonify({"error": "Invalid username or password"}), 401
                
                # Verify password
                if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                    return jsonify({"error": "Invalid username or password"}), 401
                
                # Generate token
                token = jwt.encode(
                    {
                        'user_id': user['id'],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                    },
                    app.config['SECRET_KEY'],
                    algorithm='HS256'
                )
                
                return jsonify({
                    "message": "Login successful",
                    "token": token,
                    "user": {
                        "id": user['id'],
                        "username": user['username'],
                        "email": user['email']
                    }
                }), 200
        except Exception as e:
            print("Database error during login:", str(e))
            conn.rollback()
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            conn.close()
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({"error": str(e)}), 500

# 1. ROOT ENDPOINT
@app.route('/')
def api_info():
    """Root endpoint with API information"""
    endpoints = {
        "GET /": "API information",
        "GET /health": "Service health check",
        "GET /products": "List all products (paginated)",
        "GET /products/<id>": "Get single product",
        "POST /products": "Create new product",
        "PUT /products/<id>": "Update product",
        "DELETE /products/<id>": "Delete product",
        "GET /products/search": "Search products"
    }
    return jsonify({
        "message": "Product API Service",
        "version": "1.1",
        "status": "operational",
        "endpoints": endpoints,
        "timestamp": datetime.datetime.now().isoformat()
    })

# 2. HEALTH CHECK (enhanced)
@app.route('/health')
def health_check():
    """Service health check endpoint with detailed diagnostics"""
    try:
        conn = get_db_connection()
        db_status = "connected" if conn else "disconnected"
        
        diagnostics = {
            "status": "healthy" if conn else "degraded",
            "database": db_status,
            "server_time": datetime.datetime.now().isoformat(),
            "python_version": os.sys.version,
            "platform": os.sys.platform
        }
        
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT version()")
                    db_version = cur.fetchone()[0]
                    diagnostics["database_version"] = db_version
                    
                    cur.execute("SELECT COUNT(*) FROM products")
                    product_count = cur.fetchone()[0]
                    diagnostics["product_count"] = product_count
            except Exception as e:
                diagnostics["database_error"] = str(e)
            finally:
                conn.close()
        
        return jsonify(diagnostics)
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500

# 3. GET ALL PRODUCTS (PAGINATED)
@app.route('/products', methods=['GET'])
def get_products():
    """Get all products with pagination"""
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        if page < 1 or per_page < 1:
            return jsonify({"error": "Page and per_page must be positive integers"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get total count
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM scraped_data 
                """)
                total = cur.fetchone()['count']
                
                # Get paginated products
                offset = (page - 1) * per_page
                cur.execute("""
                    SELECT id, title, description, price 
                    FROM scraped_data 
                    ORDER BY id DESC 
                    LIMIT %s OFFSET %s
                """, (per_page, offset))
                products = cur.fetchall()
                
                return jsonify({
                    "page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": (total + per_page - 1) // per_page,
                    "products": products
                })
        except Exception as e:
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                conn.close()
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# 4. GET SINGLE PRODUCT
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, title, description, price 
                FROM scraped_data 
                WHERE id = %s
            """, (product_id,))
            product = cur.fetchone()
            if product:
                return jsonify(product)
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# 5. CREATE PRODUCT
@app.route('/products', methods=['POST'])
def create_product():
    """Create new product with price prediction"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'electronics').strip()
        input_price = data.get('price')  # Get the input price
        
        if not title:
            return jsonify({"error": "Title is required"}), 400

        # Get predicted price using input price
        predicted_price = price_predictor.predict_price(
            title=title,
            description=description,
            category=category,
            input_price=input_price
        )
        
        if predicted_price is None:
            # If prediction fails, use input price or default
            predicted_price = input_price if input_price is not None else 1000.0
            print("Using input price or default due to prediction failure")

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # First check if product already exists
                cur.execute("""
                    SELECT id FROM scraped_data 
                    WHERE title = %s
                """, (title,))
                
                if cur.fetchone():
                    return jsonify({"error": "Product with this title already exists"}), 400

                # Insert new product
                cur.execute("""
                    INSERT INTO scraped_data (title, description, price, category)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, title, description, price, category
                """, (
                    title,
                    description,
                    predicted_price,
                    category
                ))
                
                new_product = cur.fetchone()
                conn.commit()
                
                return jsonify({
                    "message": "Product created successfully",
                    "product": {
                        "id": new_product['id'],
                        "title": new_product['title'],
                        "description": new_product['description'],
                        "price": new_product['price'],
                        "category": new_product['category']
                    }
                }), 201
        except Exception as e:
            print("Database error:", str(e))
            conn.rollback()
            return jsonify({"error": "Database error occurred"}), 500
        finally:
            conn.close()
    except Exception as e:
        print("Error creating product:", str(e))
        return jsonify({"error": str(e)}), 500

# 6. UPDATE PRODUCT
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update existing product"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    if 'price' in data and not isinstance(data['price'], (int, float)):
        return jsonify({"error": "Price must be a number"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check if product exists
            cur.execute("""
                SELECT id FROM scraped_data 
                WHERE id = %s
            """, (product_id,))
            if not cur.fetchone():
                return jsonify({"error": "Product not found"}), 404
            
            # Build dynamic update query
            updates = []
            params = []
            for field in ['title', 'description', 'price']:
                if field in data:
                    updates.append(f"{field} = %s")
                    params.append(data[field])
            
            if not updates:
                return jsonify({"error": "No fields to update"}), 400
                
            params.extend([product_id])
            
            query = f"""
                UPDATE scraped_data
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, title, description, price
            """
            
            cur.execute(query, params)
            updated_product = cur.fetchone()
            conn.commit()
            
            return jsonify({
                "message": "Product updated successfully",
                "product": updated_product
            })
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# 7. DELETE PRODUCT
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cur:
            # Check if product exists
            cur.execute("""
                SELECT id FROM scraped_data 
                WHERE id = %s
            """, (product_id,))
            if not cur.fetchone():
                return jsonify({"error": "Product not found"}), 404
            
            cur.execute("DELETE FROM scraped_data WHERE id = %s", (product_id,))
            conn.commit()
            
            return jsonify({
                "message": "Product deleted successfully"
            }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# 8. SEARCH PRODUCTS
@app.route('/products/search', methods=['GET'])
def search_products():
    """Search products by name or description"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Search query parameter 'q' is required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            search_term = f"%{query}%"
            cur.execute("""
                SELECT id, title, description, 
                FROM scraped_data 
                WHERE title ILIKE %s OR description ILIKE %s
                LIMIT 50
            """, (search_term, search_term))
            products = cur.fetchall()
            
            return jsonify({
                "query": query,
                "count": len(products),
                "products": products
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Configuration:")
    print(f"  Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  Database: {os.getenv('DB_NAME', 'data')}")
    print(f"  User: {os.getenv('DB_USER', 'postgres')}")
    print(f"  Port: {os.getenv('DB_PORT', '5432')}")
    print("  (Password hidden for security)")
    app.run(debug=True)