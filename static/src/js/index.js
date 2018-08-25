/* global window document */
window.jQuery = window.$ = require('jquery');

const $ = window.$;

require('bootstrap/dist/js/bootstrap.bundle');

import ajaxSendMethod from './ajax';
import handleMessageDismiss from './messages';
import loadStripeElements from './apps/pinax-stripe';

$(() => {
    $(document).ajaxSend(ajaxSendMethod);

    // Topbar active tab support
    $('.topbar li').removeClass('active');

    const classList = $('body').attr('class').split(/\s+/);
    $.each(classList, (index, item) => {
        const selector = `ul.nav li#tab_${item}`;
        $(selector).addClass('active');
    });

    $('#account_logout, .account_logout').click(e => {
        e.preventDefault();
        $('#accountLogOutForm').submit();
    });

    handleMessageDismiss();
    loadStripeElements();
});

$(() => {
    if($('#id_3-certificat').length) {
        $('form').on('submit', e => {
            if (!$('#id_3-certificat').val() && !$('#id_3-cerfa_non')[0].checked) {
                alert('Vous devez forunir un certificat médical pour continuer');
                e.preventDefault();
            }
        });
    }
});
