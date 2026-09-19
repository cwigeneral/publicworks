import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
database_url = os.getenv("DATABASE_URL", "sqlite:///publicworks.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Rhythm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    place = db.Column(db.String(120), nullable=False)
    cadence = db.Column(db.String(80), nullable=False, default="daily")
    domain = db.Column(db.String(80), nullable=False, default="General")
    context = db.Column(db.String(80), nullable=False, default="General")


class Witness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rhythm_id = db.Column(db.Integer, db.ForeignKey("rhythm.id"), nullable=False)
    condition = db.Column(db.String(16), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    rhythm = db.relationship("Rhythm")


class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rhythm_id = db.Column(db.Integer, db.ForeignKey("rhythm.id"), nullable=False)
    state = db.Column(db.String(16), nullable=False)
    route = db.Column(db.String(24), nullable=False)
    opened_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime(timezone=True))
    rhythm = db.relationship("Rhythm")


SEED_RHYTHMS = [
    ("Water System", "Water Facilities", "daily", "Water", "System"),
    ("Sewer System", "Sewer Facilities", "daily", "Sewer", "System"),
    ("Main Street", "Main Street", "regular", "Public Realm", "General"),
]

PARKS = [
    "Main Street Park",
    "Kiwanis Park (Library Park)",
    "Log Cabin (Hamilton) Park",
    "Sheridan Pool",
    "Baseball Fields Park",
]

PARK_CONTEXTS = ["Grounds", "Trash"]


def seed():
    for name, place, cadence, domain, context in SEED_RHYTHMS:
        if not Rhythm.query.filter_by(name=name).first():
            db.session.add(Rhythm(name=name, place=place, cadence=cadence, domain=domain, context=context))

    for place in PARKS:
        for context in PARK_CONTEXTS:
            name = f"{place} — {context}"
            if not Rhythm.query.filter_by(name=name).first():
                db.session.add(Rhythm(
                    name=name,
                    place=place,
                    cadence="regular",
                    domain="Parks",
                    context=context,
                ))
    db.session.commit()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/state")
def state():
    rhythms = Rhythm.query.order_by(Rhythm.id).all()
    latest = {}
    for witness in Witness.query.order_by(Witness.created_at.desc()).all():
        latest.setdefault(witness.rhythm_id, witness)

    active = Condition.query.filter(Condition.resolved_at.is_(None)).order_by(Condition.opened_at.desc()).all()
    return jsonify({
        "rhythms": [{
            "id": r.id,
            "name": r.name,
            "place": r.place,
            "cadence": r.cadence,
            "domain": r.domain,
            "context": r.context,
            "latest_condition": latest[r.id].condition if r.id in latest else None,
        } for r in rhythms],
        "conditions": [{
            "id": c.id,
            "rhythm_id": c.rhythm_id,
            "name": c.rhythm.name,
            "place": c.rhythm.place,
            "state": c.state,
            "route": c.route,
        } for c in active],
    })


@app.post("/api/witness")
def witness():
    payload = request.get_json(force=True)
    rhythm = db.session.get(Rhythm, int(payload["rhythm_id"]))
    state = payload["condition"]
    if not rhythm or state not in {"good", "watch", "act"}:
        return jsonify({"error": "invalid witness"}), 400

    db.session.add(Witness(rhythm_id=rhythm.id, condition=state))
    active = Condition.query.filter_by(rhythm_id=rhythm.id, resolved_at=None).first()

    if state == "good":
        if active:
            active.state = "resolved"
            active.resolved_at = datetime.now(timezone.utc)
    else:
        route = "watch" if state == "watch" else "today"
        if active:
            active.state = state
            active.route = route
        else:
            db.session.add(Condition(rhythm_id=rhythm.id, state=state, route=route))

    db.session.commit()
    return jsonify({"ok": True})


with app.app_context():
    db.create_all()
    seed()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
