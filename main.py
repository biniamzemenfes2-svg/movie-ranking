from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
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

class base(DeclarativeBase):
    pass

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
#         new_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
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
    movies_to_edit = db.session.execute(db.select(movies).where(movies.id == id)).scalar()
    if request.method == "POST":
        movies_to_edit.rating = float(request.form.get("rating"))
        movies_to_edit.review = request.form.get("review")
        db.session.commit()
        return redirect("home")
    return render_template("edit.html", id=id, movie=movies_to_edit)

@app.route("/delete/<int:id>", methods = ["GET", "POST"])
def delete(id):
    movie_to_delete = db.session.execute(db.select(movies).where(movies.id == id)).scalar()
    if request.method == "POST":
        db.session.delete(movie_to_delete)
        db.session.commit()
    return render_template("index.html", movie=movie_to_delete)

if __name__ == '__main__':
    app.run(debug=True)
