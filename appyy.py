from flask import Flask, render_template, jsonify, request
import mysql.connector
from datetime import datetime, timedelta
from collections import defaultdict
import subprocess
import threading
import os

app = Flask(__name__)

# ============================================
# DATABASE CONFIGURATION (from your db.py)
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'vyo231106',
    'database': 'vyok'
}

def get_db_connection():
    """Create a database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/stats')
def get_stats():
    """Get overall statistics for dashboard"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Total products
        cursor.execute("SELECT COUNT(*) as total FROM products")
        total = cursor.fetchone()['total']
        
        # Products by platform
        cursor.execute("""
            SELECT platform, COUNT(*) as count 
            FROM products 
            GROUP BY platform
        """)
        by_platform = cursor.fetchall()
        
        # Products by item_type (category)
        cursor.execute("""
            SELECT item_type, COUNT(*) as count 
            FROM products 
            GROUP BY item_type 
            ORDER BY count DESC 
            LIMIT 10
        """)
        by_category = cursor.fetchall()
        
        # Average price by platform
        cursor.execute("""
            SELECT platform, 
                   ROUND(AVG(price), 2) as avg_price,
                   ROUND(MIN(price), 2) as min_price,
                   ROUND(MAX(price), 2) as max_price,
                   currency
            FROM products 
            GROUP BY platform, currency
        """)
        price_by_platform = cursor.fetchall()
        
        # Recent additions (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as recent 
            FROM products 
            WHERE scrape_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        recent = cursor.fetchone()['recent']
        
        # Overall price statistics
        cursor.execute("""
            SELECT 
                ROUND(MIN(price), 2) as min_price, 
                ROUND(MAX(price), 2) as max_price,
                ROUND(AVG(price), 2) as avg_price,
                currency
            FROM products
            LIMIT 1
        """)
        price_stats = cursor.fetchone()
        
        # Products scraped per day (last 30 days)
        cursor.execute("""
            SELECT 
                DATE(scrape_time) as date,
                COUNT(*) as count
            FROM products
            WHERE scrape_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(scrape_time)
            ORDER BY date ASC
        """)
        daily_scrapes = cursor.fetchall()
        
        # Format dates for JSON
        for item in daily_scrapes:
            if 'date' in item and item['date']:
                item['date'] = item['date'].strftime('%Y-%m-%d')
        
        return jsonify({
            'total_products': total,
            'by_platform': by_platform,
            'by_category': by_category,
            'price_by_platform': price_by_platform,
            'recent_additions': recent,
            'price_stats': price_stats,
            'daily_scrapes': daily_scrapes
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/products')
def get_products():
    """Get products with pagination, search and filtering"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        platform = request.args.get('platform', '')
        item_type = request.args.get('item_type', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'scrape_time')
        sort_order = request.args.get('sort_order', 'DESC')
        
        # Build WHERE clause
        where_clauses = []
        params = []
        
        if platform:
            where_clauses.append("platform = %s")
            params.append(platform)
        
        if item_type:
            where_clauses.append("item_type = %s")
            params.append(item_type)
        
        if search:
            where_clauses.append("product_name LIKE %s")
            params.append(f"%{search}%")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as total FROM products WHERE {where_sql}", params)
        total = cursor.fetchone()['total']
        
        # Get products with pagination
        offset = (page - 1) * per_page
        query = f"""
            SELECT * FROM products 
            WHERE {where_sql}
            ORDER BY {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        # Format datetime objects for JSON
        for product in products:
            if 'scrape_time' in product and product['scrape_time']:
                product['scrape_time'] = product['scrape_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'products': products,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/filters')
def get_filters():
    """Get available filter options"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all platforms
        cursor.execute("SELECT DISTINCT platform FROM products ORDER BY platform")
        platforms = [row['platform'] for row in cursor.fetchall()]
        
        # Get all item types
        cursor.execute("SELECT DISTINCT item_type FROM products ORDER BY item_type")
        item_types = [row['item_type'] for row in cursor.fetchall()]
        
        return jsonify({
            'platforms': platforms,
            'item_types': item_types
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/price-distribution')
def get_price_distribution():
    """Get price distribution data for charts"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Price ranges
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN price < 100 THEN '0-100'
                    WHEN price < 500 THEN '100-500'
                    WHEN price < 1000 THEN '500-1000'
                    WHEN price < 2000 THEN '1000-2000'
                    ELSE '2000+'
                END as price_range,
                COUNT(*) as count
            FROM products
            GROUP BY price_range
            ORDER BY 
                CASE price_range
                    WHEN '0-100' THEN 1
                    WHEN '100-500' THEN 2
                    WHEN '500-1000' THEN 3
                    WHEN '1000-2000' THEN 4
                    ELSE 5
                END
        """)
        price_distribution = cursor.fetchall()
        
        return jsonify({
            'price_distribution': price_distribution
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/top-products')
def get_top_products():
    """Get top products by price"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        limit = int(request.args.get('limit', 10))
        
        # Most expensive products
        cursor.execute(f"""
            SELECT product_name, price, currency, platform
            FROM products
            ORDER BY price DESC
            LIMIT %s
        """, (limit,))
        most_expensive = cursor.fetchall()
        
        # Cheapest products
        cursor.execute(f"""
            SELECT product_name, price, currency, platform
            FROM products
            ORDER BY price ASC
            LIMIT %s
        """, (limit,))
        cheapest = cursor.fetchall()
        
        return jsonify({
            'most_expensive': most_expensive,
            'cheapest': cheapest
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ============================================
# SCRAPING ENDPOINTS
# ============================================

@app.route('/api/scrape', methods=['POST'])
def scrape_products():
    """Trigger scraping for a keyword"""
    data = request.get_json()
    keyword = data.get('keyword', '').strip()
    platforms = data.get('platforms', ['Amazon', 'IKEA'])
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400
    
    def run_scraper(platform, keyword):
        """Run scraper in background"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            python_exe = os.path.join(script_dir, '.bego', 'Scripts', 'python.exe')
            
            if platform == 'Amazon':
                script_path = os.path.join(script_dir, 'amazon_scraper.py')
            elif platform == 'IKEA':
                script_path = os.path.join(script_dir, 'ikea_scrpp.py')
            else:
                return
            
            # Run scraper with keyword as input
            process = subprocess.Popen(
                [python_exe, script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=script_dir
            )
            stdout, stderr = process.communicate(input=keyword + '\n', timeout=300)
            print(f"{platform} scraper output:", stdout)
            if stderr:
                print(f"{platform} scraper errors:", stderr)
        except Exception as e:
            print(f"Error running {platform} scraper: {e}")
    
    # Start scrapers in background threads
    for platform in platforms:
        if platform in ['Amazon', 'IKEA']:
            thread = threading.Thread(target=run_scraper, args=(platform, keyword))
            thread.daemon = True
            thread.start()
    
    return jsonify({
        'success': True,
        'message': f'Scraping started for "{keyword}" on {", ".join(platforms)}. This may take a few minutes.',
        'keyword': keyword,
        'platforms': platforms
    })

# ============================================
# RUN THE APP
# ============================================

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) so it's accessible from other devices
    # Access via: http://localhost:5000 or http://YOUR_IP:5000
    app.run(host='0.0.0.0', port=8080, debug=True)