from flask import Flask
app = Flask(__name__, static_url_path='/static')
from views import index_bp,employee
from utils import config





app.secret_key = config.SECRET_KEY



app.register_blueprint(index_bp.index_bp)
app.register_blueprint(employee.employee)

