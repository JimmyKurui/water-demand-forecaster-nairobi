from flask import Flask, request, Response, render_template, jsonify
from markupsafe import escape
from dotenv import load_dotenv
from itertools import chain
from datetime import datetime
from src.constants import zones

load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder='static', static_url_path='/')

# @app.route("/index/")
@app.route("/")
def index():
    from src.services.gis import Map
    map = Map()
    areas = list(chain(*zones.values()))
    return render_template("index.html", title="Home", city="Nairobi", areas=areas, map_gdf=map.nairobi.columns, map_url=map.generate_interactive_map())

@app.route("/about")
def about():
    return render_template("pages/about.html", title="About")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    from src.services.ml import MIL
    if request.method == "POST":
        ward = escape(request.form.get("ward"))
        month = request.form.get("month")
        lstm = MIL()
        month = datetime.strptime(month, "%Y-%m")
        print('month', month)
        prediction, df = lstm.predict(ward, month)
        from src.services.gis import Map
        map = Map()
        wards_categories = map.create_water_choropleth(water_data=df, date=df.tail(1).index[0])
        return jsonify({
            "value": prediction.tolist(), 
            "year_predictions": df.tail(10).reset_index().to_dict(orient='records'),
            "wards_categories": wards_categories.to_dict(orient='records')
        })
    elif request.method == "GET":
        return "You made a GET request \n"
    else:
        return "Not a valid request \n", 200

@app.route("/contribute", methods=['GET', 'POST'])
def contribute():
    if request.method == 'GET':
        return 'Contributor Guide'
    else:
        file = request.files.get('file')
        
        if file.content_type == 'text/plain':
            return file.read().decode()
        else:
            return 'To be processed'

""" 
 -- Sample routes for reuse
@app.route("/users/<int:user_id>")
def greet_user(user_id):
    if "greeting" in request.args.keys() and "name" in request.args.keys():
        greeting = request.args["greeting"]
        name = request.args["name"]
        return f"{greeting}, {name}"
    else:
        print("Something is smelling")
        users = ["Bob", "Jane"]
        try:
            return "<h2>Hi {}</h2>".format(users[user_id])
        except IndexError:
            abort(404)
            
@app.route("/convert", methods=['POST'])
def convert():
    file = request.files.get('file')
    response = Response(
        pd.read_excel(file),
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=download.csv'
        }
    )
    return response
"""
    
    

if __name__ == "__main__":
    app.run(debug=True)
