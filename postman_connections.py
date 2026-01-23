from flask import Flask, request, Response, jsonify
import pmqueries
import json
from manualtrigger import get_report
from report_queries import run_report
from sdkfunctions import sdk_config, upload_file2

app = Flask(__name__)

"""
example JSON:

POST /hours on excisting person

{
    "consultant_id": 18,
    "starttime": "2025-12-22 06:30:00",
    "endtime": "2025-12-22 21:00:00",
    "lunchbreak": true,
    "customername": "Edwards, Pope and Bishop"
}

POST /consultant (creates a new consultant)

{
    "consultant_name": "Jonathan Doebolomew"
}

"""

# Route 1: Get all consultants
@app.route('/consultants', methods=['GET'])
def consultants():
    # Call db_get_consultant function
    json_response = pmqueries.db_get_consultants()
    
    # Check if data was returned successfully
    if json_response:
        return Response(json_response, mimetype='application/json', status=200)
    else:
        return jsonify({"error": "Failed to fetch consultants"}), 500

# Route 2: Get all hours
@app.route('/hours', methods=['GET'])
def hours():
    json_response = pmqueries.get_hours()
    
    if json_response:
        return Response(json_response, mimetype='application/json', status=200)
    else:
        return jsonify({"error": "Failed to fetch hours"}), 500
    
# Route 3: POST manual trigger 

@app.route('/trigger-report', methods=['POST'])
def trigger_report_generation():
    try:
        # This replaces your manual "get_report()" call
        get_report()
        
        return jsonify({"status": "success", "message": "Report generated and uploaded."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route 4: Insert hours
@app.route('/hours', methods=['POST'])
def add_hours():
    try:
        # Get data from Postman JSON body
        data = request.get_json()
        
        # Check if we have the required fields
        required_fields = ['consultant_id', 'starttime', 'endtime', 'lunchbreak', 'customername']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        #pass raw string informaton calls excisting function
        result = pmqueries.insert_hours(
            consultant_id=data['consultant_id'],
            starttime=data['starttime'],
            endtime=data['endtime'],
            lunchbreak=data['lunchbreak'],
            customername=data['customername']
        )

        if result:
            return Response(result, mimetype='application/json', status=201)
        else:
            return jsonify({"error": "Database insert failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Route 5: Insert consultants
@app.route('/consultants', methods=['POST'])
def add_consultants():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid or missing JSON"}), 400

        if 'consultant_name' not in data:
            return jsonify({"error": "Missing required fields"}), 400

        result = pmqueries.insert_consultants(
            consultant_name=data['consultant_name']
        )

        if result:
            return jsonify(result), 201
        else:
            return jsonify({"error": "Database insert failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Route 7: Update existing hours
@app.route('/hours/<int:id>', methods=['PUT'])
def modify_hours(id):
    try:
        data = request.get_json()    
        # Check required fields (same as POST)
        required_fields = ['starttime', 'endtime', 'lunchbreak', 'customername']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        # Call the UPDATE function
        result = pmqueries.update_hours(
            workday_id=id,
            starttime=data['starttime'],
            endtime=data['endtime'],
            lunchbreak=data['lunchbreak'],
            customername=data['customername']
        )
        if result:
            return Response(result, mimetype='application/json', status=200)
        else:
            return jsonify({"error": "Workday ID not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Route 8 mtrigger for manual report? 

#@app.route('/get-report', methods=['GET'])
#def get_report_api():
#    try:
#        json_response = run_report()
#
#        if json_response:
#            sdk_config()
#            upload_file2('consultant_report.txt')
#            return Response(json_response, mimetype='application/json', status=200)
#        else:
#            return jsonify({"error": "Report generation returned no data"}), 500

#    except Exception as e:
#        return jsonify({
#            "error": "Failed to generate report",
#            "details": str(e)
#        }), 500


# Route 9: Get hours for a specific consultant
@app.route('/consultant/<int:id>/hours', methods=['GET'])
def consultant_hours(id):
    try:
        # Call the new function
        result = pmqueries.get_hours_by_consultant(id)
        
        if result:
            return Response(result, mimetype='application/json', status=200)
        else:
            return jsonify({"error": "Could not fetch hours"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)