#manual trigger
from report_queries import run_report
from sdkfunctions import sdk_config, upload_file


def get_report():
    run_report()
    sdk_config()
    upload_file('consultant_report.txt')


get_report()