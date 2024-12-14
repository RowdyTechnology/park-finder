from .parks import parks_bp
from .feature_requests import feature_requests_bp
from .utility_pages import utility_pages_bp
from .user_stats import user_stats_bp

def init_app(app):
    app.register_blueprint(parks_bp, url_prefix="/parks")
    app.register_blueprint(feature_requests_bp, url_prefix="/feature_requests")
    app.register_blueprint(utility_pages_bp)
    app.register_blueprint(user_stats_bp, url_prefix="/user_stats")