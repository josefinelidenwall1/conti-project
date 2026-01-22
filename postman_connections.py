from flask import Flask, request, Response, jsonify
import pmqueries
import json

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

# Route 3: Insert hours
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
    
# Route 4: Create new consultant 
@app.route('/createConsultant', methods=['POST'])
def add_consultant():
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)