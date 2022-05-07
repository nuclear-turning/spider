import sys

from PyQt5.QtWidgets import QApplication

from KSVS_Moudle.utils.DataGrid import DataGrid

app = QApplication(sys.argv)
window = DataGrid("","KSUserData")
window.show()
sys.exit(app.exec_())