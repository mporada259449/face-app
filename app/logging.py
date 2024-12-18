from .models import LoggingEvent
from . import db
import datetime

def log_event(msg, msg_type='app'):
    timestamp=datetime.datetime.now()
    new_log = LoggingEvent(timestamp=timestamp, msg_type=msg_type, message=msg)
    db.session.add(new_log)
    db.session.commit()

def get_event(msg_type='all'):
    if msg_type == 'all':
        events = LoggingEvent.query.all()
    else:
        events = LoggingEvent.query.filter_by(msg_type=msg_type).all()
    
    return [(e.timestamp, e.msg_type, e.message) for e in events]
    
