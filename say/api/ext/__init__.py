from flasgger import Swagger
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail


limiter = Limiter(key_func=get_remote_address)
jwt = JWTManager()
mail = Mail()
swagger = Swagger()
cache = Cache()
cors = CORS(resources={r"/api/*": {"origins": "*"}})