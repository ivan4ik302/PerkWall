from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.core.signing import Signer
from django.core import signing
from django.http import Http404
from account.models import UserSubscription, UserProduct, UserBillProduct, UserBillSubscription
from django.core.exceptions import ObjectDoesNotExist
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import datetime
import json


@require_GET
@login_required
def payment_main(request):
    token = request.GET.get('token', None)
    token_object = None
    item_object = None
    if token is not None:
        try:
            signer = Signer()
            token_object = signer.unsign_object(token)
        except signing.BadSignature:
            raise Http404

        if token_object['type'] == 'product':
            try:
               item_object = UserProduct.objects.all().get(id=token_object['id'])

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

            try:
                UserBillProduct.objects.all().get(product=item_object)
                raise Http404()

            except ObjectDoesNotExist:
                pass

        elif token_object['type'] == 'subscription':
            try:
               item_object = UserSubscription.objects.all().get(id=token_object['id'])

            except (ObjectDoesNotExist, ValueError):
                raise Http404()

            try:
                UserBillSubscription.objects.all().get(subscription=item_object)
                raise Http404()

            except ObjectDoesNotExist:
                pass

        Configuration.account_id = '871121'
        Configuration.secret_key = 'test_Twivp65mUUBJt1CK4SlQDGg4ceQkiqHbYvcMqjh4TDo'
        payment = Payment.create({
            "amount": {
                "value": str(item_object.price),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://perkwall.com/dashboard/account"
            },
            "capture": True,
            "metadata": {
                'type': token_object['type'],
                'item_id': token_object['id'],
                'user_id': request.user.id
            }
        })
        if payment.status == 'pending':
            return redirect(payment.confirmation.confirmation_url)

        else:
            raise Exception()

    raise Http404

@csrf_exempt
@require_POST
def payment_webhook(request):
    event_json = json.loads(request.body)
    notification_object = WebhookNotificationFactory().create(event_json)
    response_object = notification_object.object
    if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
        some_data = {
            'paymentId': response_object.id
        }
    elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
        some_data = {
            'paymentId': response_object.id
        }
    elif notification_object.event == WebhookNotificationEventType.REFUND_SUCCEEDED:
        some_data = {
            'paymentId': response_object.payment_id
        }
    else:
        return HttpResponse(status=400)

    Configuration.configure('871121', 'test_Twivp65mUUBJt1CK4SlQDGg4ceQkiqHbYvcMqjh4TDo')
    payment_info = Payment.find_one(some_data['paymentId'])
    if payment_info:
        if payment_info.status == 'succeeded':
            if payment_info.metadata['type'] == 'product':
                try:
                    product = UserProduct.objects.all().get(id=payment_info.metadata['item_id'])
                    user = User.objects.all().get(id=payment_info.metadata['user_id'])
                    UserBillProduct.objects.create(user=user, product=product)

                except ObjectDoesNotExist:
                    pass

            elif payment_info.metadata['type'] == 'subscription':
                try:
                    subscription = UserSubscription.objects.all().get(id=payment_info.metadata['item_id'])
                    user = User.objects.all().get(id=payment_info.metadata['user_id'])
                    expires = datetime.datetime.utcnow() + datetime.timedelta(days = 30)
                    UserBillSubscription.objects.create(user=user, subscription=subscription, expires=expires)

                except ObjectDoesNotExist:
                    pass

    else:
        return HttpResponse(status=400)

    return HttpResponse(status=200)