from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "123"

# Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///admission.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#TABLES

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    intake = db.Column(db.Integer)

class Quota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    seats = db.Column(db.Integer)
    filled = db.Column(db.Integer, default=0)

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    marks = db.Column(db.Integer)
    quota = db.Column(db.String(50))

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer)
    quota_id = db.Column(db.Integer)
    status = db.Column(db.String(30), default="Allocated")
    number = db.Column(db.String(100))


# Create DB
with app.app_context():
    db.create_all()


#ROUTES
# Home → index.html
@app.route("/")
def home():
    return render_template("index.html")


# Program → program.html
@app.route("/program", methods=["GET", "POST"])
def program():
    if request.method == "POST":
        name = request.form["name"]
        intake = request.form["intake"]

        p = Program(name=name, intake=intake)

        db.session.add(p)
        db.session.commit()
        flash("Program Added")
        return redirect("/program")

    programs = Program.query.all()
    return render_template(
        "program.html",
        programs=programs
    )
    
# Quota → quota.html
@app.route("/quota", methods=["GET", "POST"])
def quota():
    if request.method == "POST":
        name = request.form["name"]
        seats = request.form["seats"]

        q = Quota(
            name=name,
            seats=seats
        )

        db.session.add(q)
        db.session.commit()
        flash("Quota Added")
        return redirect("/quota")

    quotas = Quota.query.all()
    return render_template(
        "quota.html",
        quotas=quotas
    )

# Applicant → applicant.html
@app.route("/applicant", methods=["GET", "POST"])
def applicant():
    if request.method == "POST":
        a = Applicant(
            name=request.form["name"],
            marks=request.form["marks"],
            quota=request.form["quota"]
        )

        db.session.add(a)
        db.session.commit()
        flash("Applicant Added")
        return redirect("/applicant")

    applicants = Applicant.query.all()
    return render_template(
        "applicant.html",
        applicants=applicants
    )

# Allocate → allocate.html
@app.route("/allocate", methods=["GET", "POST"])
def allocate():
    applicants = Applicant.query.all()
    if request.method == "POST":
        # Get values
        applicant_id = request.form.get("applicant")
        quota_name = request.form.get("quota")

        print("applicant:", applicant_id)
        print("quota:", quota_name)

        # Validating
        if applicant_id is None or quota_name is None or applicant_id == "" or quota_name == "":
            flash("Please select both Applicant and Quota")
            return redirect("/allocate")

        q = Quota.query.filter_by(name=quota_name).first()

        if not q:
            flash("Quota not found")
            return redirect("/allocate")

        if q.filled >= q.seats:
            flash("Quota Full")
            return redirect("/allocate")

        q.filled += 1

        ad = Admission(
            applicant_id=int(applicant_id),
            quota_id=q.id
        )

        db.session.add(ad)
        db.session.commit()
        flash("Seat Allocated")
        return redirect("/allocate")

    return render_template(
        "allocate.html",
        applicants=applicants
    )

# Dashboard → dashboard.html
@app.route("/dashboard")
def dashboard():
    programs = Program.query.count()
    applicants = Applicant.query.count()
    admissions = Admission.query.count()

    return render_template(
        "dashboard.html",
        programs=programs,
        applicants=applicants,
        admissions=admissions
    )


#RUN
if __name__ == "__main__":
    app.run(debug=True)
