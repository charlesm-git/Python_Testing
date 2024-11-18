import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs(club_path):
    with open(club_path) as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions(competition_path):
    with open(competition_path) as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


def create_app(config=None):
    app = Flask(__name__)
    app.secret_key = 'something_special'

    if config:
        app.config.update(config)
    else:
        app.config["COMPETITIONS_DB_PATH"] = "./competitions.json"
        app.config["CLUBS_DB_PATH"] = "./clubs.json"

    app.competitions = loadCompetitions(app.config["COMPETITIONS_DB_PATH"])
    app.clubs = loadClubs(app.config["CLUBS_DB_PATH"])

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/showSummary',methods=['POST'])
    def showSummary():
        club = next(
            (
                club
                for club in app.clubs
                if club["email"] == request.form["email"]
            ),
            None,
        )
        if club is not None:
            return render_template(
                "welcome.html", club=club, competitions=app.competitions
            )
        else:
            message = "This email was not found in the database"
            return render_template("index.html", message=message)

    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        foundClub = [c for c in app.clubs if c['name'] == club][0]
        foundCompetition = [c for c in app.competitions if c['name'] == competition][0]
        if foundClub and foundCompetition:
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        else:
            flash("Something went wrong-please try again")
            return render_template('welcome.html', club=club, competitions=app.competitions)

    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        competition = [c for c in app.competitions if c['name'] == request.form['competition']][0]
        club = [c for c in app.clubs if c['name'] == request.form['club']][0]
        placesRequired = int(request.form['places'])
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=app.competitions)

    # TODO: Add route for points display

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
