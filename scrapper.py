import csv
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone

import requests
from lxml import html as parser


def allow_debug_info(record):
    if record.levelno > 20:
        return 0
    else:
        return 1


def get_webpage_html(url):
    # Network error exception in case we lose network or page goes down etc.
    try:
        html = requests.get(url)
    except requests.ConnectionError:
        logger.error('Connection Error occured')
        return False

    return html


def check_reservation_availability(html):
    tree = parser.fromstring(html.content)
    appointments = tree.xpath('//div[@id="dnn_ctr484_MakeReservation_availabilityTableCell"]//*[@class="DNNSpecialists_Modules_Reservations_Normal"]')  # noqa: E501
    timestamp = datetime.now(timezone.utc).strftime('%d-%m-%Y %H:%M:%S %Z')
    csv_log = [timestamp]
    debug_log = [timestamp]
    regex = r'(\d+)\s+από\s+(\d{1,2}/\d{1,2}/\d{4})'
    logger.info(timestamp)

    # Loop to extract text from every element of appointments list.
    # text variable may look different depending on availability
    # It can be:
    # 1. Greek Passports (NO VISAS) - Διαβατήρια: Προς το παρόν δεν υπάρχει Διαθεσιμότητα.    # noqa: E501
    # or 2. Power of Attorney - Πληρεξούσια Διαθέσιμα 2  από  8/9/2017
    military_appointment_date = None
    for appointment in appointments:
        text = appointment.text_content()
        debug_log.append(text)
        logger.info(text)

        # Check for availability of every appointment type and if True
        # and if True add date in csv_log, else add empty value.
        if 'Διαθέσιμα' in text:
            m = re.search(regex, text)
            available_appointment_number = m.group(1)
            available_appointment_date = m.group(2)

            csv_log.append(available_appointment_date)

            # Check when we have availability if it is for Military Affairs.
            if 'Military Affairs' in text:
                logger.info(
                    'Found for Military Affairs: '
                    f'{available_appointment_number} ραντεβού '
                    f'@ {available_appointment_date}'
                )
                military_appointment_date = available_appointment_date
        else:
            csv_log.append('')

    with open(f'{os.getcwd()}/data.csv', 'a', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(csv_log)

    with open(f'{os.getcwd()}/data.log', 'a') as fh:
        for line in debug_log:
            fh.write('{}\n'.format(line))

        fh.write('\n')

    return military_appointment_date


def send_availability_notification(date, mailgun_conf):
    data = {
        'from': f'Greek Embassy London <postmaster@{mailgun_conf["DOMAIN_NAME"]}>',  # noqa: E501
        'to': mailgun_conf['RECEIVER_EMAIL'],
        'subject': 'Διαθέσιμα Ραντεβού στην Πρεσβεία',
        'text': (
            f'Υπάρχουν διαθέσιμα ραντεβου για Στρατολογικά από {date}'
            'Ακολουθείστε τον παρακάτω σύνδεσμο για να κλείσετε το ραντεβού:',
            'http://www.greekembassy.org.uk/el-gr/Reservations'
        )
    }
    ret = requests.post(
        f'https://api.mailgun.net/v3/{mailgun_conf["DOMAIN_NAME"]}/messages',
        auth=('api', mailgun_conf["MAILGUN_API_KEY"]),
        data=data
    )
    return ret


logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

out_handler = logging.StreamHandler(stream=sys.stdout)
out_handler.addFilter(allow_debug_info)
err_handler = logging.StreamHandler()
err_handler.setLevel(logging.WARNING)
logger.addHandler(out_handler)
logger.addHandler(err_handler)

with open('mailgun.conf') as mailgun_json:
    mailgun_conf = json.load(mailgun_json)

url = 'http://www.greekembassy.org.uk/el-gr/Reservations'
html = get_webpage_html(url)

# First if checks if we got the html code or we encountered a network error.
if html:
    reservation_date = check_reservation_availability(html)
    # Second if checks if there was availability.
    if reservation_date:
        send_availability_notification(reservation_date, mailgun_conf)
else:
    logger.info('Unable to check reservations.')

logger.info('Done.')
