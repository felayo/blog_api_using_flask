from flask import Flask
import os
from dotenv import load_dotenv, find_dotenv

from .models import setup_db
from .shared import mail

from .views.UserView import user_api as user_blueprint
from .views.BlogpostView import blogpost_api as blogpost_blueprint

load_dotenv(find_dotenv())

def create_app():
  app = Flask(__name__)
  setup_db(app)
  mail.init_app(app)
  
  app.register_blueprint(user_blueprint, url_prefix='/api/v1/users')
  app.register_blueprint(blogpost_blueprint, url_prefix='/api/v1/blogposts')
  

  @app.route('/', methods=['GET'])
  def index():
    """
    example endpoint
    """
    return 'Congratulations! Your first endpoint is working'

  return app


if __name__ == '__main__':
  env_name = os.getenv('FLASK_ENV')
  app = create_app(env_name)
  # run app
  app.run()
