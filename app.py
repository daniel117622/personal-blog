import math
from flask import Flask, render_template , request
import mocks

app = Flask(__name__)

@app.route('/article/<int:id>')
def article_page(id):
    # You can pass dynamic data here later
    article : mocks.Article = mocks.fill_article(str(id))
    thread : mocks.CommentThread = mocks.get_comment_thread("x")

    return render_template('index.html', 
                           article=article,
                           comment_thread=thread)

@app.route('/home')
def home_page():
    page = request.args.get('page', 1, type=int)
    page = page if page > 0 else 1
    POST_PER_PAGE = 6
    
    # Calculate OFFSET
    page_start = (page - 1) * POST_PER_PAGE
    
    # Fetch data slice and TRUE total count
    summaries = mocks.get_summaries(page_start, POST_PER_PAGE)
    total_count = mocks.get_total_count() # Assumes you added this helper in the previous step
    
    # Calculate total pages
    total_pages = math.ceil(total_count / POST_PER_PAGE)
    
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

if __name__ == '__main__':
    app.run(debug=True)