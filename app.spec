block_cipher = None


a = Analysis(['gui.py'],
             binaries=[],
             datas=[('message.mp3', 'sound'), ('connect.mp3','sound'), ('icon.ico','.'), 
("Visuals/Backgrounds/Metal.png", "Visuals/Backgrounds"),
("Visuals/Backgrounds/Paper.png", "Visuals/Backgrounds"),
("Visuals/Backgrounds/Wood.png", "Visuals/Backgrounds"),
("Visuals/Backgrounds/Fabric.jpg", "Visuals/Backgrounds"),
("Visuals/Borders/Bottom.png", "Visuals/Borders"),
("Visuals/Borders/BottomLeft.png", "Visuals/Borders"),
("Visuals/Borders/BottomLeftRight.png", "Visuals/Borders"),
("Visuals/Borders/BottomLeftTop.png", "Visuals/Borders"),
("Visuals/Borders/BottomRight.png", "Visuals/Borders"),
("Visuals/Borders/BottomRightLeft.png", "Visuals/Borders"),
("Visuals/Borders/BottomRightTop.png", "Visuals/Borders"),
("Visuals/Borders/Left.png", "Visuals/Borders"),
("Visuals/Borders/Right.png", "Visuals/Borders"),
("Visuals/Borders/Top.png", "Visuals/Borders"),
("Visuals/Borders/TopLeft.png", "Visuals/Borders"),
("Visuals/Borders/TopLeftBottom.png", "Visuals/Borders"),
("Visuals/Borders/TopLeftRight.png", "Visuals/Borders"),
("Visuals/Borders/TopRight.png", "Visuals/Borders"),
("Visuals/Borders/TopRightBottom.png", "Visuals/Borders"),
("Visuals/Borders/TopRightLeft.png", "Visuals/Borders"),
("Visuals/Borders/BBottom.png", "Visuals/Borders"),
("Visuals/Borders/BLeft.png", "Visuals/Borders"),
("Visuals/Borders/BLeftBottom.png", "Visuals/Borders"),
("Visuals/Borders/BLeftTop.png", "Visuals/Borders"),
("Visuals/Borders/BRight.png", "Visuals/Borders"),
("Visuals/Borders/BRightBottom.png", "Visuals/Borders"),
("Visuals/Borders/BRightTop.png", "Visuals/Borders"),
("Visuals/Borders/BTop.png", "Visuals/Borders"),
("Visuals/Buttons/CloseActive.png", "Visuals/Buttons"),
("Visuals/Buttons/CloseClicked.png", "Visuals/Buttons"),
("Visuals/Buttons/CloseNormal.png", "Visuals/Buttons"),
("Visuals/Buttons/ButtonActive.png", "Visuals/Buttons"),
("Visuals/Buttons/ButtonClicked.png", "Visuals/Buttons"),
("Visuals/Buttons/ButtonDisable.png", "Visuals/Buttons"),
("Visuals/Buttons/ButtonNormal.png", "Visuals/Buttons"),
("Visuals/Buttons/AddActive.png", "Visuals/Buttons"),
("Visuals/Buttons/AddClicked.png", "Visuals/Buttons"),
("Visuals/Buttons/AddDisabled.png", "Visuals/Buttons"),
("Visuals/Buttons/addNormal.png", "Visuals/Buttons"),
("Visuals/Buttons/MenuActive.png", "Visuals/Buttons"),
("Visuals/Buttons/MenuNormal.png", "Visuals/Buttons"),
("Visuals/CheckBox/RoundActive.png", "Visuals/CheckBox"),
("Visuals/CheckBox/RoundDisabled.png", "Visuals/CheckBox"),
("Visuals/CheckBox/RoundNormal.png", "Visuals/CheckBox"),
("Visuals/Cursor/AoE.png", "Visuals/Cursor"),
("Visuals/Fonts/MTCORSVA.TTF", "Visuals/Fonts"),
("Visuals/Fonts/formal-436-bt-5947cc2c8b950.ttf", "Visuals/Fonts"),
("Visuals/Fonts/DroidSans.ttf", "Visuals/Fonts"),
("Visuals/TextBlock/TextBlock.png", "Visuals/TextBlock"),
("Visuals/TextBlock/TextEdit.png", "Visuals/TextBlock"),
("Visuals/Tabs/Active.png", "Visuals/Tabs"),
("Visuals/Tabs/Normal.png", "Visuals/Tabs"),
("Visuals/Civs/British.png", "Visuals/Civs"),
("Visuals/Civs/Chinese.png", "Visuals/Civs"),
("Visuals/Civs/Dutch.png", "Visuals/Civs"),
("Visuals/Civs/French.png", "Visuals/Civs"),
("Visuals/Civs/Germans.png", "Visuals/Civs"),
("Visuals/Civs/Indians.png", "Visuals/Civs"),
("Visuals/Civs/Japanese.png", "Visuals/Civs"),
("Visuals/Civs/Ottomans.png", "Visuals/Civs"),
("Visuals/Civs/Portuguese.png", "Visuals/Civs"),
("Visuals/Civs/Russians.png", "Visuals/Civs"),
("Visuals/Civs/Spanish.png", "Visuals/Civs"),
("Visuals/Civs/XPAztec.png", "Visuals/Civs"),
("Visuals/Civs/XPIroquois.png", "Visuals/Civs"),
("Visuals/Civs/XPSioux.png", "Visuals/Civs"),

],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['FixTk', 'tcl', 'tk', '_tkinter', 'tkinter', 'Tkinter','matplotlib'],
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
          name='ESO Tracker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=False,
icon='icon.ico',
version='file_version_info.txt' )