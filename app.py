import os
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

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
    attention = db.Column(db.String(40))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    rhythm = db.relationship("Rhythm")


class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rhythm_id = db.Column(db.Integer, db.ForeignKey("rhythm.id"), nullable=False)
    state = db.Column(db.String(16), nullable=False)
    route = db.Column(db.String(24), nullable=False)
    attention = db.Column(db.String(40))
    opened_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime(timezone=True))
    rhythm = db.relationship("Rhythm")


class Attention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rhythm_id = db.Column(db.Integer, db.ForeignKey("rhythm.id"), nullable=False)
    kind = db.Column(db.String(40), nullable=False)
    response = db.Column(db.String(16))
    opened_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime(timezone=True))
    rhythm = db.relationship("Rhythm")


class WorkSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("condition.id"), nullable=True)
    attention_id = db.Column(db.Integer, db.ForeignKey("attention.id"))
    rhythm_id = db.Column(db.Integer, db.ForeignKey("rhythm.id"), nullable=False)
    attention = db.Column(db.String(40))
    started_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ended_at = db.Column(db.DateTime(timezone=True))
    result = db.Column(db.String(16))
    condition = db.relationship("Condition")
    attention_record = db.relationship("Attention")
    rhythm = db.relationship("Rhythm")


SEED_RHYTHMS = [
    ("Water System", "Water Facilities", "daily", "Water", "System"),
    ("Sewer System", "Sewer Facilities", "daily", "Sewer", "System"),
    ("Main Street", "Main Street", "regular", "Public Realm", "General"),
]
PARKS = ["Main Street Park", "Kiwanis Park (Library Park)", "Log Cabin (Hamilton) Park", "Sheridan Pool", "Baseball Fields Park"]
PARK_CONTEXTS = ["Grounds", "Trash"]


def migrate():
    inspector = inspect(db.engine)
    if "rhythm" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("rhythm")}
    if "domain" not in columns:
        db.session.execute(text("ALTER TABLE rhythm ADD COLUMN domain VARCHAR(80) NOT NULL DEFAULT 'General'"))
    if "context" not in columns:
        db.session.execute(text("ALTER TABLE rhythm ADD COLUMN context VARCHAR(80) NOT NULL DEFAULT 'General'"))
    witness_columns = {column["name"] for column in inspector.get_columns("witness")}
    if "attention" not in witness_columns:
        db.session.execute(text("ALTER TABLE witness ADD COLUMN attention VARCHAR(40)"))
    condition_columns = {column["name"] for column in inspector.get_columns("condition")}
    if "attention" not in condition_columns:
        db.session.execute(text("ALTER TABLE condition ADD COLUMN attention VARCHAR(40)"))
    work_columns = {column["name"] for column in inspector.get_columns("work_session")}
    if "attention_id" not in work_columns:
        db.session.execute(text("ALTER TABLE work_session ADD COLUMN attention_id INTEGER"))
    db.session.commit()


def seed():
    for name, place, cadence, domain, context in SEED_RHYTHMS:
        if not Rhythm.query.filter_by(name=name).first():
            db.session.add(Rhythm(name=name, place=place, cadence=cadence, domain=domain, context=context))
    for place in PARKS:
        for context in PARK_CONTEXTS:
            name = f"{place} — {context}"
            if not Rhythm.query.filter_by(name=name).first():
                db.session.add(Rhythm(name=name, place=place, cadence="regular", domain="Parks", context=context))
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
    work = WorkSession.query.filter(WorkSession.ended_at.is_(None)).order_by(WorkSession.started_at.desc()).all()
    return jsonify({
        "rhythms": [{"id": r.id, "name": r.name, "place": r.place, "cadence": r.cadence, "domain": r.domain, "context": r.context, "latest_condition": latest[r.id].condition if r.id in latest else None} for r in rhythms],
        "conditions": [{"id": c.id, "rhythm_id": c.rhythm_id, "name": c.rhythm.name, "place": c.rhythm.place, "state": c.state, "route": c.route, "attention": c.attention, "work_session_id": next((w.id for w in work if w.condition_id == c.id), None)} for c in active],
        "work": [{"id": w.id, "condition_id": w.condition_id, "attention_id": w.attention_id, "rhythm_id": w.rhythm_id, "place": w.rhythm.place, "context": w.rhythm.context, "attention": w.attention, "started_at": w.started_at.isoformat()} for w in work],
    })


