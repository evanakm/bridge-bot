import os, pathlib
import pytest

os.chdir( pathlib.Path.cwd() / 'bridgebot' / 'test' )

pytest.main()
