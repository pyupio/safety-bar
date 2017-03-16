# -*- mode: python -*-

block_cipher = None


a = Analysis(['app.py'],
             pathex=['/Users/j/dev/pyup-menubar'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [
            (
                'icons/gray.png',
                'icons/gray.png',
                'icons'
            ),
            (
                'icons/red.png',
                'icons/red.png',
                'icons'
            ),
            (
                'icons/green.png',
                'icons/green.png',
                'icons'
            ),
          ],
          name='app',
          debug=False,
          strip=False,
          upx=True,
          console=True )
