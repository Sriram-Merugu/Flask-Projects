from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p/w500'
API_KEY = "YOUR API KEY"
app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
Bootstrap(app)
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
# creating db
SELECTED_MOVIE = 'https://api.themoviedb.org/3/movie'


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mymovies.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.init_app(app)

# creating new Table

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(300))
    img_url = db.Column(db.String(300), nullable=False)

with app.app_context():
    db.create_all()


# creating forms
class MovieForm(FlaskForm):
    your_rating = StringField(label="Your rating out of 10 e.g.8.6", validators=[DataRequired()])
    your_review = StringField(label="Your review", validators=[DataRequired()])
    update = SubmitField("submit")

# add movie by name
class MovieName(FlaskForm):
    new_movie = StringField(label="Movie title", validators=[DataRequired()])
    add = SubmitField("submit")

# create a new record

# new_movie = Movies(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )


# db.session.add(new_movie)
# db.session.commit()



@app.route("/")
def home():
    my_movies = db.session.query(Movies).order_by("rating").all()
    # This line loops through all the movies
    for i in range(len(my_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        my_movies[i].ranking = len(my_movies) - i
    db.session.commit()
    return render_template("index.html", movies=my_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = MovieForm()
    if form.validate_on_submit():
        movie_id = request.args.get('id')
        movie_to_update = Movies.query.get(movie_id)
        movie_to_update.rating = form.your_rating.data
        movie_to_update.review = form.your_review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', form=form)


@app.route('/delete')
def delete_movie():
    movie_id = request.args.get('id')

    # Delete a record by ID
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for('home'))

# add a movie

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    add_form = MovieName()
    if add_form.validate_on_submit():
        movie_title = add_form.new_movie.data
        response = requests.get(url=MOVIE_DB_SEARCH_URL, params={"api_key":API_KEY, "query": movie_title})
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template('add.html', form=add_form)


@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{SELECTED_MOVIE}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movies(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{TMDB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"],
            rating=0,
            ranking=0,
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("edit", id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
