try:
    from flask import (
        Blueprint,
        Flask,
        Response,
        render_template,
        session,
        request,
        flash,
        url_for,
    )
except ModuleNotFoundError:
    print(f"Missing modules, please install with 'pip install exonviz[webserver]'")
    exit(-1)


from typing import Tuple, List, Dict, Any
import secrets
import functools
import copy

from exonviz import draw_exons, config, Exon
from exonviz import mutalyzer
from exonviz.cli import check_input, get_MANE, trim_variants
from werkzeug.utils import secure_filename

# Set up flask
app = Flask(__name__)
bp = Blueprint("exonviz", __name__)
app.register_blueprint(bp)

# Pull FLASK_SECRET_KEY from environment, or use fallback random ID
app.config.from_prefixed_env()
if not app.config.get("SECRET_KEY"):
    app.secret_key = secrets.token_hex()

# Log the secret key
app.logger.info(f"Secret key: {app.config['SECRET_KEY']}")


MANE = get_MANE()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", help="Hostname to listen on")
    parser.add_argument(
        "--debug", default=False, action="store_true", help="Run Flask in debug mode"
    )

    args = parser.parse_args()
    app.run(args.host, debug=args.debug)


@functools.cache
def cache_fetch_exons(transcript: str) -> Dict[str, Any]:
    """Wrapper to cache calls to mutalyzer"""
    no_variants = trim_variants(transcript)
    app.logger.info(f"Fetching {no_variants} from mutalyzer")
    return mutalyzer.fetch_exons(no_variants)


def build_exons(hgvs: str, config: Dict[str, Any]) -> Tuple[List[str], List[Exon]]:
    exons = copy.deepcopy(cache_fetch_exons(hgvs))

    build_exons, dropped_variants = mutalyzer.build_exons(hgvs, exons, config)
    return dropped_variants, build_exons


@app.route("/", methods=["GET"])
def index() -> str:
    # Put the default config into the session
    for key in config:
        if key not in session:
            session[key] = config[key]
    # Set a default transcript
    if "transcript" not in session:
        session["transcript"] = "NM_003002.4:r.[274g>u;300del]"
    # Set the width as default
    session["width"] = 1024
    # Set the first and last exon
    session["firstexon"] = 1
    session["lastexon"] = 1000
    # Set to show exonnumbers by default
    session["exonnumber"] = True

    return render_template("index.html")


def _update_config(config: Dict[str, Any], session: Any) -> Dict[str, Any]:
    """Update the configuration with values from the session"""
    d = config.copy()
    for key in d:
        d[key] = session[key]
    return d


def rewrite_transcript(transcript: str, MANE: Dict[str, str]) -> str:
    """Rewrite the transcript, if needed"""
    if transcript in MANE:
        transcript = MANE[transcript]
    return check_input(transcript)


@app.route("/", methods=["POST"])
def index_post() -> str:
    session["transcript"] = request.form["transcript"]
    session["height"] = int(request.form["height"])
    session["scale"] = float(request.form["scale"])
    session["gap"] = int(request.form["gap"])
    session["firstexon"] = int(request.form["firstexon"])
    session["lastexon"] = int(request.form["lastexon"])
    session["noncoding"] = "noncoding" in request.form
    session["exonnumber"] = "exonnumber" in request.form
    session["variantcolors"] = request.form["variantcolors"].split(" ")
    session["variantshape"] = request.form["variantshape"]

    # Checkboxes only show up when set to true
    session["color"] = request.form["color"] or config["color"]

    session["width"] = int(request.form["width"])

    download_url = url_for("draw", **session)

    try:
        # Rewrite the transcript
        session["transcript"] = rewrite_transcript(session["transcript"], MANE)
        dropped_variants, exons = build_exons(
            session["transcript"], config=_update_config(config, session)
        )
        figure = str(draw_exons(exons, config=_update_config(config, session)))
    except Exception as e:
        flash(str(e))
        figure = ""
        dropped_variants = list()

    # Report any variants we had to drop
    if dropped_variants:
        varstring = ", ".join(dropped_variants)
        if len(dropped_variants) > 1:
            flash(
                f"Dropped {len(dropped_variants)} variants which falls outside the exons: {varstring}"
            )
        else:
            flash(f"Dropped 1 variant which falls outside the exons: {varstring}")

    return render_template("index.html", figure=str(figure), download_url=download_url)


@app.route("/draw", methods=["GET"])
def draw() -> Response:
    figure_config: dict[str, Any] = dict(request.args)

    # Get the list of variant colors
    figure_config["variantcolors"] = request.args.getlist("variantcolors")

    # Rewrite the transcript, if required. This will also lookup the MANE select
    # for gene names
    figure_config["transcript"] = rewrite_transcript(figure_config["transcript"], MANE)

    # Cast integer values to int
    for field in ["firstexon", "lastexon", "gap", "height", "width"]:
        figure_config[field] = int(figure_config[field])

    # Cast float values to float
    for field in ["scale"]:
        figure_config[field] = float(figure_config[field])

    # Cast boolean values to boolean
    for field in ["exonnumber", "noncoding"]:
        figure_config[field] = figure_config[field] == "True"

    # Pull out the transcript name
    transcript = figure_config.pop("transcript")

    dropped_variants, exons = build_exons(transcript, figure_config)
    figure = str(draw_exons(exons, figure_config))
    fname = secure_filename(f"{transcript}.svg")

    return Response(
        figure,
        mimetype="text/svg",
        headers={"Content-disposition": f"attachment; filename={fname}"},
    )


if __name__ == "__main__":
    main()
