
from dynaconf import Dynaconf
from scheduling.models import GlobalState

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
)

state = GlobalState()
ALPHA = 0.05
# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
