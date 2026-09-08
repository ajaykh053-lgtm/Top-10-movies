from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, IntegerField, URLField
from wtforms.validators import DataRequired, URL
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Movies_day64.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app=app)


# CREATE TABLE
class Movies(db.Model):
    id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


with app.app_context():
    db.create_all()

# # Manually Adding Movies to Database
# with app.app_context():
#     new_movie = Movies(
#         title="Phone Booth",
#         year=2002,
#         description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#         rating=7.3,
#         ranking=10,
#         review="My favourite character was the caller.",
#         img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg",
#     )
#     db.session.add(new_movie)
#     db.session.commit()
# with app.app_context():
#     second_movie = Movies(
#         title="Avatar The Way of Water",
#         year=2022,
#         description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#         rating=7.3,
#         ranking=9,
#         review="I liked the water.",
#         img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
#     )
#     db.session.add(second_movie)
#     db.session.commit()


# CREATE FROM
class movie_form(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    year = IntegerField("Movie Released Year", validators=[DataRequired()])
    description = StringField("Movie Description", validators=[DataRequired()])
    rating = FloatField("Movie Rating", validators=[DataRequired()])
    ranking = IntegerField("Movie Ranking", validators=[DataRequired()])
    review = StringField("Movie Review", validators=[DataRequired()])
    img_url = URLField("Movie Link", validators=[DataRequired(), URL()])
    submit = SubmitField("Add")


class editmovie_form(FlaskForm):
    rating = FloatField(
        "Your Movie Rating out of 10 eg:7.5", validators=[DataRequired()]
    )
    review = StringField("Movie Review", validators=[DataRequired()])
    submit = SubmitField("Add")

@app.route("/")
def home():
    with app.app_context():
        movies = (
            db.session.execute(db.select(Movies).order_by(Movies.id)).scalars()
        ).all()
    return render_template("index.html", movie_list=movies)


@app.route("/edit/<int:movieid>", methods=["GET", "POST"])
def editmovie(movieid):
    edit_form = editmovie_form()
    if request.method == "POST":
        with app.app_context():
            new_rating = db.session.execute(db.select(Movies).where(Movies.id == movieid)).scalar()
            new_review = db.session.execute(db.select(Movies).where(Movies.id == movieid)).scalar()
            new_rating.rating = request.form["rating"]
            new_review.review = request.form["review"]
            db.session.commit()
        return redirect(url_for('home'))
    else:
        pass
    return render_template("edit.html", form=edit_form)


@app.route("/add", methods=["GET", "POST"])
def addmovie():
    movies_form = movie_form()
    if request.method == "POST":
        with app.app_context():
            Movie = Movies(
                title=request.form["title"],
                year=request.form["year"],
                description=request.form["description"],
                rating=request.form["rating"],
                ranking=request.form["ranking"],
                review=request.form["review"],
                img_url=request.form["img_url"],
            )
            db.session.add(Movie)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=movies_form)


@app.route("/delete/<int:movieid>")
def deletemovie(movieid):
    with app.app_context():
        Movie = db.session.execute(db.select(Movies).where(Movies.id == movieid)).scalar()
        db.session.delete(Movie)
        db.session.commit()
    return redirect(url_for('home'))


@app.route("/select", methods=["GET", "POST"])
def selectmovie():
    return render_template("select.html")


if __name__ == "__main__":
    app.run(debug=True)
