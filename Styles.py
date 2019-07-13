stylesheet = """
QScrollBar:horizontal {{
     height: 12px;
     margin: 2px;
     border: 1px transparent #2A2929;
     border-radius: 4px;
     background-color: transparent;
}}
 QScrollBar::handle:horizontal {{
     background-color: #4c4c4c;
     min-width: 5px;
     border-radius: 4px;
}}
 QScrollBar::add-line:horizontal {{
     width: 0px;
     height: 0px;
}}
 QScrollBar::sub-line:horizontal {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::add-line:horizontal:hover,QScrollBar::add-line:horizontal:on {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::sub-line:horizontal:hover, QScrollBar::sub-line:horizontal:on {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {{
     background: none;
}}
 QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
     background: none;
}}
 QScrollBar:vertical {{
     background-color: transparent;
     width: 12px;
     margin: 2px;
     border: 1px transparent #2A2929;
     border-radius: 4px;
}}
 QScrollBar::handle:vertical {{
     background-color: #4c4c4c;
     min-height: 5px;
     border-radius: 4px;
}}
 QScrollBar::sub-line:vertical {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::add-line:vertical {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::sub-line:vertical:hover,QScrollBar::sub-line:vertical:on {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::add-line:vertical:hover, QScrollBar::add-line:vertical:on {{
     height: 0px;
     width: 0px;
}}
 QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
     background: none;
}}
 QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
     background: none;
}}
 QAbstractScrollArea {{
     background-color:transparent;
}}
 QLineEdit{{
     background-image: url("{path}Visuals/Backgrounds/Fabric.jpg") repeat;
     height: 26px;
     border: 1px solid black;
     font-size: 14px;
}}
 QLabel{{
     font: 24px Monotype Corsiva;
}}
 QWidget#TeamWon{{
     border: 1px solid rgba(229,229,229,0.25);
     background-color: rgba(0, 255, 0, 0.2);
     border-radius: 5px;
     padding: 5px;

 }}

  QWidget#TeamNone{{
     border: 1px solid rgba(229,229,229,0.25);
     background-color: rgba(255, 255, 0, 0.2);
     border-radius: 5px;
     padding: 5px;

 }}

 QWidget#TeamLost{{
     border: 1px solid rgba(229,229,229,0.25);
     background-color: rgba(255, 0, 0, 0.2);
     border-radius: 5px;
     padding: 5px;

 }}

 QLabel#TextBlock{{
     border-image: url("{path}Visuals/TextBlock/TextBlock.png") no-repeat;
     font: 500 22px Monotype Corsiva;
     color: #e5e5e5;
}}

 QLabel#GameInfo{{
     color: #e5e5e5;
     font: 700 13px Verdana;
     padding-right:5px;
 }}

  QLabel#GameName{{
     color: #e5e5e5;
     font: 36px Monotype Corsiva;

 }}

   QLabel#MapName{{
     color: #e5e5e5;
     font: 24px Monotype Corsiva;
 }}

 QLabel,QCheckBox{{
     color:black;
}}
 QCheckBox{{
     font: 24px Monotype Corsiva;
}}
 QWidget#RecordedGames {{
     color: white;
}}

 QWidget#MainWindow {{
     border-image: url("{path}Visuals/Backgrounds/Wood.png") repeat;
}}
 QWidget#TopLeft {{
     border-image: url("{path}Visuals/Borders/TopLeft.png") no-repeat;
}}
 QPushButton#TopRight {{
     border-image: url("{path}Visuals/Buttons/CloseNormal.png") no-repeat;
}}

 QPushButton#MenuItem {{
     font: 500 22px Monotype Corsiva;
     color:#e5e5e5;
     
     text-align:right;
     padding-right:6px;
     border-image: url("{path}Visuals/Buttons/MenuNormal.png") no-repeat;
}}

 QPushButton#MenuItem:checked {{
     border-image: url("{path}Visuals/Buttons/MenuActive.png") no-repeat;
     padding-right:9px;
}}

 QPushButton#TopRight:hover {{
     border-image: url("{path}Visuals/Buttons/CloseActive.png") no-repeat;
}}
 QPushButton#TopRight:pressed {{
     border-image: url("{path}Visuals/Buttons/CloseClicked.png") no-repeat;
}}
 QWidget#BottomLeft {{
     border-image: url("{path}Visuals/Borders/BottomLeft.png") no-repeat;
}}
 QWidget#BottomRight {{
     border-image: url("{path}Visuals/Borders/BottomRight.png") no-repeat;
}}
 QWidget#Right {{
     border-image: url("{path}Visuals/Borders/Right.png") repeat-y;
}}
 QWidget#Left {{
     border-image: url("{path}Visuals/Borders/Left.png") repeat-x;
}}
 QWidget#Top {{
     border-image: url("{path}Visuals/Borders/Top.png") repeat-x;
}}
 QLabel#Title {{
     
     font: 18px formal436 BT;
     color: #e5e5e5;
}}

QWidget#TitleBkg{{
    border-image: url("{path}Visuals/TextBlock/TextBlock.png") no-repeat;
}}

 QWidget#BBottom {{
     border-image: url("{path}Visuals/Borders/BBottom.png") repeat-x;
}}
 QWidget#BTop {{
     border-image: url("{path}Visuals/Borders/BTop.png") repeat-x;
}}
 QWidget#BRight {{
     border-image: url("{path}Visuals/Borders/BRight.png") repeat-x;
}}
 QWidget#BLeft {{
     border-image: url("{path}Visuals/Borders/BLeft.png") repeat-x;
}}

 QWidget#BTopLeft {{
     border-image: url("{path}Visuals/Borders/BLeftTop.png") repeat-x;
}}
 QWidget#BTopRight {{
     border-image: url("{path}Visuals/Borders/BRightTop.png") repeat-x;
}}

 QWidget#BBottomLeft {{
     border-image: url("{path}Visuals/Borders/BLeftBottom.png") repeat-x;
}}

 QWidget#BBottomRight {{
     border-image: url("{path}Visuals/Borders/BRightBottom.png") repeat-x;
}}

 QWidget#Bottom {{
     border-image: url("{path}Visuals/Borders/Bottom.png") repeat-x;
}}
 QWidget#TopLeftBottom {{
     border-image: url("{path}Visuals/Borders/TopLeftBottom.png") no-repeat;
}}
 QWidget#TopLeftRight {{
     border-image: url("{path}Visuals/Borders/TopLeftRight.png") no-repeat;
}}
 QWidget#BottomLeftTop {{
     border-image: url("{path}Visuals/Borders/BottomLeftTop.png") no-repeat;
}}
 QWidget#BottomLeftRight {{
     border-image: url("{path}Visuals/Borders/BottomLeftRight.png") no-repeat;
}}
 QWidget#TopRightBottom {{
     border-image: url("{path}Visuals/Borders/Right.png") no-repeat;
}}
 QWidget#TopRightLeft {{
     border-image: url("{path}Visuals/Borders/Top.png") no-repeat;
}}
 QWidget#BottomRightTop {{
     border-image: url("{path}Visuals/Borders/BottomRightTop.png") no-repeat;
}}
 QWidget#BottomRightLeft {{
     border-image: url("{path}Visuals/Borders/BottomRightLeft.png") no-repeat;
}}
 QListView::item:selected {{
      background : rgba(255, 255, 255, 0.4);
      color: black;
      border-top: 1px solid #A0000000;
      border-bottom: 1px solid #A0000000;
      outline: none;
}}
 QListView::item:hover {{
      background : rgba(255, 255, 255, 0.3);
      color: black;
      border-top: 1px solid #A0000000;
      border-bottom: 1px solid #A0000000;
      outline: none;
}}

 QListView {{
     background-image: url("{path}Visuals/Backgrounds/Fabric.jpg") repeat;
     border: 1px solid black;
     outline: none;
}}

 QWidget#MenuContent {{
     background-image: url("{path}Visuals/Backgrounds/Paper.png") repeat;

}}

QCheckBox#standardCheckBoxW{{
    color: #e5e5e5;
}}

 QCheckBox#standardCheckBoxW::indicator {{
     width: 32px;
     height: 32px;
}}
 QCheckBox#standardCheckBoxW::indicator:checked {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBoxW::indicator:unchecked {{
     image: url("{path}Visuals/CheckBox/RoundNormal.png");
}}
 QCheckBox#standardCheckBoxW::indicator:checked:hover {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBoxW::indicator:unchecked:hover {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBoxW::indicator:checked:pressed {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBoxW::indicator:unchecked:pressed {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBoxW::indicator:checked:disabled {{
     image: url("{path}Visuals/CheckBox/RoundDisabled.png");
}}
 QCheckBox#standardCheckBoxW::indicator:unchecked:disabled {{
     image: url("{path}Visuals/CheckBox/RoundDisabled.png");
}}

 QCheckBox#standardCheckBox::indicator {{
     width: 32px;
     height: 32px;
}}
 QCheckBox#standardCheckBox::indicator:checked {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBox::indicator:unchecked {{
     image: url("{path}Visuals/CheckBox/RoundNormal.png");
}}
 QCheckBox#standardCheckBox::indicator:checked:hover {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBox::indicator:unchecked:hover {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBox::indicator:checked:pressed {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBox::indicator:unchecked:pressed {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox#standardCheckBox::indicator:checked:disabled {{
     image: url("{path}Visuals/CheckBox/RoundDisabled.png");
}}
 QCheckBox#standardCheckBox::indicator:unchecked:disabled {{
     image: url("{path}Visuals/CheckBox/RoundDisabled.png");
}}

 QCheckBox#Player1Color::indicator,QCheckBox#Player2Color::indicator,QCheckBox#Player3Color::indicator,QCheckBox#Player4Color::indicator,QCheckBox#Player5Color::indicator,QCheckBox#Player6Color::indicator,QCheckBox#Player7Color::indicator,QCheckBox#Player8Color::indicator {{
     width: 36px;
     height: 24px;
     padding:2px;
     border: 1px solid black;
}}
 QCheckBox#Player1Color::indicator:checked {{
     background-color: rgb(45, 45, 245);
}}
 QCheckBox#Player2Color::indicator:checked {{
     background-color: rgb(210, 40, 40);
}}
 QCheckBox#Player3Color::indicator:checked {{
     background-color: rgb(215, 215, 30);
}}
 QCheckBox#Player4Color::indicator:checked {{
     background-color: rgb(150, 15, 250);
}}
 QCheckBox#Player5Color::indicator:checked {{
     background-color: rgb(15, 210, 80);
}}
 QCheckBox#Player6Color::indicator:checked {{
     background-color: rgb(255, 150, 5);
}}
 QCheckBox#Player7Color::indicator:checked {{
     background-color: rgb(150, 255, 240);
}}
 QCheckBox#Player8Color::indicator:checked {{
     background-color: rgb(255, 190, 255);
}}


 QCheckBox#Player1Color::indicator:hover {{
     background-color: rgb(70, 70, 255);
}}
 QCheckBox#Player2Color::indicator:hover {{
     background-color: rgb(230, 60, 60);
}}
 QCheckBox#Player3Color::indicator:hover {{
     background-color: rgb(235, 235, 50);
}}
 QCheckBox#Player4Color::indicator:hover {{
     background-color: rgb(170, 35, 255);
}}
 QCheckBox#Player5Color::indicator:hover {{
     background-color: rgb(35, 230, 100);
}}
 QCheckBox#Player6Color::indicator:hover {{
     background-color: rgb(255, 170, 25);
}}
 QCheckBox#Player7Color::indicator:hover {{
     background-color: rgb(170, 255, 255);
}}
 QCheckBox#Player8Color::indicator:hover {{
     background-color: rgb(255, 210, 255);
}}

 QCheckBox#Player1Color::indicator:unchecked,QCheckBox#Player2Color::indicator:unchecked,QCheckBox#Player3Color::indicator:unchecked,QCheckBox#Player4Color::indicator:unchecked,QCheckBox#Player5Color::indicator:unchecked,QCheckBox#Player6Color::indicator:unchecked,QCheckBox#Player7Color::indicator:unchecked,QCheckBox#Player8Color::indicator:unchecked {{
     background-color: rgb(127, 127, 127);
}}


 QTabBar::tab {{
      font: 500 20px Monotype Corsiva;
      color: #e5e5e5;
      width:256px;
      height:32px;
      border-image: url("{path}Visuals/Tabs/Normal.png") no-repeat;
}}     

 QTabBar::tab:selected {{
      border-image: url("{path}Visuals/Tabs/Active.png") no-repeat;
}}     


 QTabWidget::pane{{
     border: 1px solid black;
     background-image: url("{path}Visuals/Backgrounds/Metal.png") repeat;
   
 }}


 QPushButton#Button{{
     font: 500 20px Monotype Corsiva;
     border-image: url("{path}Visuals/Buttons/ButtonNormal.png") no-repeat;
     color: #e5e5e5;
   
 }}

 QPushButton#Button:hover{{
     border-image: url("{path}Visuals/Buttons/ButtonActive.png") no-repeat;  
 }}

 QPushButton#Button:pressed{{
     border-image: url("{path}Visuals/Buttons/ButtonClicked.png") no-repeat;  
 }}

 QPushButton#Button:disabled{{
     border-image: url("{path}Visuals/Buttons/ButtonDisable.png") no-repeat;  
 }}
"""