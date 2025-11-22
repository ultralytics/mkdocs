# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

__version__ = "0.2.2"

from .main import MetaPlugin
from .postprocess import postprocess_site

__all__ = ["MetaPlugin", "__version__", "postprocess_site"]
