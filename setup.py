import os
from typing import List, Tuple
from cx_Freeze import setup, Executable
from curl_cffi import __file__ as curl_cffi_file

# https://github.com/marcelotduarte/cx_Freeze/issues/1288
base = None

proj_root = os.path.abspath(os.path.dirname(__file__))


include_files: List[Tuple[str, str]] = [
    (f'{proj_root}/config.yml', 'config.yml'),
    (f'{proj_root}/data', 'data'),
    (f'{proj_root}/image', 'image')
]

# curl_cffi's native libcurl DLL is installed alongside its package rather than
# inside it, so cx_Freeze does not discover it from the Python imports alone.
curl_cffi_libs = os.path.join(
    os.path.dirname(os.path.dirname(curl_cffi_file)), 'curl_cffi.libs'
)
if os.path.isdir(curl_cffi_libs):
    include_files.append((curl_cffi_libs, 'lib/curl_cffi.libs'))

includes = []

for file in os.listdir('javsp/web'):
    name, ext = os.path.splitext(file)
    if ext == '.py':
        includes.append('javsp.web.' + name)

packages = [ 
    'pendulum' # pydantic_extra_types depends on pendulum
]

build_exe = {
    'include_files': include_files,
    'includes': includes,
    'excludes': ['unittest'],
    'packages': packages,
}

javsp = Executable(
    './javsp/__main__.py', 
    target_name='JavSP', 
    base=base,
    icon='./image/JavSP.ico',
)

setup(
    name='JavSP',
    options = {'build_exe': build_exe}, 
    executables=[javsp]
)
