from flask import Flask, render_template, redirect, url_for, request, session
from flask_bootstrap import Bootstrap, Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float, desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top_movies.db"
db = SQLAlchemy(app)


# CREATE TABLE
class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float)
    ranking= db.Column(db.Integer)
    review= db.Column(db.String(250))
    img_url= db.Column(db.String(250))
    def __repr__(self):
        return f"<Movie {self.title}>"


with app.app_context():
    db.create_all()
    new_movie = Movies(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg")

    try:
        db.session.add(new_movie)
        db.session.commit()
    except:
        db.session.rollback()
    second_movie = Movies(
        title="Avatar The Way of Water",
        year=2022,
        description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
        rating=7.3,
        ranking=9,
        review="I liked the water.",
        img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg")

    try:
        db.session.add(second_movie)
        db.session.commit()
        print("adding movie worked")
    except:
        print("adding movie didnt work")
        db.session.rollback()

### Movie Search ###
def search_movie(movie_string):
    '''in form eingegebener string wird auf the movie db homepage gesucht und das json file zurückgegeben'''
    movie_search = movie_string.replace(" ","%20")
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_search}&include_adult=false&language=en-US&page=1"
    API_KEY = "5245b8736f0dfedeeabe27e8fa7faa46"
    API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1MjQ1Yjg3MzZmMGRmZWRlZWFiZTI3ZThmYTdmYWE0NiIsIm5iZiI6MTcxOTU2Njk5NS40MDgwMjcsInN1YiI6IjY2N2U4MThkNWRkMjQ5YTUyZjQ1ZjVmYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.xyrSUt_f6D5dojsUhBHY1kLU77vez0STIiSx8HMwjtI"
    headers = {"accept": "application/json", "Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(url, headers=headers)
    return response.json()["results"]

def movieyear_list(movie_data):
    movieyear_list = []
    for movie in movie_data["results"]:
        movieyear_list.append(f"{movie['original_title']} - {movie['release_date'][0:4]}")
    print(movieyear_list)
    return movieyear_list

def add_movieyear(movie_data):
    '''adds the movie year to each result'''
    for movie in movie_data:
        movie["release_year"] = movie['release_date'][0:4]
    return movie_data

def gen_new_movie(selected_movie):
    new_movie = Movies(
        title = selected_movie["original_title"],
        year = int(selected_movie["release_year"]),
        description = selected_movie["overview"],
        rating = round(float(selected_movie["vote_average"]),2),
        ranking = 10,
        review = "shit",
        img_url = f"https://image.tmdb.org/t/p/w500/{selected_movie['poster_path']}"
    )
    return new_movie


class RateMovieForm(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

class AddMovieForm(FlaskForm):
    new_movie = StringField("Add a new movie!")
    submit = SubmitField("Done")

# class FindMovieForm(FlaskForm):
#     new_movie = StringField("Add a new movie!")
#     submit = SubmitField("Done")

@app.route("/delete",methods=["GET"])
def delete_movie():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/")
def home():
    all_movies = db.session.execute(db.select(Movies).order_by(desc(Movies.rating))).scalars().all()
    return render_template("index.html", all_movies = all_movies)

@app.route("/edit", methods=["GET", "POST"])
# coming from index
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)



@app.route("/add", methods=["GET","POST"])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        new_movie = form.new_movie.data
        print(f"{new_movie} line 165")
        movie_data = search_movie(new_movie)
        movie_data = add_movieyear(movie_data)
        #session['movie_data'] = movie_data
        return render_template("select.html", movie_data=movie_data, movie_search=new_movie)

    return render_template("add.html", form=form)

@app.route("/generate", methods=["GET"])
def gen_movie():
    #movie_title = request.args.get("movie_title") #infos aus select form holen
    movie_search = request.args.get("movie_search")
    print(movie_search)
    number = request.args.get("number")
    print(number)
    all_movies = search_movie(movie_search)
    all_movies = add_movieyear(all_movies) # jahr hinzufügen
    new_movie = gen_new_movie(all_movies[int(number)]) # Movies Objekt generieren
    try:
        db.session.add(new_movie)
        db.session.commit()
        movie_id = db.session.execute(db.select(func.max(Movies.id))).scalar()#movie_id ist letzter zugefügter film und damit max id
        print(movie_id)
        return redirect(url_for("rate_movie", id = movie_id))
    except:
        db.session.rollback()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)
