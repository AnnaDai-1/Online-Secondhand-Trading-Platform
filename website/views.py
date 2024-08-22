from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from website import db
from werkzeug.utils import secure_filename
from.models import Item, User, Image, Comment
import os


views = Blueprint('views', __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    items = Item.query.all()
    image_sources = [f'/website/static/UPLOAD_FOLDER/{Image.filename}' for item in items]
    return render_template("home.html", user=current_user, items = items, image_sources=image_sources)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@views.route('/post_item', methods=['GET', 'POST'])
@login_required
def create_post():
    filename=None
    filenames = []
    
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        images = request.files.getlist('files[]')  # Use getlist to get multiple files
        price = request.form.get('price')
        available = request.form.get('available')
        if not title:
            flash('Title cannot be empty', category='error')
       
        elif not description:
            flash('Description cannot be empty', category='error')
        elif not price:
            flash('Price cannot be empty.', category='error')
        elif not images or not all(allowed_file(image.filename) for image in images):
            flash('Invalid or missing image', category='error')
        else:
            if available == 'available':
                item = Item(title=title, description=description, price=price, state=True, user_id=current_user.id)
            else:
                item = Item(title=title, description=description, price=price, state=False, user_id=current_user.id)

            for image in images:
                # Process each image and save it to the server
                filename = secure_filename(image.filename)
                image.save(os.path.join('website/static/img', filename))
                filenames.append(filename)

            # Set the thumbnail field to the first filename in the list
            if filenames:
                item.thumbnail = filenames[0]

            # Save the post with the image filenames
            for filename in filenames:
                item.images.append(Image(filename=filename))

            
               
            # Add the post to the database
            db.session.add(item)
            db.session.commit()

            flash('Item posted!', category='success')
            return redirect(url_for('views.home'))

    return render_template('post_item.html', user=current_user, filename=filename)

@views.route("/delete-item/<id>")
@login_required
def delete_item(id):
    item= Item.query.filter_by(id=id).first()
    if not item:
        flash("Item does not exist.", category="error")
    elif current_user.id != item.user_id:
        flash('You do not have permission to delete this item.', category="error")
    else:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted.', category='success')

    return redirect(url_for('views.home'))

@views.route("/items/<user_id>")
@login_required
def items(user_id):
    user=User.query.filter_by(id=user_id).first()
    if not user:
        flash('No user with that user id exists.', category='error')
        return redirect(url_for('views.home'))
    items= user.items
    username = user.username

    return render_template("items.html", user=current_user, items=items, user_id = user_id, username=username)

@views.route("/single_item/<item_id>")
@login_required
def single_item(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if not item:
        flash('No item with that id exists.', category='error')
        return redirect(url_for('views.home'))
    title=item.title
    description=item.description
    price=item.price
    images=item.images
    state=item.state
    
    return render_template("single_item.html", item=item, title=title, description=description, price=price, images=images, state=state, user=current_user)
    


@views.route("/search", methods=['POST', 'GET'])
@login_required
def search():
    if request.method=="POST":
        keyword= request.form.get('search')
        items=[]
        item = Item.query.all()
        for i in item:
            if keyword.lower() in i.title.lower() or keyword == str(i.user_id):  # Case-insensitive search
                items.append(i)
        
        if not items:
            flash('No items or username found.', category='error')
            return redirect(url_for('views.home'))
    
        items = items

    return render_template("search_result.html", items=items, user=current_user)


@views.route("/edit/<item_id>", methods=['POST', 'GET'])
@login_required
def edit_item(item_id):
    item=Item.query.get(item_id)
    filenames=[]
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        images = request.files.getlist('files[]')  # Use getlist to get multiple files
        price = request.form.get('price')
        available = request.form.get('available')
        if title:
            item.title=title
        if  description:
            item.description=description
        if price:
            item.price=price
        if images and all(allowed_file(image.filename) for image in images):
            
            for image in images:
                # Process each image and save it to the server
                filename = secure_filename(image.filename)
                image.save(os.path.join('website/static/img', filename))
                filenames.append(filename)

            # Set the thumbnail field to the first filename in the list
            if filenames:
                item.thumbnail = filenames[0]

            # Save the post with the image filenames
            for filename in filenames:
                item.images.append(Image(filename=filename))
        if available == 'available':
            item.state = True
        elif available != 'available':
            item.state = False

        else:
            flash('Please enter at least one field to make change to the item.')
            
               
            
            
        db.session.commit()

        flash('Item edited!', category='success')
        return redirect(url_for('views.home'))

    return render_template('edit.html', user=current_user, item=item)


@views.route("/create_comment/<item_id>", methods=['POST'])
def create_comment(item_id):
    text=request.form.get('text')
    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        item = Item.query.get(item_id)
        if item:
            comment = Comment(text=text, author=current_user.id, item_id=item_id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment created!', category='success')
        else:
            flash('Item does not exist.', category='error')


    return redirect(url_for('views.home'))


@views.route("/delete_comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment=Comment.query.get(comment_id)
    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author:
        flash('You do not have permission to delete this comment.')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))