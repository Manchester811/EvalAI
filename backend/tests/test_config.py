import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings

def test_config_loads():
    assert hasattr(settings, 'SECRET_KEY')
    assert settings.APP_ENV == 'development'

def test_db_connects():
    from sqlalchemy import create_engine
    try:
        connect_args = {'check_same_thread': False} if settings.DATABASE_URL.startswith('sqlite') else {'connect_timeout': 2}
        engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
        conn = engine.connect()
        conn.close()
    except Exception as e:
        assert False, f'DB connect failed: {e}'
