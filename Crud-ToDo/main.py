import datetime
import os

import flask
import flask_sqlalchemy

app = flask.Flask(__name__)
base_directory = path = os.path.dirname(os.path.realpath(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_directory, 'data.sqlite')
db = flask_sqlalchemy.SQLAlchemy(app)


class ToDo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.DateTime, nullable=False)
	message = db.Column(db.Text, nullable=False)

	def __init__(self, **kwargs):
		super(ToDo, self).__init__(**kwargs)

	def __repr__(self):
		return '<ToDo %s>' % self.date


@app.route("/", methods=["GET", "POST"])
def home():
	if flask.request.method == "GET":
		return flask.render_template("home.html")
	else:
		try:
			form_data = flask.request.form
			date, message = datetime.datetime.strptime(form_data["date"], "%Y-%m-%d"), form_data["comment"]
			todo = ToDo(date=date, message=message)
			db.session.add(todo)
			db.session.commit()
			return flask.render_template("home.html",
			                             info=dict(
				                             message="Saved the item under ID: %s" % todo.id,
				                             status="Saved successfully"),
			                             submission=True
			                             )
		except BaseException as e:
			print(e)
			return flask.render_template("home.html",
			                             info=dict(message=e.__str__(), status="Failed to save"),
			                             submission=True)


@app.route("/show", methods=["GET"])
def show_all():
	all_todos = ToDo.query.all()
	return flask.render_template("show.html", todos=all_todos)


@app.route("/delete/<int:id>", methods=["GET"])
def delete(id):
	todo = ToDo.query.get_or_404(id)
	db.session.delete(todo)
	db.session.commit()
	return flask.redirect("/show")


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
	todo = ToDo.query.get_or_404(id)
	if flask.request.method == "GET":
		return flask.render_template("home.html", todo=todo)
	elif flask.request.method == "POST":
		form_data = flask.request.form
		todo.date, todo.message = datetime.datetime.strptime(form_data["date"], "%Y-%m-%d"), form_data["comment"]
		db.session.commit()
		return flask.render_template("home.html",
		                             info=dict(
			                             message="Updated the item under ID: %s" % todo.id,
			                             status="Updated successfully"),
		                             submission=True
		                             )
	else:
		return flask.redirect("/")


db.create_all()

if __name__ == "__main__":
	app.run(debug=True, Threaded=True, host="0.0.0.0")
