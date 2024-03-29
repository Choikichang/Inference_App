import sys
import paramiko
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QLineEdit, QFileDialog, QTextEdit, QMenuBar
from PyQt5.QtGui import QPixmap  # Import QPixmap to display the logo
from PyQt5.QtCore import Qt

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Docker Control GUI'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        layout = QVBoxLayout()

        # Create a QLabel to display the logo image with a fixed size
        logo_label = QLabel(self)
        logo_label.setFixedSize(600, 100)  # Set the desired size (600x300)

#########################  Logo path ###############################

        pixmap = QPixmap('/home/choi/Git/Inference_App/LOGO/Seoseoul_slump_time_table.jpg')  # Provide the path to your logo image

########################################################

        pixmap = pixmap.scaled(600, 100, Qt.KeepAspectRatio)  # Scale the pixmap to fit the label
        logo_label.setPixmap(pixmap)
        layout.addWidget(logo_label)

        self.menu_bar = QMenuBar(self)
        file_menu = self.menu_bar.addMenu('File')
        edit_menu = self.menu_bar.addMenu('Edit')
        help_menu = self.menu_bar.addMenu('Help')

        # 메뉴 항목에 액션 추가 예제 (더 많은 액션 추가 가능)
        file_menu.addAction('Open')
        file_menu.addAction('Exit')
        help_menu.addAction('About')

        # 메뉴 바를 레이아웃에 추가
        layout.setMenuBar(self.menu_bar)



        # Rest of your UI elements (config_path, checkpoint_path, etc.)

        self.setLayout(layout)

        self.config_path_edit = QLineEdit(self)
        self.checkpoint_path_edit = QLineEdit(self)
        self.img_path_edit = QLineEdit(self)
        self.output_edit = QTextEdit(self)
        self.output_edit.setReadOnly(True)

        layout.addWidget(QLabel('D드라이브 video 폴더 안의 파일을 선택해주세요'))

        layout.addWidget(QLabel('Config Path:'))
        layout.addWidget(self.config_path_edit)
        config_path_button = QPushButton('Browse', self)
        config_path_button.clicked.connect(lambda: self.browse_file(self.config_path_edit))
        layout.addWidget(config_path_button)

        layout.addWidget(QLabel('Checkpoint Path:'))
        layout.addWidget(self.checkpoint_path_edit)
        checkpoint_path_button = QPushButton('Browse', self)
        checkpoint_path_button.clicked.connect(lambda: self.browse_file(self.checkpoint_path_edit))
        layout.addWidget(checkpoint_path_button)

        layout.addWidget(QLabel('Image Path:'))
        layout.addWidget(self.img_path_edit)
        img_path_button = QPushButton('Browse', self)
        img_path_button.clicked.connect(lambda: self.browse_file(self.img_path_edit))
        layout.addWidget(img_path_button)

        run_button = QPushButton('Run Model in Docker', self)
        run_button.clicked.connect(self.on_run)
        layout.addWidget(run_button)

        layout.addWidget(QLabel('Output:'))
        layout.addWidget(self.output_edit)

        self.setLayout(layout)

    def browse_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if file_name:
            line_edit.setText(file_name)

    def on_run(self):
        config_path = self.config_path_edit.text()
        checkpoint_path = self.checkpoint_path_edit.text()
        img_path = self.img_path_edit.text()

        # SSH Connection to Docker Container
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('localhost', port=2222, username='root', password='0801')  # Replace with actual credentials

        # Command to run the script inside the container
        command = f'/opt/conda/bin/python /data/Eugene-deploy/deep_label_inference.py'
        if config_path:
            command += f' --config "{config_path}"'
        if checkpoint_path:
            command += f' --checkpoint "{checkpoint_path}"'
        if img_path:
            command += f' --video "{img_path}"'
        stdin, stdout, stderr = ssh.exec_command(command)

        # Fetch the output and error
        output = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            self.output_edit.setText("Error: " + error)
        elif output:
            # Extracting the relevant part of the output
            predicted_class = None
            for line in output.split('\n'):
                if line.startswith("Predicted Class for the video:"):
                    predicted_class = line.strip()
                    break
            if predicted_class:
                self.output_edit.setText(predicted_class)
            else:
                self.output_edit.setText("Output received, but no prediction found.")
        else:
            pass

        ssh.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())