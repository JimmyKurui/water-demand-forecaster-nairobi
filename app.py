from flask import Flask, request, Response, render_template, jsonify
from markupsafe import escape
from dotenv import load_dotenv
from itertools import chain
from datetime import datetime
from app.constants import zones

load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder='static', static_url_path='/')

# @app.route("/index/")
@app.route("/")
def index():
    from app.services.gis import Map
    map = Map()
    areas = list(chain(*zones.values()))
    return render_template("index.html", title="Home", city="Nairobi", areas=areas, map_gdf=map.nairobi.columns, map_url=map.generate_interactive_map())

@app.route("/predict", methods=["GET", "POST"])
def predict():
    from app.services.ml import MIL
    if request.method == "POST":
        ward = escape(request.form.get("ward"))
        month = request.form.get("month")
        lstm = MIL()
        month = datetime.strptime(month, "%Y-%m")
        prediction, df = lstm.predict(ward, month)
        from app.services.gis import Map
        map = Map()
        map.create_water_choropleth(water_data=df, date=df.tail(1).index[0])
        return jsonify({"value": prediction.tolist()})
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
    app.run(host="0.0.0.0", port=5000, debug=True)