@app.post("/api/witness")
def witness():
    payload = request.get_json(force=True)
    rhythm = db.session.get(Rhythm, int(payload["rhythm_id"]))
    state = payload["condition"]
    attention = payload.get("attention")
    allowed_attention = {"mow", "weeds", "water", "clean", "damage", "other"}
    if not rhythm or state not in {"good", "watch", "act"}:
        return jsonify({"error": "invalid witness"}), 400
    if attention and (rhythm.domain != "Parks" or rhythm.context != "Grounds" or state != "act" or attention not in allowed_attention):
        return jsonify({"error": "invalid attention"}), 400
    db.session.add(Witness(rhythm_id=rhythm.id, condition=state, attention=attention))
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
            active.attention = attention
        else:
            db.session.add(Condition(rhythm_id=rhythm.id, state=state, route=route, attention=attention))
    db.session.commit()
    active = Condition.query.filter_by(rhythm_id=rhythm.id, resolved_at=None).first()
    attention_record = None
    if state == "act" and attention:
        attention_record = Attention(rhythm_id=rhythm.id, kind=attention)
        db.session.add(attention_record)
        db.session.commit()
    return jsonify({"ok": True, "condition_id": active.id if active else None, "attention_id": attention_record.id if attention_record else None})


@app.post("/api/attentions/<int:attention_id>/respond")
def respond_attention(attention_id):
    payload = request.get_json(force=True)
    response = payload.get("response")
    if response not in {"handled", "start", "route"}:
        return jsonify({"error": "invalid response"}), 400
    attention = db.session.get(Attention, attention_id)
    if not attention or attention.resolved_at is not None:
        return jsonify({"error": "attention not active"}), 404
    attention.response = response
    if response == "handled":
        attention.resolved_at = datetime.now(timezone.utc)
    elif response == "start":
        condition = Condition.query.filter_by(rhythm_id=attention.rhythm_id, resolved_at=None).first()
        work = WorkSession(condition_id=condition.id if condition else None, attention_id=attention.id, rhythm_id=attention.rhythm_id, attention=attention.kind)
        db.session.add(work)
        if condition:
            condition.route = "now"
    db.session.commit()
    return jsonify({"ok": True})


@app.post("/api/rhythms/<int:rhythm_id>/complete-witness")
def complete_witness(rhythm_id):
    rhythm = db.session.get(Rhythm, rhythm_id)
    if not rhythm:
        return jsonify({"error": "rhythm not found"}), 404
    unresolved = Attention.query.filter_by(rhythm_id=rhythm_id, resolved_at=None).count()
    active = Condition.query.filter_by(rhythm_id=rhythm_id, resolved_at=None).first()
    if unresolved == 0:
        db.session.add(Witness(rhythm_id=rhythm_id, condition="good"))
        if active:
            active.state = "resolved"
            active.resolved_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify({"ok": True, "balanced": unresolved == 0})


@app.post("/api/conditions/<int:condition_id>/handled")
def handled(condition_id):
    condition = db.session.get(Condition, condition_id)
    if not condition or condition.resolved_at is not None:
        return jsonify({"error": "condition not active"}), 404
    condition.state = "resolved"
    condition.resolved_at = datetime.now(timezone.utc)
    db.session.add(Witness(rhythm_id=condition.rhythm_id, condition="good"))
    db.session.commit()
    return jsonify({"ok": True})


@app.post("/api/conditions/<int:condition_id>/start")
def start_work(condition_id):
    condition = db.session.get(Condition, condition_id)
    if not condition or condition.resolved_at is not None:
        return jsonify({"error": "condition not active"}), 404
    active = WorkSession.query.filter_by(condition_id=condition.id, ended_at=None).first()
    if not active:
        active = WorkSession(condition_id=condition.id, rhythm_id=condition.rhythm_id, attention=condition.attention)
        db.session.add(active)
        condition.route = "now"
        db.session.commit()
    return jsonify({"ok": True, "work_session_id": active.id})


@app.post("/api/work/<int:work_id>/finish")
def finish_work(work_id):
    payload = request.get_json(force=True)
    result = payload.get("condition")
    if result not in {"good", "watch", "act"}:
        return jsonify({"error": "invalid result"}), 400
    work = db.session.get(WorkSession, work_id)
    if not work or work.ended_at is not None:
        return jsonify({"error": "work session not active"}), 404
    condition = work.condition
    attention_record = work.attention_record
    work.ended_at = datetime.now(timezone.utc)
    work.result = result
    db.session.add(Witness(rhythm_id=work.rhythm_id, condition=result, attention=work.attention if result == "act" else None))
    if attention_record and result == "good":
        attention_record.resolved_at = datetime.now(timezone.utc)
    if condition:
        if result == "good":
            unresolved = Attention.query.filter_by(rhythm_id=work.rhythm_id, resolved_at=None).count()
            if unresolved == 0:
                condition.state = "resolved"
                condition.resolved_at = datetime.now(timezone.utc)
            else:
                condition.state = "act"
                condition.route = "today"
        else:
            condition.state = result
            condition.route = "watch" if result == "watch" else "today"
    db.session.commit()
    return jsonify({"ok": True})


with app.app_context():
    db.create_all()
    migrate()
    seed()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
