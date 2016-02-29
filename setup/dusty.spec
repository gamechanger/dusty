# -*- mode: python -*-

import os

block_cipher = None

a = Analysis(['bin/dusty'],
             pathex=[os.path.abspath('.')],
             binaries=None,
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=['setup/binary-hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

for resource in ['502.js', 'jquery-2.2.1.min.js', 'nginx_502_page.html',
                 'nginx_base_config.txt', 'skeleton.min.css']:
    path = os.path.join('dusty', 'resources', resource)
    a.datas += [(path, path, 'DATA')]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='dusty',
          debug=False,
          strip=False,
          upx=True,
          console=True )
