from flask import Flask, render_template, request
import mbta_helper

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/nearest_mbta", methods=["POST"])
def nearest_mbta():
    """
    Handle form submission:
      - get place name from form
      - call mbta_helper.find_stop_near
      - render result page
    """
    place_name = request.form.get("place_name", "").strip()

    if not place_name:
        # simple validation
        return render_template(
            "error.html",
            message="Please enter a place name."
        )

    try:
        station_name, is_accessible = mbta_helper.find_stop_near(place_name)
        return render_template(
            "mbta_station.html",
            place_name=place_name,
            station_name=station_name,
            is_accessible=is_accessible,
        )
    except Exception as e:
        # For debugging, you might print(e) in the console
        return render_template(
            "error.html",
            message=f"Could not find a nearby station for {place_name}."
        )


if __name__ == "__main__":
    app.run(debug=True)
