from flask import Blueprint
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from webApp import db
from webApp.models import Theorem
from webApp.mathpractice.forms import MathForm

mathpractice = Blueprint('mathpractice', __name__)


@mathpractice.route("/mathpractice/add_theorem" , methods=['GET','POST'] )
def add_theorem():
     form = MathForm()
     if form.validate_on_submit():
         theorem = Theorem(title= form.title.data, course=form.course.data, chapter=form.chapter.data, theorem_latex=form.theorem_latex.data, proof_latex=form.proof_latex.data, hint= form.hint.data, difficulty=form.difficulty.data)
         db.session.add(theorem)
         db.session.commit()
         flash('Theorem added','success')
         return redirect(url_for('main.home'))
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
    return render_template('practice_theorem.html',title='Theorems' , theorem=theorem ,
                            legend='boeie ruurd', no_sidebar = True )


@mathpractice.route("/mathpractice/<int:theorem_id>/delete", methods=['POST'])
def delete_theorem(theorem_id):
    theorem= Theorem.query.get_or_404(theorem_id)
    db.session.delete(theorem)
    db.session.commit()
    flash('Theorem deleted!', 'success')
    return redirect(request.referrer)

'''    
@mathpractice.route("/mathpractice/<int:post_id>")
def post(post_id):
    post= Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title , post=post)

@mathpractice.route("/mathpractice/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post= Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id ))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',title='Update Post' , 
                           form=form , legend='Update Post')

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post= Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

'''
