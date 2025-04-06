from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.community_owner import CommunityOwner
from models.subscriber import Subscriber
from models.alert_log import AlertLog
