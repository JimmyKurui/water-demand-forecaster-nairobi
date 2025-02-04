from flask import Flask, request, Response, make_response, render_template, abort, send_from_directory, jsonify
from markupsafe import escape
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder="templates", static_folder='static', static_url_path='/')

# @app.route("/index/")
@app.route("/")
def index():
    from app.services.gis import Map
    map = Map()
    return render_template("index.html", title="Home", city="Nairobi", map_gdf=map.nairobi[['subcounty', 'ward']].head(), map_url=map.generate_interactive_map())

@app.route("/predict", methods=["GET", "POST"])
def predict():
    from app.services.ml import MIL
    if request.method == "POST":
        ward = request.form.get("ward")
        month = request.form.get("month")
        volume = request.form.get("volume")
        print(f"You made a POST request \n{ward, month}")
        lstm = MIL()
        prediction = lstm.predict(ward, volume, month)
        return jsonify({"value": prediction})
    elif request.method == "GET":
        return "You made a GET request \n"
    else:
        return "Not a request \n", 200


@app.route("/capitalize/<word>/")
def capitalize(word):
    response = make_response("<h1>{}</h1>".format(escape(word.capitalize())))
    response.status_code = 202
    response.headers["content-type"] = "application/json"
    return response


@app.route("/contribute", methods=['GET', 'POST'])
def contribute():
    if request.method == 'GET':
        return 'Contributor Guide'
    else:
        file = request.files.get('file')
        
        if file.content_type == 'text/plain':
            return file.read().decode()
        else:
            return 'Excel File'

""" 
 -- Sample routes for reuse
 
@app.route("/add/<int:n1>/<int:n2>/")
def add(n1, n2):
    return "<h1>{}</h1>".format(n1 + n2)


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

@app.route("/convert_two", methods=['POST'])
def convert_two():
    file = request.files.get('file')
    df = pd.read_excel(file)
    
    if os.
    return response
@app.route("/download")
def download(): 
    pass
"""
    
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
