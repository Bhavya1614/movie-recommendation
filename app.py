from flask import Flask, render_template, request, redirect
import pandas as pd
import random

app = Flask(__name__)

# Load data
df = pd.read_csv("movies.csv")
df = df[['title', 'overview', 'genres', 'director', 'vote_average']]
df.dropna(subset=["overview", "genres", "director"], inplace=True)
df.reset_index(drop=True, inplace=True)

liked = []
disliked = []
not_watched = []

@app.route("/")
def index():
    if df.empty:
        return "No more movies to rate!"
    movie = df.iloc[0]
    return render_template("index.html", movie=movie)

@app.route("/feedback", methods=["POST"])
def feedback():
    global df
    action = request.form['action']
    movie = df.iloc[0]
    df = df.drop(df.index[0])  # remove current movie

    if action == "like":
        liked.append(movie)
    elif action == "dislike":
        disliked.append(movie)
    else:
        not_watched.append(movie)

    return redirect("/")

@app.route("/recommendations")
def recommendations():
    if not liked:
        return "Please like some movies first."

    liked_df = pd.DataFrame(liked)
    top_genres = liked_df['genres'].str.split().explode().value_counts().index.tolist()
    top_directors = liked_df['director'].value_counts().index.tolist()

    # Recommend based on liked genres or director
    recommended = df[
        df['genres'].apply(lambda x: any(genre in x for genre in top_genres)) |
        df['director'].isin(top_directors)
    ].drop_duplicates(subset="title").head(10)

    return render_template("recommendations.html", movies=recommended.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True)
