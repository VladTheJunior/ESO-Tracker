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
     background-image: url("{path}Visuals/Backgrounds/Paper.png") repeat;
     height: 26px;
     border: 1px solid black;
     font-size: 14px;
}}
 QLabel,QCheckBox{{
     color:#e5e5e5;
}}
 QCheckBox{{
     font: 20px Monotype Corsiva;
}}
 QLabel{{
     font: 24px Monotype Corsiva;
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
 QPushButton#TopRight:hover {{
     border-image: url("{path}Visuals/Buttons/CloseActive.png") no-repeat;
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
     border-image: url("{path}Visuals/TextBlock/TextBlock.png") no-repeat;
     font: 18px formal436 BT;
}}
 QLabel#checkIPDesc {{
     color: lightblue;
     font: bold 18px;
}}
QLabel#InfoCountry {{
     font: 20px;
}}
QLabel#InfoFlag {{
     margin-bottom: 16px;
}}
 QLabel#InfoIP {{
     text-decoration: underline;
     font: bold  18px;
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
 QListWidget::item:selected {{
      background : rgba(255, 255, 255, 0.2);
      border: 0px solid transparent;
      outline: none;
}}
 QListWidget::item:hover {{
      background : rgba(255, 255, 255, 0.1);
      border: 0px solid transparent;
      outline: none;
}}

 QListWidget {{
     background-image: url("{path}Visuals/Backgrounds/Metal.png") repeat;
     border: 1px solid black;
     outline: none;
}}
 QCheckBox::indicator {{
     width: 32px;
     height: 32px;
}}
 QCheckBox::indicator:checked {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox::indicator:unchecked {{
     image: url("{path}Visuals/CheckBox/RoundNormal.png");
}}
 QCheckBox::indicator:checked:hover {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox::indicator:unchecked:hover {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox::indicator:checked:pressed {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox::indicator:unchecked:pressed {{
     image: url("{path}Visuals/CheckBox/RoundActive.png");
}}
 QCheckBox::indicator:checked:disabled {{
     image: url("{path}Visuals/CheckBox/RoundDisabled.png");
}}
 QCheckBox::indicator:unchecked:disabled {{
     image: url("{path}Visuals/CheckBox/RoundDisabled.png");
}}
"""