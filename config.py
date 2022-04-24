
from dynaconf import Dynaconf
from src.scheduling.models import GlobalState

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
)

state = GlobalState()
ALPHA = 0.05

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'console': {
            'format': ('[%(asctime)s][%(levelname)s] %(name)s '
                       '%(filename)s:%(funcName)s:%(lineno)d | %(message)s'),
            'datefmt': '%H:%M:%S',
        }
    },
    'handlers': {
        'simple': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['simple', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}
# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
