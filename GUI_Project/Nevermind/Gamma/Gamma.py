import sys, random
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QMessageBox

BLOCK_SIZE = 32  # размер блока в битах

def str_to_blocks(text):
    blocks = []
    for i in range(0, len(text), 4):
        chunk = text[i:i+4].ljust(4, '\0')
        blocks.append(int.from_bytes(chunk.encode('utf-8'), 'big'))
    return blocks

def blocks_to_str(blocks):
    s = b''.join(b.to_bytes(4, 'big') for b in blocks)
    return s.rstrip(b'\0').decode('utf-8', errors='ignore')

def generate_key(n_blocks):
    return [random.getrandbits(BLOCK_SIZE) for _ in range(n_blocks)]

def xor_mod_blocks(blocks, key, N):
    mod = 2 ** N
    return [(b ^ k) % mod for b, k in zip(blocks, key)]

def blocks_to_bin(blocks, size=32):
    return ' '.join(f"{b:0{size}b}" for b in blocks)

class XORModCipherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 500)
        self.setWindowTitle("XOR + mod 2^N Гаммирование с проверкой N")
        self.layout: QVBoxLayout = QVBoxLayout()

        self.input_label = QLabel("Открытый текст:")
        self.input_text = QTextEdit()
        self.output_label = QLabel("Выходной текст:")
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.info_label = QLabel("Информация о шифровании:")

        self.button_layout = QHBoxLayout()
        self.encrypt_btn = QPushButton("Зашифровать")
        self.decrypt_btn = QPushButton("Расшифровать")
        self.clear_btn = QPushButton("Очистить")
        self.button_layout.addWidget(self.encrypt_btn)
        self.button_layout.addWidget(self.decrypt_btn)
        self.button_layout.addWidget(self.clear_btn)

        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_text)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_text)
        self.layout.addWidget(self.info_label)
        self.setLayout(self.layout)

        self.encrypt_btn.clicked.connect(self.encrypt)
        self.decrypt_btn.clicked.connect(self.decrypt)
        self.clear_btn.clicked.connect(self.clear_all)

        self.key = []
        self.last_plain_blocks = []

    def encrypt(self):
        text = self.input_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для шифрования!")
            return
        blocks = str_to_blocks(text)
        N = len(blocks)
        if N < BLOCK_SIZE:
            QMessageBox.warning(self, "Ошибка", f"Число блоков ({N}) меньше размера блока ({BLOCK_SIZE} бит). Шифрование запрещено!")
            return
        self.last_plain_blocks = blocks
        self.key = generate_key(N)
        cipher_blocks = xor_mod_blocks(blocks, self.key, N)

        hex_cipher = ' '.join(f"{b:08X}" for b in cipher_blocks)
        bin_cipher = blocks_to_bin(cipher_blocks, N.bit_length())
        hex_key = ' '.join(f"{k:08X}" for k in self.key)
        bin_key = blocks_to_bin(self.key)

        info_text = (
            f"Размер блока: {BLOCK_SIZE} бит\n"
            f"Число блоков (N): {N}\n\n"
            f"Гамма (HEX): {hex_key}\n"
            f"Гамма (BIN): {bin_key}\n\n"
            f"Зашифрованный текст (HEX): {hex_cipher}\n"
            f"Зашифрованный текст (BIN): {bin_cipher}"
        )
        self.output_text.setText(hex_cipher)
        self.info_label.setText(info_text)

    def decrypt(self):
        if not self.key or not self.last_plain_blocks:
            QMessageBox.warning(self, "Ошибка", "Сначала зашифруйте текст!")
            return
        N = len(self.last_plain_blocks)
        if N < BLOCK_SIZE:
            QMessageBox.warning(self, "Ошибка", f"Число блоков ({N}) меньше размера блока ({BLOCK_SIZE} бит). Дешифровка запрещена!")
            return
        cipher_text = self.output_text.toPlainText().split()
        try:
            cipher_blocks = [int(b, 16) for b in cipher_text]
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректный зашифрованный текст!")
            return
        plain_blocks = xor_mod_blocks(cipher_blocks, self.key, N)
        decrypted_text = blocks_to_str(plain_blocks)
        self.output_text.setText(decrypted_text)

    def clear_all(self):
        self.input_text.clear()
        self.output_text.clear()
        self.info_label.setText("Информация о шифровании:")
        self.key = []
        self.last_plain_blocks = []

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = XORModCipherApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
