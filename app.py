from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف جدول المهام
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "completed": self.completed}

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# جلب كل المهام
@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])

# إضافة مهمة جديدة
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data:
        abort(400, description="Title is required")
    t = Task(title=data["title"])
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

# تحديث مهمة
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    t = Task.query.get_or_404(task_id)
    if "title" in data:
        t.title = data["title"]
    if "completed" in data:
        t.completed = bool(data["completed"])
    db.session.commit()
    return jsonify(t.to_dict())

# حذف مهمة
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200

@app.route("/tasks/count", methods=["GET"])
def task_count():
    count = Task.query.count()
    return jsonify({"count": count})


if __name__ == "__main__":
    app.run(debug=True)
