import sys
import paramiko
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QLineEdit, QFileDialog

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Docker Control GUI'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        layout = QVBoxLayout()

        self.config_path_edit = QLineEdit(self)
        self.checkpoint_path_edit = QLineEdit(self)
        self.img_path_edit = QLineEdit(self)

        layout.addWidget(QLabel('Config Path:'))
        layout.addWidget(self.config_path_edit)
        layout.addWidget(QLabel('Checkpoint Path:'))
        layout.addWidget(self.checkpoint_path_edit)
        layout.addWidget(QLabel('Image Path:'))
        layout.addWidget(self.img_path_edit)

        run_button = QPushButton('Run Model in Docker', self)
        run_button.clicked.connect(self.on_run)
        layout.addWidget(run_button)

        self.setLayout(layout)

    def on_run(self):
        config_path = self.config_path_edit.text()
        checkpoint_path = self.checkpoint_path_edit.text()
        img_path = self.img_path_edit.text()

        # SSH Connection to Docker Container
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('localhost', port=2222, username='root', password='0801')  # Replace with actual credentials

        # Command to run the script inside the container
        command = f'/opt/conda/bin/python /data/mmaction2_for_deploy/inference_connect.py {config_path} {checkpoint_path} {img_path}'
        stdin, stdout, stderr = ssh.exec_command(command)

        # Fetch the output and error
        output = stdout.read()
        error = stderr.read()

        if error:
            print("Error:", error.decode())
        else:
            print("Output:", output.decode())

        ssh.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())