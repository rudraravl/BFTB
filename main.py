import datetime
import os
from fileinput import filename
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, or_

# Colors:
# 517664 - 81, 118, 100 - Pale Green
# fbfbf2 - 251, 251, 242 - Off-White
# 000000 - 0, 0, 0 - Black
# FF5964 - 255, 89, 100 - Bright Pink/Salmon
# 35A7FF - 53, 167, 255 - Bright Blue


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///BFTB-DB.db"
db = SQLAlchemy(app)
FEATURED_ID_1 = 2
FEATURED_ID_2 = 1


class Thought(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thought = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    source = db.Column(db.String, nullable=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    day = db.Column(db.String, nullable=False)
    month = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    thumbnail = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)



logged_in = False
NULL_POST = {'id': 0,
             'title': 'More Coming Soon!', 'day': '16', 'month': 'January', 'year': '2004', 'subtitle': 'Stay Tuned',
             'author':
                 'Rudra', 'thumbnail': 'default.jpg', 'body': 'No post here yet!'
             }


def post_null_checker(post):
    if post is None:
        return NULL_POST
    return post


@app.route('/')
def index():
    global logged_in
    logged_in = False
    reverse_posts = db.session.execute(db.select(Post).order_by(Post.id * -1)).scalars()
    featured_post = None
    recent_posts = []
    i = 0
    for c_post in reverse_posts:
        if i < 3:
            recent_posts.append(c_post)
        if i == 0:
            featured_post = c_post
        if i >= 3:
            break
        i += 1
    sub_features = db.session.execute(
        db.select(Post).where(or_(Post.id == FEATURED_ID_1, Post.id == FEATURED_ID_2))).scalars()

    featured_post = post_null_checker(featured_post)
    recent_posts = [post_null_checker(c_post) for c_post in recent_posts]

    return render_template('index.html', featured_post=featured_post, sub_features=sub_features,
                           recent_posts=recent_posts)


@app.route('/latest')
def latest():
    latest_post = db.session.execute(db.select(Post).order_by(Post.id * -1)).scalar()
    return render_template('latest.html', post=post_null_checker(latest_post))


@app.route('/all')
def all():
    all_posts = db.session.execute(db.select(Post).order_by(Post.id * -1)).scalars()
    return render_template('all.html', posts=[post_null_checker(c_post) for c_post in all_posts])


@app.route('/thoughts')
def thoughts():
    all_thoughts = db.session.execute(db.select(Thought).order_by(Thought.id * -1)).scalars()
    return render_template('thoughts.html', thoughts=all_thoughts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        query = request.form.get('query')
        with open("static/contactme.csv", 'a') as file:
            file.write(f'{name}, {email}, {query}\n')
        return render_template('contact.html', message='Sent!')
    return render_template('contact.html', message='Contact me!')


@app.route('/post/<int:post_id>')
def post(post_id):
    current_post = db.session.execute(db.select(Post).where(Post.id == post_id)).scalar()
    return render_template('post.html', post=post_null_checker(current_post))


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         if request.form['password'] == ADMIN_PASSWORD:
#             global logged_in
#             logged_in = True
#             return redirect(url_for('admin'))
#         return render_template('login.html')
#     if request.method == "GET":
#         return render_template('login.html')


# @authentication_decorator
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global logged_in

    if not logged_in:
        if request.method == 'POST':
            if request.form['password'] == ADMIN_PASSWORD:
                logged_in = True
                return redirect(url_for('admin'))
            return render_template('login.html')
        if request.method == "GET":
            return render_template('login.html')

    else:
        if request.method == 'GET':
            return render_template('admin.html', message='')
        if request.method == 'POST':
            if request.form.get('submit-post') is not None:

                title = request.form.get('blog-title')
                subtitle = request.form.get('blog-subtitle')
                author = request.form.get('blog-author')
                pic = request.files['blog-pic']
                pic.save(f'static\\img\\thumbnails\\{title}.jpg')
                thumbnail = f'{title}.jpg'
                body = request.form.get('blog-body')
                day = datetime.date.today().strftime("%d")
                month = datetime.date.today().strftime("%B")
                year = datetime.date.today().strftime("%Y")

                new_post = Post(title=title, subtitle=subtitle, author=author, thumbnail=thumbnail, day=day,
                                month=month, year=year, body=body)
                with app.app_context():
                    db.session.add(new_post)
                    db.session.commit()
                return render_template('admin.html', message='Success')

            elif request.form.get('submit-thought') is not None:

                thought = request.form.get('thought')
                author = request.form.get('thought-author')
                source = request.form.get('thought-source')

                new_thought = Thought(thought=thought, author=author, source=source)
                with app.app_context():
                    db.session.add(new_thought)
                    db.session.commit()
                return render_template('admin.html', message='Success')


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        if request.form['submit'] == 'Subscribe':
            name = 'Reader'
            if request.form['name'] != '':
                name = request.form['name']
            new_subscriber = Subscriber(name=name, email=email)
            with app.app_context():
                db.session.add(new_subscriber)
                db.session.commit()
            return render_template('subscribe.html', message="subbed")
        else:
            with app.app_context():
                subscriber = db.session.execute(db.select(Subscriber).where(Subscriber.email == email)).scalar()
                db.session.delete(subscriber)
                db.session.commit()
            return render_template('subscribe.html', message='unsubbed')
    return render_template('subscribe.html', message='noSubmit')


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
