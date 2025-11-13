# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

__version__ = "0.2.0"

from .main import MetaPlugin
from .postprocess import postprocess_site

__all__ = ["MetaPlugin", "postprocess_site", "__version__"]
