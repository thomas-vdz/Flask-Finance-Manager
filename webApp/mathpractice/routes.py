from flask import Blueprint
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from webApp import db
from webApp.models import Theorem
from webApp.mathpractice.forms import MathForm , MathFormProgress
import random


mathpractice = Blueprint('mathpractice', __name__)


@mathpractice.route("/mathpractice/add_theorem" , methods=['GET','POST'] )
@login_required
def add_theorem():
     form = MathForm()
     if form.validate_on_submit():
         theorem = Theorem(title= form.title.data, course=form.course.data, chapter=form.chapter.data, theorem_latex=form.theorem_latex.data, 
         proof_latex=form.proof_latex.data, hint= form.hint.data, difficulty=form.difficulty.data, progress="Not learned", author=current_user)
         db.session.add(theorem)
         db.session.commit()
         flash('Theorem added','success')
         return redirect(url_for('mathpractice.add_theorem'))
     return render_template('create_theorem.html',title='New Theorem' , form=form ,
                            legend='New Theorem' )
 


@mathpractice.route("/mathpractice/display_theorems" , methods=['GET','POST'] )
def show_theorems():
    theorems = Theorem.query.all()


    return render_template('display_theorems.html',title='Theorems' , theorems=theorems ,
                            legend='boeie ruurd', no_sidebar = True )



@mathpractice.route("/mathpractice/practice_theorem/<int:theorem_id>" , methods=['GET','POST'] )
def practice_theorem(theorem_id):
    theorem = Theorem.query.get_or_404(theorem_id)
    form = MathFormProgress()

    theorems = Theorem.query.filter(Theorem.progress.isnot('Mastered')).all()
    len_theorems = len(theorems)

    if form.submit_next.data and form.validate_on_submit():
        #Saves progress
        theorem.progress = form.progress.data
        db.session.commit()

        
        

        if len_theorems == 1 and form.progress.data == 'Mastered':
            flash('Congratulations you have mastered all theorems','success')
            return redirect(url_for('mathpractice.show_theorems'))

        else:
            #Prevents it from picking itself if it happens to be the first theorem
            if theorem_id == theorems[0].id:
                next_theorem = theorem_id+1
            else:
                next_theorem = theorems[0].id

            return redirect(url_for('mathpractice.practice_theorem', theorem_id=next_theorem))

    elif form.submit_random.data and form.validate_on_submit():
        #Saves progress
        theorem.progress = form.progress.data
        db.session.commit()


        if len_theorems == 1 and form.progress.data == 'Mastered':
            flash('Congratulations you have mastered all theorems','success')
            return redirect(url_for('mathpractice.show_theorems'))
        else:
            #Picks a random theorem 
            t = theorems[random.randint(0,len_theorems - 1)]

            #Prevents it from picking itself and picking a non existant one if its the last and it happends to pick itself 
            if theorem_id == t.id and theorem_id != theorems[-1].id:
                rand_theorem = theorem_id+1
            else:
                rand_theorem = t.id
                    
            return redirect(url_for('mathpractice.practice_theorem', theorem_id = rand_theorem))

    elif request.method == 'GET':
        form.progress.data = theorem.progress
            


    return render_template('practice_theorem.html',title='Theorems' , theorem=theorem ,
                            legend='boeie ruurd', form=form, no_sidebar = True , left=len_theorems)

@mathpractice.route("/mathpractice/<int:theorem_id>/update", methods=['GET','POST'])
@login_required
def update_theorem(theorem_id):
    theorem = Theorem.query.get_or_404(theorem_id)
    if theorem.author != current_user:
        abort(403)
    form = MathForm()
    if form.validate_on_submit():
        theorem.title = form.title.data
        theorem.course = form.course.data
        theorem.theorem_latex = form.theorem_latex.data
        theorem.proof_latex = form.proof_latex.data
        theorem.hint = form.hint.data
        theorem.difficulty = form.difficulty.data

        db.session.commit()
        flash('Your thoerem has been updated!', 'success')
        return redirect(url_for('mathpractice.practice_theorem', theorem_id=theorem_id ))
    elif request.method == 'GET':
        form.title.data = theorem.title
        form.course.data = theorem.course
        form.chapter.data = theorem.chapter
        form.theorem_latex.data = theorem.theorem_latex
        form.proof_latex.data = theorem.proof_latex
        form.hint.data = theorem.hint
        form.difficulty.data = theorem.difficulty
    return render_template('create_theorem.html',title='Update Post' , 
                           form=form , legend='Update Post')




@mathpractice.route("/mathpractice/<int:theorem_id>/delete", methods=['POST'])
def delete_theorem(theorem_id):
    theorem= Theorem.query.get_or_404(theorem_id)
    if theorem.author != current_user:
        abort(403)
    
    db.session.delete(theorem)
    db.session.commit()
    flash('Theorem deleted!', 'success')
    return redirect(request.referrer)


