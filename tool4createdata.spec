# -*- mode: python -*-

block_cipher = None


a = Analysis(['tool4createdata.py'],
             pathex=['D:\\5.Workspace\\Python\\V-Medsub-py'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['D:\\5.Workspace\\Python\\V-Medsub-py\\hook'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='tool4createdata',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
