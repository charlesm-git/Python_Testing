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
        # Extract data from the form
        competition = next(
            (
                c
                for c in app.competitions
                if c["name"] == request.form["competition"]
            ),
            None,
        )
        club = next(
            (c for c in app.clubs if c["name"] == request.form["club"]), None
        )
        placesRequired = int(request.form["places"])

        club_already_booked_places = 0
        if (
            "participants" in competition
            and club["name"] in competition["participants"]
        ):
            club_already_booked_places = competition["participants"][
                club["name"]
            ]

        # Checks if it is allowed to book the number of places requested
        can_buy = True
        if placesRequired > 12 - club_already_booked_places:
            flash(
                "You can't purchase more than 12 places per club for a "
                "competition"
            )
            can_buy = False
        if placesRequired > club["points"]:
            flash("You don't have enough points to book that many places")
            can_buy = False
        if placesRequired > competition["numberOfPlaces"]:
            flash(
                "You are booking more places than the number of places "
                "available for this competition"
            )
            can_buy = False

        # If allowed, the number of places in the competition and the
        # number of points of the club is updated. Otherwise, refresh the
        # booking page with error messages
        if can_buy:
            competition["numberOfPlaces"] = (
                competition["numberOfPlaces"] - placesRequired
            )

            # if the participants key doesn't exist, creates it an
            # initialize an empty dictionary
            if "participants" not in competition:
                competition["participants"] = {}
            # if the club hasn't booked any places yet, creates the key in
            # the participants dictionary
            if club["name"] not in competition["participants"]:
                competition["participants"][club["name"]] = 0

            # Updates the number of places left in the competition and the
            # clubs number of points
            competition["participants"][club["name"]] += placesRequired
            club["points"] = club["points"] - placesRequired

            flash("Great-booking complete!")
            return render_template(
                "welcome.html", club=club, competitions=app.competitions
            )
        else:
            return redirect(
                url_for(
                    "book",
                    club=club["name"],
                    competition=competition["name"],
                )
            )

    # TODO: Add route for points display

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
