import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
Bootstrap5(app)
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjZDBlZjFiNGUwMTkyZjA2YzI4ODMyZTZiZWM2ZjQ3YyIsIm5iZiI6MTc4ODg3NTQzNS40MjcsInN1YiI6IjZhYTAxMmFiYTNiZWNiYmZjNGM3NjQxMiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.aJC8UXuev_dSzScRwW8FDF4ogRNkqTB3-IIv8gGQwko",
}


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
    year: Mapped[int] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=True)


with app.app_context():
    db.create_all()


# CREATE FROM
class movie_form(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
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
        result = db.session.execute(db.select(Movies).order_by(Movies.ranking))
        all_movies = result.scalars().all()
    return render_template("index.html", movie_list=all_movies)


@app.route("/add", methods=["GET", "POST"])
def addmovie():
    movies_form = movie_form()
    if movies_form.validate_on_submit():
        movie_title = movies_form.title.data
        response = requests.get(
            os.environ["MOVIE_DB_SEARCH_URL"],
            params={
                "api_key": f"{os.environ['API_KEY']}",
                "query": f"{movie_title}",
            },
            headers=headers,
        )
        data = response.json()["results"]
        return render_template("select.html", options=data)
    return render_template("add.html", form=movies_form)


@app.route("/delete/<int:movieid>")
def deletemovie(movieid):
    with app.app_context():
        Movie = db.session.execute(
            db.select(Movies).where(Movies.id == movieid)
        ).scalar()
        db.session.delete(Movie)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/edit", methods=["GET", "POST"])
def editmovie():
    edit_form = editmovie_form()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movies, movie_id)
    if edit_form.validate_on_submit():
        movie.rating = float(request.form["rating"])
        movie.review = request.form["review"]
        db.session.commit()
        with app.app_context():
            result = db.session.execute(db.select(Movies).order_by(Movies.rating))
            all_movies = result.scalars().all()
            for i in range(len(all_movies)):
                all_movies[i].ranking = len(all_movies) - i
                db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie, form=edit_form)


@app.route("/find/<int:movie_api_id>")
def find_movie(movie_api_id):
    print(movie_api_id)
    if movie_api_id:
        movie_api_url = f"{os.environ['MOVIE_DB_INFO_URL']}/{movie_api_id}"
        response = requests.get(
            movie_api_url,
            params={"api_key": os.environ["API_KEY"], "language": "en-US"},
        )
        data = response.json()
        new_movie = Movies(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{os.environ['MOVIE_DB_IMAGE_URL']}{data['poster_path']}",
            description=data["overview"],
        )
        db.session.add(new_movie)
        db.session.commit()
        movie = db.get_or_404(Movies,new_movie.id)
        print(movie.id)
    return redirect(url_for("editmovie", id=movie.id))


if __name__ == "__main__":
    app.run(debug=True)
