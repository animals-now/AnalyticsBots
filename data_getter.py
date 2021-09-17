from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import Setup
import auth

class DataGetter:
    """
    The purpose of this class is to easily get data from Google Analytics API.
    In some methods you need to supply dimension and metrics, in order to search for dimension or metric use
    this link: https://ga-dev-tools.web.app/dimensions-metrics-explorer/
    notice that you insert the dimension/metric without the ga prefix for example for ga:sessions insert only session.
    You also might need to provide filter operator, for all filter and usage guide look here:
    https://developers.google.com/analytics/devguides/reporting/core/v4/rest/v4/reports/batchGet#Operator
    """
    def __init__(self):
       self.analytics = auth.get_service_analytics()

    @staticmethod
    def __create_date_ranges(start, end, num_periods):
        """
        Create date range list as require in analytics api.
        :param start: days ago for the start of the period(int).
        :param end: days ago for the end of the period(int).
        :param num_periods: num of periods.
        :return: list of dictionary
        """
        # [{'startDate': '30daysAgo', 'endDate': 'today'},
        #  {'startDate': '60daysAgo', 'endDate': '30daysAgo'}],
        date_range_list = []
        delta = start - end
        for period in range(num_periods):
            period_dict = dict()
            period_dict['startDate'] = '{}daysAgo'.format(start)
            period_dict['endDate'] = '{}daysAgo'.format(end)
            date_range_list.append(period_dict)
            start += delta
            end += delta

        return date_range_list

    @staticmethod
    def __add_dimension_filter(request_body, filter_by, filter_operator, filter_expressions):
        """
        Add filter by dimension to the request body.
        :param request_body: request body.
        :param filter_operator:  operator to filter by(string). like "EXACT", "REGEXP", etc..
        :param filter_expressions:  filter expressions(string, format depend on the operator).
        :param filter_expressions:  filter expressions.
        """
        request_body['reportRequests'][0]['dimensionFilterClauses'] = [{
            'filters': [
                {
                    "dimensionName": "ga:{}".format(filter_by),
                    "operator": "{}".format(filter_operator),
                    "expressions": '{}'.format(filter_expressions),
                },
            ],
        }],

    def __metric_by_dimension_response(self, view, dimension, metric, filter_by, filter_operator, filter_expressions,
                                       start, end, num_periods):
        """
        :param view: Analytic's view id.
        :param dimension: dimension to get.
        :param metric:  metric to get.
        :param filter_operator:  operator to filter by(string). like "EXACT", "REGEXP", etc..
        :param filter_expressions:  filter expressions(string, format depend on the operator).
        :param filter_expressions:  filter expressions.
        :param start: first periods start date(int). example 30 = "30daysAgo".
        :param end: first periods end date(int). example 0 = "today".
        :param num_periods: number of periods(max 2) to view data by
        :return: Analytics API response (JSON)
        """
        request_body = {
                'reportRequests': [
                    {
                        'viewId': view,
                        'dateRanges': DataGetter.__create_date_ranges(start, end, num_periods),
                        'metrics': [{'expression': 'ga:{}'.format(metric)}],
                        'dimensions': [{'name': 'ga:{}'.format(dimension)}],
                    }]
            }
        if filter_by != '':
            DataGetter.__add_dimension_filter(request_body, filter_by, filter_operator, filter_expressions)

        return self.analytics.reports().batchGet(
            body=request_body).execute()

    def __metric_response(self, view, metric, filter_by, filter_operator, filter_expressions, start, end, num_periods):
        """
        :param view: Analytic's view id.
        :param metric:  metric to get.
        :param filter_by: filter metric data by dimension.
        :param filter_operator:  operator to filter by(string). like "EXACT", "REGEXP", etc..
        :param filter_expressions:  filter expressions(string, format depend on the operator).
        :param start: first periods start date(int). example 30 = "30daysAgo".
        :param end: first periods end date(int). example 0 = "today".
        :param num_periods: number of periods(max 2) to view data by.
        :return: Analytics API response (JSON).
        """
        request_body = {
                'reportRequests': [
                    {
                        'viewId': view,
                        'dateRanges': DataGetter.__create_date_ranges(start, end, num_periods),
                        'metrics': [{'expression': 'ga:{}'.format(metric)}],
                        'orderBys': [{"fieldName": "ga:{}".format(metric), "sortOrder": "DESCENDING"}],
                    }]
            }
        if filter_by != '':
            DataGetter.__add_dimension_filter(request_body, filter_by, filter_operator, filter_expressions)
        response = self.analytics.reports().batchGet(
            body=request_body).execute()

        return response

    def get_metric_report(self, views, metric, filter_by='', filter_operator='', filter_expressions='', start=30,
                          end=0, num_periods=2):
        """
        Get metric data by view. Allow filtering by dimension.
        :param views: analytic's views id dictionary.
        :param metric:  metric to get form each view.
        :param filter_by: filter metric data by dimension.
        :param filter_operator:  operator to filter by(string). like "EXACT", "REGEXP", etc..
        :param filter_expressions:  filter expressions(string, format depend on the operator).
        :param start: first periods start date(int). example 30 = "30daysAgo".
        :param end: first periods end date(int). example 0 = "today".
        :param num_periods: number of periods(max 2) to view data by
      Return:
            {view: [i'th periods metric data]}
            for example:
            metric = sessions.
            {'Veg.co.il': ['1313', '14872'],
            'all_challenges': ['593100', '9078'],
            'animals-org.il': ['684', '817'],
            'challenge22.co.il': ['419900', '5117'],
            'etgar22.co.il': ['149', '1249']}
        """
        metric_dict = dict()
        for view, view_id in views.items():
            response = self.__metric_response(view_id, metric, filter_by, filter_operator, filter_expressions, start,
                                              end, num_periods)
            data = response.get('reports', [])[0].get('data', {}).get('rows', [])
            metric_dict[view] = [metric['values'][0] for row in data for metric in row['metrics']]
        return metric_dict

    def get_metric_dimension_report(self, view, dimension, metric, filter_by='', filter_operator='',
                                    filter_expressions='', start=30, end=0, num_periods=2):
        """
        Get metric data by dimension. Allow filtering by dimension.
        :param view: Analytic's view id.
        :param dimension: dimension to get.
        :param metric:  metric to get.
        :param filter_by: filter metric data by dimension.
        :param filter_operator:  operator to filter by(string). like "EXACT", "REGEXP", etc..
        :param filter_expressions:  filter expressions(string, format depend on the operator).
        :param start: first periods start date(int). example 30 = "30daysAgo".
        :param end: first periods end date(int). example 0 = "today".
        :param num_periods: number of periods(max 2) to view data by
        Return:
            {Dimension: [i'th periods metric data]}
            for example:
            dimension = eventLabel.
            metric = uniqueEvents.
            filter_by = eventAction.
            filter_operator = EXACT
            filter_expressions = success
            Result:
            'Challenge22 - English': ['410', '404'],
            'Challenge22 - Hebrew Form Plugin': ['245', '4653'],
            'Challenge22 - Hebrew P3': ['480', '41'],
            'Challenge22 - Hebrew VEG': ['1432', '32'],
            'Challenge22 - Hebrew regular': ['513', '7137'],
            'Challenge22 - Spanish': ['35', '44']}
        """

        response = self.__metric_by_dimension_response(view, dimension, metric, filter_by, filter_operator,
                                                       filter_expressions, start, end, num_periods)
        data = response.get('reports', [])[0].get('data', {}).get('rows', [])
        metric_over_dimension = {row['dimensions'][0]: [metric['values'][0] for metric in row['metrics']] for row in data}
        return metric_over_dimension
