from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv 


app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR SECRET KEY'
Bootstrap(app)


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    location = StringField("Cafe location on google maps (URL)", validators=[DataRequired(), URL()])
    open = StringField("Opening Time e.g. 8AM", validators=[DataRequired()])
    close = StringField("Opening Time e.g. P.M.", validators=[DataRequired()])
    coffe_rating = SelectField("Coffe Rating", choices=["☕", "☕☕", "☕☕☕", "☕☕☕☕", "☕☕☕☕☕"], validators=[DataRequired()])
    wifi_rating = SelectField("Wifi Stregth rating", choices=["✖️", "💪","💪💪", "💪💪💪", "💪💪💪💪", "💪💪💪💪💪"], validators=[DataRequired()] )
    power_rating = SelectField("Power Socket Availability", choices=["✘", "🔌", "🔌🔌", "🔌🔌🔌", "🔌🔌🔌🔌", "🔌🔌🔌🔌🔌"],
                               validators=[DataRequired()])

    submit = SubmitField('Submit')



# all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():


        with open('./static/data/cafe-data.csv',mode='a', newline='', encoding='utf-8') as csv_file:
            csv_file.write(f"\n{form.cafe.data},"
                           f"{form.location.data}, "
                           f"{form.open.data},"
                           f"{form.close.data},"
                           f"{form.coffe_rating.data},"
                           f"{form.wifi_rating.data},"
                           f"{form.power_rating.data}")


            return redirect(url_for('cafes'))
    # Exercise:

    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('./static/data/cafe-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        length = 0
        for row in csv_data:
            length += 1
            list_of_rows.append(row)
        # print(list_of_rows)
    return render_template('cafes.html', cafes=list_of_rows, n=length)


if __name__ == '__main__':
    app.run(debug=True)
