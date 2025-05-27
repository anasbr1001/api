from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration with explicit defaults
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'dbname': os.getenv('DB_NAME', 'data'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'Anasanas.1'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Establish connection to PostgreSQL database with detailed error handling"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        print(f"✅ Successfully connected to database: {DB_CONFIG['dbname']}")
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nAttempted connection with these parameters:")
        print(f"  Host: {DB_CONFIG['host']}")
        print(f"  Database: {DB_CONFIG['dbname']}")
        print(f"  User: {DB_CONFIG['user']}")
        print(f"  Port: {DB_CONFIG['port']}")
        print("  (Password hidden for security)\n")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected database error: {str(e)}")
        return None

def extract_product_info(url):
    """Extract product info from URL with enhanced error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Enhanced name extraction
        name = None
        for tag in ['h1', 'title']:
            if not name and soup.find(tag):
                name = soup.find(tag).get_text(strip=True)
                if name: break
        
        # Enhanced price extraction
        price = None
        price_patterns = [r'[\d,.]+', r'\$\d+\.\d{2}', r'\d+\.\d{2}\s*€']
        price_elements = soup.find_all(class_=re.compile(r'price|prix|cost|value', re.I))
        
        for elem in price_elements:
            price_text = elem.get_text(strip=True)
            for pattern in price_patterns:
                match = re.search(pattern, price_text)
                if match:
                    try:
                        price = float(match.group().replace(',', ''))
                        break
                    except ValueError:
                        continue
            if price: break
        
        # Enhanced description extraction
        description = None
        desc_elements = soup.find_all(class_=re.compile(r'description|product-desc|detail|info', re.I))
        
        for elem in desc_elements[:3]:  # Check first 3 potential elements
            if elem.get_text(strip=True):
                description = elem.get_text(strip=True)[:500]
                break
        
        return {
            'title': name,
            'price': price,
            'description': description
        }
    except requests.RequestException as e:
        print(f"🌐 Network error extracting product info: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Error extracting product info: {e}")
        return None

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
                    
                    cur.execute("SELECT COUNT(*) FROM scraped_data")
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
    """Get all products with pagination and enhanced error handling"""
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        search = request.args.get('search', default=None, type=str)
        
        if page < 1 or per_page < 1:
            return jsonify({"error": "Page and per_page must be positive integers"}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Base query
                query = "SELECT id, title, description FROM scraped_data"
                count_query = "SELECT COUNT(*) FROM scraped_data"
                params = []
                
                # Add search filter if provided
                if search:
                    search_term = f"%{search}%"
                    query += " WHERE title ILIKE %s OR description ILIKE %s"
                    count_query += " WHERE title ILIKE %s OR description ILIKE %s"
                    params.extend([search_term, search_term])
                
                # Get total count
                cur.execute(count_query, params)
                total = cur.fetchone()['count']
                
                # Add pagination
                offset = (page - 1) * per_page
                query += " LIMIT %s OFFSET %s"
                params.extend([per_page, offset])
                
                # Execute final query
                cur.execute(query, params)
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
                SELECT id, title, description 
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
    """Create new product with optional auto-scraping"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({"error": "Product URL is required"}), 400
    
    # Auto-extract product info if only URL provided
    if 'url' in data and len(data) == 1:
        extracted_data = extract_product_info(data['url'])
        if extracted_data:
            data.update(extracted_data)
        else:
            print("Warning: Could not auto-extract product data")
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check if product already exists
            cur.execute("SELECT id FROM scraped_data WHERE title = %s", (data.get('title'),))
            if cur.fetchone():
                return jsonify({"error": "Product with this title already exists"}), 409
            
            # Insert new product
            cur.execute("""
                INSERT INTO scraped_data (title, description)
                VALUES (%s, %s, %s)
                RETURNING id, title, description 
            """, (
                data.get('title'),
                data.get('description'),
                
            ))
            
            new_product = cur.fetchone()
            conn.commit()
            
            return jsonify({
                "message": "Product created successfully",
                "product": new_product,
                "auto_filled": 'title' not in data or 'description' not in data
            }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# 6. UPDATE PRODUCT
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update existing product"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # First check if product exists
            cur.execute("SELECT id FROM scraped_data WHERE id = %s", (product_id,))
            if not cur.fetchone():
                return jsonify({"error": "Product not found"}), 404
            
            # Build dynamic update query
            updates = []
            params = []
            for field in ['title', 'description']:
                if field in data:
                    updates.append(f"{field} = %s")
                    params.append(data[field])
            
            if not updates:
                return jsonify({"error": "No fields to update"}), 400
                
            params.append(product_id)
            
            query = f"""
                UPDATE scraped_data
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, title, description
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
            cur.execute("SELECT id FROM scraped_data WHERE id = %s", (product_id,))
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

def initialize_database():
    """Initialize the database with detailed setup"""
    print("\n🔧 Initializing database...")
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'scraped_data'
                    )
                """)
                table_exists = cur.fetchone()[0]
                
                if not table_exists:
                    print("🛠 Creating scraped_data table...")
                    cur.execute("""
                        CREATE TABLE scraped_data (
                            id SERIAL PRIMARY KEY,
                            title VARCHAR(255),
                            description TEXT,
                            
                        )
                    """)
                    conn.commit()
                    print("✅ scraped_data table created")
                else:
                    print("ℹ️ scraped_data table already exists")
        else:
            print("❌ Failed to initialize database - no connection")
    except Exception as e:
        print(f"⚠️ Error initializing database: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    print("\n🚀 Starting Product API Service")
    print("-----------------------------")
    print("Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Database: {DB_CONFIG['dbname']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print("  (Password hidden for security)")
    
    initialize_database()
    
    print("\n🌍 Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)