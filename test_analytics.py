from typing import Dict, List
from time import sleep

import Setup
import auth
from data_getter import DataGetter
import emailfunc


VIEW_DICT = {
    "Veg.co.il": Setup.VEG_VIEW_ID,
    "animals-org.il": Setup.ANIMALS_VIEW_ID,
    "etgar22.co.il": Setup.ETGAR22_VIEW_ID,
    "challenge22.co.il": Setup.CHALLENGE22_VIEW_ID,
    "all_challenges": Setup.ALL_CHALLENGES_VIEW_ID
}
DIMENSION = {
    'sessions': 'sessions',
    'event_label': 'eventLabel',
    'unique_event': 'uniqueEvents',
    'event_action': 'eventAction'
}

SESSIONS_DECREASE_FAILURE = -20
SIGN_UPS_DECREASE_FAILURE = -15
DONT_TEST_CHALLENGE_TYPE = ['Challenge22 - Hebrew Form Plugin', '(not set)']
### Email Const ###
SENDER = "me"
TO = "maor@animals-now.org"
USER_ID = "me"


def create_session_decreased_alert(website: str, view: str, period: int, decreased_by: float) -> str:
    session_decreased_msg = "##### SESSION DECREASE ALERT #####\n" \
                            "Website: {}\n" \
                            "Analytics view id: {}\n" \
                            "Period: {} days\n" \
                            "Decreased by: {}%\n" \
                            "Explanation: This message sent because the sessions on {} decreased " \
                            "by {}% in the last {} days compare to the {} days before.Which means there is far less " \
                            "visitors on the website in this period compare to the one before".format(website, view, period,
                                                                                                 decreased_by, website,
                                                                                                 decreased_by, period,
                                                                                                 period)
    return session_decreased_msg


def create_sign_ups_decreased_alert(challenge_type: str, view: str, period: int, decreased_by: float) -> str:
    session_decreased_msg = "##### SIGN UPS DECREASE ALERT #####\n" \
                            "Challenge Type: {}\n" \
                            "Analytics view id: {}\n" \
                            "Period: {} days\n" \
                            "Decreased by: {}%\n" \
                            "Explanation:\n" \
                            "This message sent because the sign ups of {} decreased " \
                            "by {}% in the last {} days compare to the {} days before. Which means there is far less " \
                            "sign ups on the challenge in this period compare to the one before."\
                            "That also might indicate the analytics sign ups event is broken. For each challenge " \
                            "there is a google sheet that contain all of the sign ups to this challenge. " \
                            "You can use this sheet to count the real number of sign ups and compare it to the " \
                            "number of sign up events in the analytics.".format(challenge_type, view, period,
                                                                                decreased_by, challenge_type,
                                                                                decreased_by, period, period)
    return session_decreased_msg


def calculate_change_percent(first_periods: float, second_periods: float) -> float:
    """
    Calculate the percent change from the first periods to the second one.
    :return: The change percent
    """
    delta = first_periods - second_periods
    if second_periods == 0:
        return 10000000000000
    return (delta / second_periods) * 100


def calculate_report_change_percent(report: Dict[str, List[int]]) -> Dict[str, float]:
    """
    Calculate the percent change from the first periods to the second one for each item in the report.
    :param report: for example:   { 'Challenge22 - English': ['410', '404'],
                                    'Challenge22 - Hebrew': ['513', '7137'],
                                    'Challenge22 - Spanish': ['35', '44']}
    :return: Dictionary with the change percent for each item.
    """
    change_dict = dict()
    for key, val in report.items():
        change_dict[key] = calculate_change_percent(int(val[0]), int(val[1]))
    return change_dict


def create_failure_dictionary(change_dict: Dict[str, float], decrease_bound: float) -> Dict[str, float]:
    """
    create failure dictionary and add all item with change percent below the decrease_bound
    :param change_dict: {item: change percent}
    :return: failure_dict
    """
    failure_dict = dict()
    for item, change_percent in change_dict.items():
        if change_percent <= decrease_bound:
            failure_dict[item] = change_percent
    return failure_dict


