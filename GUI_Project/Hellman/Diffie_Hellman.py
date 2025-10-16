from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTextEdit
)
import math
import random

class DiffieHellmanDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diffie-Hellman Шифрование и Дешифровка")
        self.resize(520, 500)

        layout = QVBoxLayout()

        # Исходный текст
        layout.addWidget(QLabel("Исходный текст:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите текст для шифрования...")
        layout.addWidget(self.input_text)

        # Кнопки
        self.btn_encrypt = QPushButton("🔒 Зашифровать")
        self.btn_decrypt = QPushButton("🔓 Расшифровать")
        layout.addWidget(self.btn_encrypt)
        layout.addWidget(self.btn_decrypt)

        # Результаты
        layout.addWidget(QLabel("Зашифрованный текст:"))
        self.encrypted_text = QTextEdit()
        self.encrypted_text.setReadOnly(True)
        layout.addWidget(self.encrypted_text)

        layout.addWidget(QLabel("Расшифрованный текст:"))
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)
        layout.addWidget(self.decrypted_text)

        self.setLayout(layout)

        # Сигналы
        self.btn_encrypt.clicked.connect(self.encrypt_text)
        self.btn_decrypt.clicked.connect(self.decrypt_text)

        # Параметры DH
        self.shift = None
        self.encrypted = ""

    def generate_shared_key(self):
        # Простые числа (~20 разрядов)
        p = 32416190071  # простое число
        g = 5
        a = random.randint(10**9, 10**10)
        b = random.randint(10**9, 10**10)

        A = pow(g, a, p)
        B = pow(g, b, p)

        K_A = pow(B, a, p)
        K_B = pow(A, b, p)
        K = K_A  # общий ключ

        # Используем тангенс для сдвига
        key_value = abs(math.tan(K)) % 1
        shift = int(key_value * 255)
        return shift

    def encrypt_text(self):
        text = self.input_text.toPlainText()
        if not text:
            self.encrypted_text.setPlainText("Введите текст.")
            return

        self.shift = self.generate_shared_key()
        encrypted = ''.join(chr((ord(c) + self.shift) % 256) for c in text)
        self.encrypted = encrypted
        self.encrypted_text.setPlainText(encrypted)
        self.decrypted_text.clear()

    def decrypt_text(self):
        if not self.encrypted:
            self.decrypted_text.setPlainText("Сначала выполните шифрование.")
            return
        if self.shift is None:
            self.decrypted_text.setPlainText("Ключ не найден.")
            return

        decrypted = ''.join(chr((ord(c) - self.shift) % 256) for c in self.encrypted)
        self.decrypted_text.setPlainText(decrypted)

if __name__ == "__main__":
    app = QApplication([])
    window = DiffieHellmanDemo()
    window.show()
    app.exec()