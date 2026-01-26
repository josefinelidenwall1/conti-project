#manual trigger
import os
from report_queries import run_report
from sdkfunctions import sdk_config, upload_file2


def get_report():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"DEBUGG: workign directory set to: {script_dir}")
    run_report()
    
    sdk_config()
    upload_file2('consultant_report.txt')

if __name__ == "__main__":
    get_report()