#manual trigger
from report_queries import run_report
from sdkfunctions import sdk_config, upload_file2


def get_report():
    run_report()
    sdk_config()
    upload_file2('consultant_report.txt')

if __name__ == "__main__":
    get_report()