def get_session_decreased_failure(analytics_service: DataGetter, VIEW_DICT: Dict[str, str], start: int = 30, end: int = 0) ->\
        Dict[str, float]:
    """
    Check for each view if there is a decrease in sessions from given the period compare to the one before. If there is a
    decreased and it above the SESSIONS_DECREASE_FAILURE constant, the view will be add to the failure dictionary.
    :param analytics_service: Analytics Reporting API V4 service object.
    :param VIEW_DICT: analytic's views id dictionary
    :param start: first periods start date(int). example 30 = "30daysAgo".
    :param end: first periods end date(int). example 0 = "today".
    :return: failure dict - {view: change percent}
    """
    session_report = analytics_service.get_metric_report(VIEW_DICT, DIMENSION['sessions'], start=start, end=end)
    change_dict = calculate_report_change_percent(session_report)
    failure_dict = create_failure_dictionary(change_dict, SESSIONS_DECREASE_FAILURE)
    return failure_dict


def get_challenges_sign_ups_failure(analytics_service: DataGetter, view: str=Setup.ALL_CHALLENGES_VIEW_ID, start: int = 30,
                                    end: int = 0) -> Dict[str, float]:
    """

    Check for each challenge type if there is a decrease in sign ups from given the period compare to the one before.
    If there is a decreased and it above the SIGN_UPS_DECREASE_FAILURE constant, the challenge type will be add to the
    failure dictionary.
    :param analytics_service: Analytics Reporting API V4 service object.
    :param view: analytic's views id
    :param start: first periods start date(int). example 30 = "30daysAgo".
    :param end: first periods end date(int). example 0 = "today".
    :return: failure dict - {view: change percent}

    """
    sign_ups_report = analytics_service.get_metric_dimension_report(view, 'eventLabel', 'uniqueEvents', 'eventAction', 'EXACT',
                                                         'success', start=start, end=end)
    change_dict = calculate_report_change_percent(sign_ups_report)
    failure_dict = create_failure_dictionary(change_dict, SIGN_UPS_DECREASE_FAILURE)
    return failure_dict


def send_email_on_session_decreased_failure(gmail_service, failure_dict: Dict[str, float], period: int) -> None:
    for website, change_percent in failure_dict.items():
        decreased_by = -int(change_percent)
        subject = "{} - SESSIONS DECREASE ALERT".format(website)
        body = create_session_decreased_alert(website, VIEW_DICT[website], period, decreased_by)
        msg = emailfunc.create_message(SENDER, TO, subject, body)
        emailfunc.send_message(gmail_service, USER_ID, msg)
        sleep(3)


def send_email_on_sign_ups_decreased_failure(gmail_service, failure_dict: Dict[str, float], period: int,
                                             view: str=Setup.ALL_CHALLENGES_VIEW_ID) -> None:
    for challenge_type, change_percent in failure_dict.items():
        if challenge_type in DONT_TEST_CHALLENGE_TYPE:
            continue
        decreased_by = -int(change_percent)
        subject = "{} - SIGN UPS DECREASE ALERT".format(challenge_type)
        body = create_sign_ups_decreased_alert(challenge_type, view, period, decreased_by)
        msg = emailfunc.create_message(SENDER, TO, subject, body)
        emailfunc.send_message(gmail_service, USER_ID, msg)
        sleep(3)


                                         
                                         
def main():
    analytics_service = DataGetter()
    gmail_service = auth.get_service_gmail()
    
    #### WEEKLY TEST ####

    week_session_failure_dict = get_session_decreased_failure(analytics_service, VIEW_DICT, start=7, end=0)
    send_email_on_session_decreased_failure(gmail_service, week_session_failure_dict, 7)

    week_sign_ups_failure_dict = get_challenges_sign_ups_failure(analytics_service, start=7, end=0)
    send_email_on_sign_ups_decreased_failure(gmail_service, week_sign_ups_failure_dict, 7)

    #### MONTHLY TEST ####
    session_failure_dict = get_session_decreased_failure(analytics_service, VIEW_DICT, start=30, end=0)
    send_email_on_session_decreased_failure(gmail_service, session_failure_dict, 30)

    sign_ups_failure_dict = get_challenges_sign_ups_failure(analytics_service, start=30, end=0)
    send_email_on_sign_ups_decreased_failure(gmail_service, sign_ups_failure_dict, 30)


if __name__ == '__main__':
    main()