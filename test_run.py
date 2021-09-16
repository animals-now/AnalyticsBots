import Setup
import auth
from data_getter import DataGetter
import test_analytics

VIEW_DICT = {
    "Veg.co.il": Setup.VEG_VIEW_ID,
    "animals-org.il": Setup.ANIMALS_VIEW_ID,
    "etgar22.co.il": Setup.ETGAR22_VIEW_ID,
    "challenge22.co.il": Setup.CHALLENGE22_VIEW_ID,
    "all_challenges": Setup.ALL_CHALLENGES_VIEW_ID
}
analytics_service = DataGetter()
gmail_service = auth.get_service_gmail()

if Setup.WEEKLY_TEST == 'True' or Setup.WEEKLY_TEST == 'true':
    week_session_failure_dict = test_analytics.get_session_decreased_failure(analytics_service,
                                                                             VIEW_DICT, start=7, end=0)
    test_analytics.send_email_on_session_decreased_failure(gmail_service, week_session_failure_dict, 7)

    week_sign_ups_failure_dict = test_analytics.get_challenges_sign_ups_failure(analytics_service, start=7, end=0)
    test_analytics.send_email_on_sign_ups_decreased_failure(gmail_service, week_sign_ups_failure_dict, 7)

if Setup.MONTHLY_TEST == 'True' or Setup.MONTHLY_TEST == 'true':
    week_session_failure_dict = test_analytics.get_session_decreased_failure(analytics_service,
                                                                             VIEW_DICT, start=30, end=0)
    test_analytics.send_email_on_session_decreased_failure(gmail_service, week_session_failure_dict, 30)

    week_sign_ups_failure_dict = test_analytics.get_challenges_sign_ups_failure(analytics_service, start=30, end=0)
    test_analytics.send_email_on_sign_ups_decreased_failure(gmail_service, week_sign_ups_failure_dict, 30)
