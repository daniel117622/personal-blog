import math

from flask import Flask, jsonify, redirect, render_template, request, g, url_for

from data_access.db_bootstrap import ContentBlock
from models.article import Article
from services import get_service, USE_MOCK_DATA


app = Flask(__name__)


# ---------------------------------------------------------
# WEB ROUTES (HTML Views)
# ---------------------------------------------------------
@app.route('/')
def root():
    """Redirects root to the home page."""
    return redirect(url_for('home_page'))


@app.route('/home')
def home_page():
    service = get_service()

    page = request.args.get('page', 1, type=int)
    page = page if page > 0 else 1
    POST_PER_PAGE = 6
    
    # Calculate OFFSET
    offset = (page - 1) * POST_PER_PAGE
    
    # Fetch data via Service
    summaries = service.get_summaries(POST_PER_PAGE, offset)
    total_count = service.get_total_count()
    
    # Calculate total pages
    total_pages = math.ceil(total_count / POST_PER_PAGE) if total_count > 0 else 1
    
    # Logic for pagination buttons
    has_next = page < total_pages
    has_prev = page > 1

    return render_template(
        'home.html', 
        summaries=summaries, 
        page=page, 
        total_pages=total_pages,
        has_next=has_next, 
        has_prev=has_prev
    )


@app.route('/article/<int:id>')
def article_page(id):
    service = get_service()
    
    # Use the service to get data
    article = service.get_article(id)
    
    if not article:
        # Assuming you might want a 404 page, or just return text
        return render_template('404.html'), 404
    
    thread = service.get_comment_thread(id)

    return render_template(
        'index.html', 
        article=article,
        comment_thread=thread
    )


# ---------------------------------------------------------
# API ROUTES (JSON Data)
# ---------------------------------------------------------

@app.route('/api/articles', methods=['POST'])
def create_article():
    data = request.get_json()
    
    # Simple validation
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Convert raw JSON "content_blocks" to ContentBlock objects
        blocks = [ContentBlock(**b) for b in data.get('content_blocks', [])]
        
        # Create Article Object
        article = Article(
            id=data['id'],
            title=data['title'],
            date_created=data['date_created'],
            author=data['author'],
            topics=data['topics'],
            article_img_link=data['article_img_link'],
            content_blocks=blocks
        )

        service = get_service()
        service.create_article(article)
        
        return jsonify({"message": "Article created successfully", "id": article.id}), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/articles/<int:id>', methods=['DELETE'])
def delete_article(id):
    try:
        service = get_service()
        
        # Optional: Check if article exists first if you want 404 behavior
        article = service.get_article(id)
        if not article:
             return jsonify({"error": "Article not found"}), 404

        service.delete_article(id)
        
        return jsonify({"message": f"Article {id} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------ARN1exr@mhj6zkq6tgz
# APP LIFECYCLE
# ---------------------------------------------------------

@app.teardown_appcontext
def close_connection(exception):
    """
    Closes the database connection at the end of the request.
    This is critical when using the RealService to prevent connection leaks.
    """
    dao = g.pop('dao', None)
    if dao is not None:
        dao.con.close()


if __name__ == '__main__':
    print(f"--- APP STARTING (MOCK DATA: {USE_MOCK_DATA}) ---")
    app.run(host="0.0.0.0", port=5000, debug=True)