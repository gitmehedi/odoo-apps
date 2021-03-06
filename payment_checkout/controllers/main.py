# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CheckoutController(http.Controller):

    @http.route(['/payment/checkout/s2s/create_json'], type='json', auth='public')
    def checkout_s2s_create_json(self, **kwargs):
        acquirer_id = int(kwargs.get('acquirer_id'))
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        return acquirer.s2s_process(kwargs)

    @http.route(['/payment/checkout/s2s/create'], type='http', auth='public')
    def checkout_s2s_create(self, **post):
        acquirer_id = int(post.get('acquirer_id'))
        acquirer = request.env['payment.acquirer'].browse(acquirer_id)
        acquirer.s2s_process(post)
        return werkzeug.utils.redirect(post.get('return_url', '/'))

    @http.route(['/payment/checkout/create_charge'], type='json', auth='public')
    def checkout_create_charge(self, **post):
        """ Create a payment transaction

        Expects the result from the user input from checkout.js popup"""
        tx = request.env['payment.transaction'].sudo().browse(
            int(request.session.get('sale_transaction_id') or request.session.get('website_payment_tx_id', False))
        )
        response = tx._create_checkout_charge(tokenid=post['tokenid'], email=post['email'])
        _logger.info('Checkout: entering form_feedback with post data %s', pprint.pformat(response))
        if response:
            request.env['payment.transaction'].sudo().with_context(lang=None).form_feedback(response, 'checkout')
        return post.pop('return_url', '/')
