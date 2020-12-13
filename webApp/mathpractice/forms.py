from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired


class MathForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    course = SelectField('Course', choices=[('Mathematics 4','Mathematics 4')] , default='Mathematics 4')
    chapter = StringField('Chapter', validators=[DataRequired()])
    theorem_latex = TextAreaField('Theorem_latex',  validators=[DataRequired()] )
    proof_latex = TextAreaField('Proof_latex',  validators=[DataRequired()] )
    hint = StringField('Hint')
    difficulty = RadioField('Difficulty', choices=[('Easy','Easy'),('Difficult','Difficult'),('Hard','Hard')], default = 'Easy')
    submit = SubmitField('Add')

