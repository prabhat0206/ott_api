from flask import Blueprint, request, jsonify
from . import auth
from .models import *

payment_api = Blueprint('payment_api', __name__)


@payment_api.route('/api/addcard/', methods=['POST'])
@payment_api.route('/api/addcard', methods=['POST'])
@auth.login_required()
def add_card():
    try:
        data = request.get_json()
        card_number = str(data['card_number'])
        exp_month = int(data["exp_month"])
        exp_year = int(data["exp_year"])
        cvv = str(data["cvv"])
        cid = auth.current_user()
        user = User_table.query.filter_by(customer_id=cid).first()
        cards = stripe.PaymentMethod.list(
                    customer=user.stripe_cus_id,
                    type="card",
                )['data']
        if len(cards)>0:
            for temp_card in cards:
                stripe.PaymentMethod.detach(
                    temp_card['id'],
                    )
        card = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvv,
            }
        )
        stripe.PaymentMethod.attach(
            card["id"],
            customer=user.stripe_cus_id,
        )
        return jsonify({'success': True})
    except stripe.error.StripeError as e:
        return jsonify({'success': False, 'error': e.user_message})


@payment_api.route('/api/make_payment', methods=['POST'])
@payment_api.route('/api/make_payment/', methods=['POST'])
@auth.login_required()
def make_payment():
    try:
        data = request.get_json()
        amount = int(data['amount']) * 100
        cid = auth.current_user()
        user = User_table.query.filter_by(customer_id=cid).first()
        cards = stripe.PaymentMethod.list(
                    customer=user.stripe_cus_id,
                    type="card",
                )['data']
        if len(cards) <= 0:
            return jsonify({'success': False, 'error': 'Please add a card'})
        payment = stripe.PaymentIntent.create(
            amount=amount,
            currency='inr',
            payment_method=str(cards[0]['id']),
            payment_method_types=["card"],
            customer=user.stripe_cus_id,
            confirm=True
        )

        return jsonify({'success': True, 'url': payment['next_action']['use_stripe_sdk']['stripe_js']})
    except stripe.error.StripeError as e:
        return jsonify({'success': False, 'error': e.user_message})