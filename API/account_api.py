from flask import Blueprint, request, jsonify, abort
from .models import User_table, Movie
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, get_model_dict, auth, client

account_api = Blueprint('account_api', __name__)


@account_api.route('/api/register/', methods=['POST'])
@account_api.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = str(data['full_name'])
    dob = data['DOB']
    password = data['password']
    Gender = data['Gender']

    # if 'email' in data:
    #     email = data['email']
    #     user = User_table.query.filter_by(email=email).first()
    #     if user:
    #         return jsonify({"success": False, 'error': 'Email already exists, Try to Login.'})
    #     elif "@" not in email:
    #         return jsonify({"success": False, 'error': 'Enter a valid Email'})
    #     razorpay_data = {
    #         'name': full_name,
    #         'email': email
    #     }
    #     response = client.customer.create(data=razorpay_data)
    #     new_user = User_table(
    #         email=email,
    #         full_name=full_name,
    #         password=generate_password_hash(
    #             password, method='sha256'),
    #         DOB=dob,
    #         Gender=Gender,
    #         razorpay_id=response['id']
    #     )
    #     db.session.add(new_user)
    #     db.session.commit()
    try:
        if 'Ph_number' in data:
            Ph_number = data['Ph_number']
            user_number = User_table.query.filter_by(Ph_number=Ph_number).first()
            if user_number:
                return jsonify({"success": False, 'error': 'Phone number is already registered with other user .'})
            elif "+" not in Ph_number:
                return jsonify({"success": False, 'error': 'Enter phone number with country code'})
            razorpay_data = {
                'name': full_name,
                'contact': Ph_number,
            }
            response = client.customer.create(data=razorpay_data)

            new_user = User_table(
                password=generate_password_hash(
                    password, method='sha256'),
                Ph_number=Ph_number,
                DOB=dob,
                Gender=Gender,
                membership='Free',
                razorpay_id=response['id']
            )
            db.session.add(new_user)
            db.session.commit()
        return jsonify({"success": True, "sha": new_user.password, "user_id": new_user.uid})
    except Exception:
        abort(500)


@account_api.route('/api/login/', methods=['POST'])
@account_api.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data['password']
    if 'Ph_number' in data:
        Ph_number = data['Ph_number']
        user = User_table.query.filter_by(Ph_number=Ph_number).first()

    if not user:
        return jsonify({"success": False, 'error': 'Phone number is not registered with us.'})

    if check_password_hash(user.password, password):
        return jsonify({"success": True, "sha": user.password, "user_id": user.uid})
    else:
        return jsonify({"success": False, 'error': 'Incorrect password, try again.'})


@account_api.route('/api/editCustomer/', methods=['POST'])
@account_api.route('/api/editCustomer', methods=['POST'])
@auth.login_required()
def edit_customer():
    data = request.get_json()
    Profile_pic = data['Profile_pic']
    uid = auth.current_user()
    user = User_table.query.filter_by(uid=uid).first()
    user.profile_pic = Profile_pic
    db.session.commit()
    return jsonify({'success': True})


@account_api.route('/api/editPassword/', methods=['POST'])
@account_api.route('/api/editPassword', methods=['POST'])
def edit_password():
    data = request.get_json()
    if 'Ph_number' in data:
        Ph_number = data['Ph_number']
        user = User_table.query.filter_by(Ph_number=Ph_number).first()
    elif 'email' in data:
        email = data['email']
        user = User_table.query.filter_by(email=email).first()
    old_password = data['old_password']
    new_password = data['new_password']
    if user:
        if check_password_hash(user.password, old_password):
            user.password = generate_password_hash(
                            new_password, method='sha256')
            db.session.commit()
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, 'error': 'Incorrect password, try again.'})
    else:
        return jsonify({"success": False, 'error': 'Email is not registered  with us.'})


@account_api.route('/api/getuserdetails/', methods=['POST'])
@account_api.route('/api/getuserdetails', methods=['POST'])
@auth.login_required()
def get_user_details():
    uid = auth.current_user()
    user = User_table.query.filter_by(uid=uid).first()
    final_details = dict()
    if user:
        final_details['success'] = True
        final_details['Details'] = get_model_dict(user)
        del final_details['Details']['password'], final_details['Details']['razorpay_id']
        return jsonify(final_details)
    else:
        return jsonify({'success': False})


@account_api.post("/api/getWatchlist")
@auth.login_required()
def getWatchlist():
    uid = auth.current_user()
    user = User_table.query.filter_by(uid=uid).first()
    if user:
        all_watchlist = []
        for watchlist in user.watchlist:
            watch = dict()
            watch["mid"] = watchlist.mid
            watch['image_url'] = watchlist.image_url
            watch['name'] = watchlist.name
            watch['description'] = watchlist.description
            watch['language'] = watchlist.Language
            all_watchlist.append(watch)
        return jsonify({'success': True, "movies": all_watchlist})
    return jsonify({'success': False})


@account_api.post("/api/removeFromWatchlist")
@auth.login_required()
def removeFromWatchlist():
    data = request.get_json()
    movie = Movie.query.filter_by(mid=data['mid']).first()
    user = User_table.query.filter_by(uid=auth.current_user()).first()
    if user and movie:
        if movie in user.watchlist:
            user.watchlist.remove(movie)
            db.session.commit()
            return jsonify({'success': True, "message": "Removed movie from watchlist"})
        return jsonify({'success': False, "message": "movie not in watchlist"})
    return jsonify({'success': False, "message": "user or movie not exist"})

@account_api.post("/api/addToWatchlist")
@auth.login_required()
def addToWatchlist():
    data = request.get_json()
    user = User_table.query.filter_by(uid=auth.current_user()).first()
    movie = Movie.query.filter_by(mid=data['mid']).first()
    if user and movie:
        if movie not in user.watchlist:
            user.watchlist.append(movie)
            db.session.commit()
            return jsonify({"success": True, "message": "Movie added successfully"})
        return jsonify({"success": False, "message": "Movie already in watchlist"})
    return jsonify({"success": False, "message": "Movie or User not exist"})


@account_api.post("/api/forgetPassword")
def forgetPassword():
    try:
        if request.headers['Authorization'] == "e8093cbc1686fa7d876e950047b66d230c9855ce5f52e2398c299bc10b1e1ca1":
            data = request.get_json()
            password = data['password']
            confirm_password = data['confirm_password']
            if password == confirm_password:
                user = User_table.query.filter_by(Ph_number=data['Ph_number']).first()
                user.password = generate_password_hash(password, method='sha256')
                db.session.commit()
                return jsonify({'success': True, "message": "Password changed successfully"})
            else:
                return jsonify({"success": False, 'error': 'password not matching'})
        else:
            abort(401)
    except:
        abort(401)

