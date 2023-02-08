from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


MOVIE_DB_API_KEY = '985c2281013de5bd4be539f39bffd58f'
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


# create DB
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


# create Form
class EditData(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Change")


class AddData(FlaskForm):
    title = StringField('Movie Title')
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/delete', methods=['GET', 'POST'])
def delete_data():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()

    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add_data():
    form = AddData()
    if form.validate_on_submit():
        if form.title != '':
            movie_title = form.title.data
            response = requests.get('https://api.themoviedb.org/3/search/movie',
                                    params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
            data = response.json()["results"]
            print(data)
            return render_template('select.html', options=data)
    return render_template('add.html', form=form)


@app.route('/choose')
def choose_movie():
    movie_id = request.args.get('id')
    if movie_id:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}', params={"api_key": MOVIE_DB_API_KEY,
                                                                                          "language": "en-US"})
        data = response.json()
        movie_new = Movie(title=data['title'], year=data['release_date'].split('-')[0], description=data['overview'],
                          img_url=f'{MOVIE_DB_IMAGE_URL}{data["poster_path"]}')
        db.session.add(movie_new)
        db.session.commit()
        return redirect(url_for("edit_data", id=movie_new.id))


@app.route('/edit', methods=['GET', 'POST'])
def edit_data():
    form = EditData()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=form)


if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():
        db.create_all()
