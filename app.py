# python -m venv myenv
# myenv\Scripts\activate
# pip install flask sqlalchemy flask-sqlalchemy flask-marshmallow mysql-connector-python

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError, validate
from password import my_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Task 1: Setting Up Flask with Flask-SQLAlchemy - Initialize a new Flask project and set up a virtual environment. - 
# Install Flask, Flask-SQLAlchemy, and Flask-Marshmallow. - Configure Flask-SQLAlchemy to connect to your database. - 
# Define `Members` and `WorkoutSessions` models using Flask-SQLAlchemy ORM.

# Expected Outcome: A Flask project connected to a database using SQLAlchemy with ORM models for `Members` and `WorkoutSessions`.

class MemberSchema(ma.Schema):  # Schemas substantiate how we want data to be
    name = fields.String(required=True)
    age = fields.Int(required=True)

    class Meta:
        fields = ("name", "age", "id")


class WorkoutSchema(ma.Schema):
    member_id = fields.Int(required=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    calories_burned = fields.Int(required=True)

    class Meta:
        fields = ("member_id", "date", "duration_minutes", "calories_burned", "session_id")


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

class Member(db.Model):
    __tablename__ = 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    # workouts = db.relationship('Workoutsession', backref='member') # Creates a virtual column that keeps track of the order ids.

class WorkoutSession(db.Model):
    __tablename__ = 'Workoutsessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer)
    calories_burned = db.Column(db.Integer)


@app.route('/')
def home():
    return 'Welome to the Fitness Center Management System'


@app.route('/members', methods=["GET"])
def get_members():
    members = Member.query.all()
    return members_schema.jsonify(members)
    

@app.route('/members/<int:id>', methods=['GET']) 
def get_member(id):
    member = Member.query.first()
    return member_schema.jsonify(member)
    

@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_member = Member(name=member_data['name'], age=member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201


@app.route("/members/<int:id>", methods=["PUT"]) 
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400    
    
    member.name = member_data['name']
    member.age = member_data['age']

    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200


@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):    
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200


@app.route("/workoutsessions", methods=["GET"])
def get_all_workouts():
    workouts = WorkoutSession.query.all()
    return workouts_schema.jsonify(workouts)


@app.route('/workoutsessions/<int:id>', methods=['GET']) #TODO get all workout sessions that relate to a specific member.
def get_workouts(id):
    pass


@app.route('/workoutsessions', methods=['POST'])
def add_workout():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    new_workout = WorkoutSession(
        member_id=workout_data['member_id'], 
        date=workout_data['date'], 
        duration_minutes=workout_data['duration_minutes'],
        calories_burned=workout_data['calories_burned'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({"message": "New workout added successfully"}), 201


@app.route("/workoutsessions/<int:session_id>", methods=["PUT"]) 
def update_workout(session_id):
    workout = WorkoutSession.query.get_or_404(session_id)
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400    
    
    workout.member_id = workout_data['member_id']
    workout.date = workout_data['date']
    workout.duration_minutes = workout_data['duration_minutes']
    workout.calories_burned = workout_data['calories_burned']

    db.session.commit()
    return jsonify({"message": "Workout details updated successfully"}), 200


@app.route("/workoutsessions/<int:session_id>", methods=["DELETE"])
def delete_workout(session_id):   
    workout = WorkoutSession.query.get_or_404(session_id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout removed successfully"}), 200
    

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)