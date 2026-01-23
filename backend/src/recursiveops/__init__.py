import sys

__all__ = ["__version__"]

__version__ = "0.1.0"

if "pytest" in sys.modules:
    from recursiveops.core import portal_patch

    portal_patch.apply_anyio_portal_patch()
    from recursiveops.core import testclient_patch

    testclient_patch.apply_fastapi_testclient_patch()
