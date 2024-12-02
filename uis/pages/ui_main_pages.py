
# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from import_core import *


class Ui_MainPages(object):
    def setupUi(self, MainPages):
        if not MainPages.objectName():
            MainPages.setObjectName(u"MainPages")
        MainPages.resize(860, 600)
        self.main_pages_layout = QVBoxLayout(MainPages)
        self.main_pages_layout.setSpacing(0)
        self.main_pages_layout.setObjectName(u"main_pages_layout")
        self.main_pages_layout.setContentsMargins(0, 0, 0, 0)
        self.pages = QStackedWidget(MainPages)
        self.pages.setObjectName(u"pages")

        #PAGE 0
        self.page_0 = QWidget()
        self.page_0.setObjectName(u"page_0")
        self.page_0.setStyleSheet(u"font-size: 14pt")
        self.page_0_layout = QVBoxLayout(self.page_0)
        self.page_0_layout.setSpacing(5)
        self.page_0_layout.setObjectName(u"page_0_layout")
        self.page_0_layout.setContentsMargins(5, 5, 5, 5)
        self.welcome_base = QFrame(self.page_0)
        self.welcome_base.setObjectName(u"welcome_base")
        self.welcome_base.setMinimumSize(QSize(300, 150))
        self.welcome_base.setMaximumSize(QSize(300, 150))
        self.welcome_base.setFrameShape(QFrame.NoFrame)
        self.welcome_base.setFrameShadow(QFrame.Raised)
        self.center_page_layout = QVBoxLayout(self.welcome_base)
        self.center_page_layout.setSpacing(10)
        self.center_page_layout.setObjectName(u"center_page_layout")
        self.center_page_layout.setContentsMargins(0, 0, 0, 0)
        self.logo = QFrame(self.welcome_base)
        self.logo.setObjectName(u"logo")
        self.logo.setMinimumSize(QSize(300, 120))
        self.logo.setMaximumSize(QSize(300, 120))
        self.logo.setFrameShape(QFrame.NoFrame)
        self.logo.setFrameShadow(QFrame.Raised)
        self.logo_layout = QVBoxLayout(self.logo)
        self.logo_layout.setSpacing(0)
        self.logo_layout.setObjectName(u"logo_layout")
        self.logo_layout.setContentsMargins(0, 0, 0, 0)
        self.center_page_layout.addWidget(self.logo)
        self.page_0_layout.addWidget(self.welcome_base, 0, Qt.AlignHCenter)
        self.pages.addWidget(self.page_0)

        #PAGE 1
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.page_1.setStyleSheet(u"QFrame {\n"
"	font-size: 16pt;\n"
"}")
        self.page_1_layout = QHBoxLayout(self.page_1)
        self.page_1_layout.setObjectName(u"page_1_layout")
        self.page_1_layout.setSpacing(5)
        self.page_1_layout.setObjectName(u"page_1_layout")
        self.page_1_layout.setContentsMargins(0, 0, 0, 0)
        self.contents_page_1 = QFrame(self.page_1)
        self.contents_page_1.setObjectName(u"contents_page_1")
        self.contents_page_1.setStyleSheet(u"background: transparent;")
        self.contents_page_1.setFrameShape(QFrame.NoFrame)
        self.contents_page_1.setFrameShadow(QFrame.Raised)
        self.page_1_layout.addWidget(self.contents_page_1)
        self.pages.addWidget(self.page_1)

        #PAGE 2
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.page_2_layout = QVBoxLayout(self.page_2)
        self.page_2_layout.setSpacing(5)
        self.page_2_layout.setObjectName(u"page_2_layout")
        self.page_2_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_area = QScrollArea(self.page_2)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setStyleSheet(u"background: transparent;")
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)


        self.horizontallLayout = QHBoxLayout(self.contents_page_1)
        #self.horizontallLayout.setSpacing(15)
        self.horizontallLayout.setObjectName(u"horizontallLayout")
        self.horizontallLayout.setContentsMargins(0, 0, 0, 0)
        font = QFont()
        font.setPointSize(16)


        self.column_1_layout = QVBoxLayout()
        self.column_1_layout.setObjectName(u"column_1_layout")

        self.horizontallLayout.addLayout(self.column_1_layout)

        self.column_2_layout = QVBoxLayout()
        self.column_2_layout.setObjectName(u"column_2_layout")

        self.horizontallLayout.addLayout(self.column_2_layout)

        self.column_3_layout = QVBoxLayout()
        self.column_3_layout.setObjectName(u"column_3_layout")

        self.horizontallLayout.addLayout(self.column_3_layout)

        self.scroll_area.setWidget(self.contents_page_1)

        self.page_1_layout.addWidget(self.scroll_area)

        self.pages.addWidget(self.page_2)

        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.page_3.setStyleSheet(u"QFrame {\n"
"	font-size: 16pt;\n"
"}")
        self.page_3_layout = QVBoxLayout(self.page_3)
        self.page_3_layout.setObjectName(u"page_3_layout")
        self.empty_page_label = QLabel(self.page_3)
        self.empty_page_label.setObjectName(u"empty_page_label")
        self.empty_page_label.setFont(font)
        self.empty_page_label.setAlignment(Qt.AlignCenter)
        self.page_3_layout.addWidget(self.empty_page_label)
        self.pages.addWidget(self.page_3)

        self.main_pages_layout.addWidget(self.pages)
        self.retranslateUi(MainPages)
        self.pages.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainPages)
    # setupUi

    def retranslateUi(self, MainPages):
        MainPages.setWindowTitle(QCoreApplication.translate("MainPages", u"Form", None))
        #self.label.setText(QCoreApplication.translate("MainPages", u"Добро пожаловать", None))
        self.empty_page_label.setText(QCoreApplication.translate("MainPages", u"Empty Page", None))
    # retranslateUi

