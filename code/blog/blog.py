from flask import Flask, render_template, request, redirect, abort, session, url_for, flash
from db import connect_db

app = Flask(__name__)
app.config.from_object('config')

@app.route('/admin')
def adminLoggingPage():
    return render_template('adminLogging.html')

@app.route('/adminLogin', methods=['POST'])
def adminLogging(returnUrl='index'):
    error = None
    if request.form['login'] != app.config['USERNAME']:
        error = 'Invalid username'
    elif request.form['password'] != app.config['PASSWORD']:
        error = 'Invalid password'
    else:
        session['admin_logged_in'] = True
        flash('You were successfully logged in')
        return redirect(url_for(returnUrl))
    flash(error)
    return redirect(url_for('adminLoggingPage'))

@app.route('/adminLogout')
def adminLogout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    db = connect_db()
    cursor = db.execute('select name, title, content, posts.id, authors.id from authors, posts where authors.id = author_id')
    posts = [dict(author_name=row[0], title=row[1], content=row[2], id=row[3], author_id=row[4]) for row in cursor.fetchall()]
    db.close()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def getPost(post_id=None):
    if not post_id:
        abort(400)
    db = connect_db()
    cursor = db.execute('select name, title, content, posts.id, authors.id from authors, posts where posts.id = ? and authors.id = author_id', [post_id])
    posts = [dict(author_name=row[0], title=row[1], content=row[2], id=row[3], author_id=row[4]) for row in cursor.fetchall()]
    if len(posts) == 0:
        abort(404)
    return render_template('index.html', posts=posts)

@app.route('/author/<int:author_id>')
def getAuthorPosts(author_id=None):
    if not author_id:
        abort(400)
    db = connect_db()
    cursor = db.execute('select name, title, content, posts.id, authors.id from authors, posts where author_id = authors.id and posts.author_id = ?', [author_id])
    posts = [dict(author_name=row[0], title=row[1], content=row[2], id=row[3], author_id=row[4]) for row in cursor.fetchall()]
    if len(posts) == 0:
        abort(404)
    return render_template('index.html', posts=posts)

@app.route('/category/<int:cat_id>')
def getCategoryPosts(cat_id=None):
    if not cat_id:
        abort(400)
    db = connect_db()
    cursor = db.execute('select name, title, content, posts.id, authors.id from authors, posts where posts.author_id = authors.id and posts.category_id = ?', [cat_id])
    posts = [dict(author_name=row[0], title=row[1], content=row[2], id=row[3], author_id=row[4]) for row in cursor.fetchall()]
    if len(posts) == 0:
        abort(404)
    return render_template('index.html', posts=posts)

@app.route('/create')
def create():
    logged = session.get('admin_logged_in', False)
    if not logged:
        return redirect(url_for('adminLoggingPage'))
    db = connect_db()
    cursor = db.execute('select name, id from authors')
    authors = [dict(name=row[0], id=row[1]) for row in cursor.fetchall()]
    cursor = db.execute('select name, id from categories')
    categories = [dict(name=row[0], id=row[1]) for row in cursor.fetchall()]
    db.close()
    return render_template('create.html', authors=authors, categories=categories)

@app.route('/createPost', methods=['POST'])
def createPost():
    db = connect_db()
    cat_id = request.form['categoryId']
    aut_id = request.form['authorId']
    post_title = request.form['titleText']
    text = request.form['contentText']
    db.execute('insert into posts (author_id, category_id, title, content) values (?, ?, ?, ?)', [aut_id, cat_id, post_title, text])
    db.commit()
    return redirect("/")

if __name__ == '__main__':
    app.run()
