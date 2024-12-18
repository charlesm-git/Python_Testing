import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs(club_path):
    with open(club_path) as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def updateClubsFile(
    clubs_path,
    clubs_list,
    updated_club,
):
    for club in clubs_list:
        if club["name"] == updated_club["name"]:
            club["points"] = updated_club["points"]
    updated_data = {"clubs": clubs_list}
    with open(clubs_path, "w") as club_file:
        json.dump(updated_data, club_file, indent=4)


def loadCompetitions(competition_path):
    with open(competition_path) as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


def updateCompetitionsFile(
    competitions_path,
    competitions_list,
    updated_competition,
):
    for competition in competitions_list:
        if competition["name"] == updated_competition["name"]:
            competition["numberOfPlaces"] = updated_competition[
                "numberOfPlaces"
            ]
    updated_data = {"competitions": competitions_list}
    with open(competitions_path, "w") as competition_file:
        json.dump(updated_data, competition_file, indent=4)


def create_app(config=None):
    app = Flask(__name__)
    app.secret_key = "something_special"

    if config:
        app.config.update(config)
    else:
        app.config["COMPETITIONS_DB_PATH"] = "./competitions.json"
        app.config["CLUBS_DB_PATH"] = "./clubs.json"

    app.competitions = loadCompetitions(app.config["COMPETITIONS_DB_PATH"])
    app.clubs = loadClubs(app.config["CLUBS_DB_PATH"])

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/showSummary", methods=["POST"])
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
            current_time = str(datetime.now())
            return render_template(
                "welcome.html",
                club=club,
                competitions=app.competitions,
                current_time=current_time,
            )
        else:
            message = "This email was not found in the database"
            return render_template("index.html", message=message)

    @app.route("/book/<competition>/<club>")
    def book(competition, club):
        foundClub = next((c for c in app.clubs if c["name"] == club), None)
        foundCompetition = next(
            (c for c in app.competitions if c["name"] == competition), None
        )
        # Render the welcome page if the club or the competition in the url is
        # wrong
        current_time = str(datetime.now())
        if foundClub is None or foundCompetition is None:
            flash("Something went wrong-please try again")
            return render_template(
                "welcome.html",
                club=foundClub,
                competitions=app.competitions,
                current_time=current_time,
            )
        # Render an error message if the user is trying to book place for a 
        # past competition.
        if foundCompetition["date"] <= current_time:
            flash("Booking on a past competition is not allowed")
            return render_template(
                "welcome.html",
                club=foundClub,
                competitions=app.competitions,
                current_time=current_time,
            )
        # If everything is ok, render the booking page.
        else:
            return render_template(
                "booking.html", club=foundClub, competition=foundCompetition
            )


    @app.route("/purchasePlaces", methods=["POST"])
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

            # Updates Database
            updateCompetitionsFile(
                app.config["COMPETITIONS_DB_PATH"],
                app.competitions,
                competition,
            )
            updateClubsFile(app.config["CLUBS_DB_PATH"], app.clubs, club)

            flash("Great-booking complete!")
            current_time = str(datetime.now())
            return render_template(
                "welcome.html",
                club=club,
                competitions=app.competitions,
                current_time=current_time,
            )
        else:
            return redirect(
                url_for(
                    "book",
                    club=club["name"],
                    competition=competition["name"],
                )
            )

    @app.route("/points")
    def points():
        return render_template("points.html", clubs=app.clubs)

    @app.route("/logout")
    def logout():
        return redirect(url_for("index"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
