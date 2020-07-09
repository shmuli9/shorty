import random
import string
import os

from flask import Flask, request, jsonify, redirect, render_template, url_for, send_from_directory
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
        """
        Generate new shortened url. Slug is optional, if not provided a random one will be created

        Required:
            url: string - url

        Optional:
            slug: string - slug to use

        :return
            400 - error - url not provided
            422 - error - slug already in use
            200 -   {
                        url,
                        slug,
                        short
                    }
        """

        if request.method == "GET":
            return render_template("index.html")

        data = request.form
        long_url = data["url"]

        if not long_url:
            return jsonify("error - url not provided"), 400

        if long_url.find("http://") == -1 and long_url.find("https://") == -1:
            long_url = "http://" + long_url

        if data["slug"]:  # if slug provided, use that as slug
            slug = data["slug"]

            if URL.query.filter_by(slug=slug).first():  # if slug in use, error out
                return jsonify("error - slug already in use"), 422

        elif URL.query.filter_by(url=long_url).first():  # check if url already stored, and reuse slug
            slug = URL.query.filter_by(url=long_url).first().slug

        else:  # otherwise geenrate random slug
            slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

            while URL.query.filter_by(slug=slug).first():  # check if slug in use, if so regenerate
                slug = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        db_data = {
            "slug": slug,
            "url": long_url
        }

        db_url = URL(**db_data)
        db.session.add(db_url)
        db.session.commit()

        resp = {
            **db_data,
            "short": url_for("url", slug=slug, _external=True)
        }

        return jsonify(resp)

    @app.route("/<slug>")
    def url(slug):
        """
        Use the slug to redirect to URL
        Also acts as favicon request handler

        Required:
            slug: string referring to URL in db

        :return:
            200 - favicon
            302 - redirect to correct site
            404 - slug does not refer to a knwn url
        """

        if slug == "favicon.ico":
            return send_from_directory(os.path.join(app.root_path, 'static'),
                                       "favicon.ico", mimetype="image/vnd.microsoft.icon")

        url_obj = URL.query.filter_by(slug=slug).first()

        if url_obj:
            long_url = url_obj.url
            return redirect(long_url)

        return jsonify("error - link not found"), 404

    return app
