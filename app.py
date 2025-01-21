from flask import Flask, render_template, request, jsonify
from database import AirConditionerDB
import pandas as pd

app = Flask(__name__)
db = AirConditionerDB()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/area_search')
def area_search():
    return render_template('area_search.html')

@app.route('/api/search_by_area', methods=['POST'])
def search_by_area():
    area = float(request.form['area'])
    db.connect()
    result = db.find_by_area(area)
    db.close()
    return jsonify(result.to_dict('records'))

@app.route('/price_search')
def price_search():
    return render_template('price_search.html')

@app.route('/api/search_by_price', methods=['POST'])
def search_by_price():
    min_price = int(request.form['min_price'])
    max_price = int(request.form['max_price'])
    db.connect()
    result = db.find_by_price_range(min_price, max_price)
    db.close()
    return jsonify(result.to_dict('records'))

@app.route('/calculation')
def calculation():
    return render_template('calculation.html')

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.form
    db.connect()
    capacity = db.calculate_cooling_capacity(
        float(data['area']),
        float(data.get('height', 2.8)),
        data.get('room_type', '一般'),
        data.get('direction', '一般'),
        data.get('windows', 'false').lower() == 'true'
    )
    result = db.suggest_ac_by_calculation(capacity)
    db.close()
    return jsonify({
        'capacity': capacity,
        'suggestions': result.to_dict('records')
    })

@app.route('/series_info')
def series_info():
    db.connect()
    result = db.get_series_info()
    db.close()
    return render_template('series_info.html', series=result.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True) 