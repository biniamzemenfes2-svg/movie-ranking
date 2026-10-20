from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

MOVIE_API_KEY = "9f802bdd0a249e8ad1405a2254f5db2f"

app = Flask(__name__)

class base(DeclarativeBase):
    pass

class editform(FlaskForm):
    rating = StringField("your rating out of 10 e.g 7.3", validators=[DataRequired()])
    review = StringField("your review", validators=[DataRequired()])
    submit = SubmitField("Done")

class addform(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
bootstrap = Bootstrap5(app)

# CREATE DB


db = SQLAlchemy()
db.init_app(app)
# CREATE TABLE
class movies(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description:Mapped[str] = mapped_column(String(1000), nullable=True)
    rating:Mapped[float] = mapped_column(Float, nullable=False)
    ranking:Mapped[int] = mapped_column(Integer, nullable=False)
    review:Mapped[str] = mapped_column(String(500), nullable=True)
    image_url:Mapped[str] = mapped_column(String(500), nullable=False)

with app.app_context():
    db.create_all()


# with app.app_context():
#     existing_movie = db.session.execute(
#         db.select(movies).where(movies.title == "Phone Booths")
#     ).scalar_one_or_none()

#     if existing_movie is None:
#         new_movie = movies(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     image_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

#         db.session.add(new_movie)
#         db.session.commit()
#         print("Movie added successfully!")
#     else:
#         print("Movie already exists!")



@app.route("/")
def home():
    with app.app_context():
        all_movies = db.session.execute(db.select(movies).order_by(movies.title)).scalars().all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit/<int:id>", methods = ["GET", "POST"])
def edit(id):
    form = editform()
    movies_to_edit = db.session.execute(db.select(movies).where(movies.id == id)).scalar()
    if form.validate_on_submit():
        movies_to_edit.rating = float(form.rating.data)
        movies_to_edit.review = form.review.data
        db.session.commit()
        return redirect("/")
    return render_template("edit.html", movie=movies_to_edit, form=form)


@app.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    movie_to_delete = db.get_or_404(movies, id)

    db.session.delete(movie_to_delete)
    db.session.commit()

    return redirect(url_for("home"))



@app.route("/add", methods=["GET", "POST"])
def add():
    add_form = addform()
    if add_form.validate_on_submit():
        movie_title = add_form.title.data
        # Make a request to the TMDB API to search for the movie
        response = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": MOVIE_API_KEY, "query": movie_title},
        )
        data = response.json()
        if data["results"]:
            # If there are results, take the first one
            movie_data = data["results"][0]
            new_movie = movies(
                title=movie_data["title"],
                year=int(movie_data["release_date"].split("-")[0]) if movie_data.get("release_date") else None,
                description=movie_data.get("overview"),
                rating=0.0,  # Default rating
                ranking=0,   # Default ranking
                review="",   # Default review
                image_url=f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}" if movie_data.get("poster_path") else None,
            )
            db.session.add(new_movie)
            db.session.commit()
            return redirect("/add")
    return render_template("add.html", form = add_form, error = "no movie found with that title. Please try again.")


if __name__ == '__main__':
    app.run(debug=True)
