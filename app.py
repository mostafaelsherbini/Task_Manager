from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # غيّرها في مشروع حقيقي
db = SQLAlchemy(app)
jwt = JWTManager(app)

# جدول المستخدمين
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship("Task", backref="owner", lazy=True)

# جدول المهام
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed}

with app.app_context():
    db.create_all()

# تسجيل مستخدم جديد
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        abort(400, description="Username and password are required")
    if User.query.filter_by(username=data["username"]).first():
        abort(400, description="User already exists")
    hashed = generate_password_hash(data["password"])
    user = User(username=data["username"], password=hashed)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

# تسجيل الدخول
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password, data["password"]):
        abort(401, description="Invalid credentials")
    token = create_access_token(identity=str(user.id))  # نبعته String
    return jsonify({"token": token})

# جلب المهام الخاصة بالمستخدم الحالي
@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())  # نرجعه int
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks])

# إضافة مهمة جديدة
@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())  # نرجعه int
    data = request.get_json()
    if not data or "title" not in data:
        abort(400, description="Title is required")
    t = Task(title=data["title"], user_id=user_id)
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

if __name__ == "__main__":
    app.run(debug=True)
