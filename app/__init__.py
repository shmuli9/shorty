import random
import string

from flask import Flask, request, jsonify, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate = Migrate(app, db)

    class URL(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        url = db.Column(db.String(2048), nullable=False)
        slug = db.Column(db.String(100), unique=True, nullable=False)

    @app.route("/", methods=["GET", "POST"])
    def gen():
        if request.method == "GET":
            return render_template("index.html")

        data = request.form
        long_url = data["url"]

        if long_url.find("http://") == -1 and long_url.find("https://") == -1:
            long_url = "http://" + long_url

        slug = data["slug"] or ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        if URL.query.filter_by(slug=slug).first():
            return jsonify("error - slug already in use"), 500
        else:
            db_url = URL(slug=slug, url=long_url)
            db.session.add(db_url)
            db.session.commit()

        print(long_url, slug)

        resp = {
            "url": long_url,
            "slug": slug,
            "short": url_for("url", slug=slug, _external=True)
        }

        return jsonify(resp)

    @app.route("/<slug>")
    def url(slug):
        url_obj = URL.query.filter_by(slug=slug).first()

        if url_obj:
            long_url = url_obj.url
            return redirect(long_url)

        return jsonify(), 200

    return app
