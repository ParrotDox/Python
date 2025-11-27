import sys
import os
import hashlib
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QTextEdit, QPushButton, 
                               QLabel, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt

class BlockCipher:
    def __init__(self):
        self.block_size = 8  # 64 бит = 8 байт
        self.key_size = 4    # 32 бита = 4 байта
        self.rounds = 16
        self.const = 0x9E3779B9  # Константа для генерации ключей
    
    def generate_round_keys(self, key):
        """Генерация раундовых ключей"""
        keys = []
        key_int = int.from_bytes(key, byteorder='big')
        for i in range(self.rounds):
            round_key = (key_int + i * self.const) & 0xFFFFFFFF
            keys.append(round_key)
        return keys
    
    def feistel_function(self, data, key):
        result = ((data + key) & 0xFFFFFFFF) ^ ((data << 3) & 0xFFFFFFFF) ^ ((key >> 2) & 0xFFFFFFFF)
        return result & 0xFFFFFFFF
    
    def process_block(self, block, keys, encrypt=True):
        """Обработка одного блока (шифрование/дешифрование)"""
        if len(block) != self.block_size:
            # Дополнение блока если необходимо
            block = block.ljust(self.block_size, b'\x00')
        
        # Разделение на две половины
        left = int.from_bytes(block[:4], byteorder='big')
        right = int.from_bytes(block[4:], byteorder='big')
        
        if encrypt:
            # Шифрование
            for i in range(self.rounds):
                next_left = right
                next_right = left ^ self.feistel_function(right, keys[i])
                left, right = next_left, next_right
        else:
            # Дешифрование
            for i in range(self.rounds-1, -1, -1):
                next_right = left
                next_left = right ^ self.feistel_function(left, keys[i])
                left, right = next_left, next_right
        
        # Объединение половин
        result = left.to_bytes(4, byteorder='big') + right.to_bytes(4, byteorder='big')
        return result
    
    def encrypt(self, data, key):
        """Шифрование данных"""
        if len(key) != self.key_size:
            raise ValueError(f"Key must be {self.key_size} bytes")
        
        keys = self.generate_round_keys(key)
        
        # Разбиение на блоки
        encrypted_blocks = []
        for i in range(0, len(data), self.block_size):
            block = data[i:i+self.block_size]
            encrypted_block = self.process_block(block, keys, encrypt=True)
            encrypted_blocks.append(encrypted_block)
        
        return b''.join(encrypted_blocks)
    
    def decrypt(self, data, key):
        """Дешифрование данных"""
        if len(key) != self.key_size:
            raise ValueError(f"Key must be {self.key_size} bytes")
        
        keys = self.generate_round_keys(key)
        
        # Разбиение на блоки
        decrypted_blocks = []
        for i in range(0, len(data), self.block_size):
            block = data[i:i+self.block_size]
            decrypted_block = self.process_block(block, keys, encrypt=False)
            decrypted_blocks.append(decrypted_block)
        
        return b''.join(decrypted_blocks)

class PasswordHasher:
    def __init__(self):
        self.cipher = BlockCipher()
        self.stored_hash = None
        self.encrypted_data = None  # Сохраняем зашифрованные данные до SHA-256
    
    def pad_password(self, password):
        """Дополнение пароля до 28 символов"""
        if len(password) < 4 or len(password) > 28:
            raise ValueError("Длина пароля должна быть от 4 до 28 символов")
        
        # Дополняем пароль до 28 символов нулевыми байтами
        padded = password.ljust(28, '\x00')
        return padded.encode('utf-8')
    
    def remove_padding(self, padded_data):
        """Удаление дополнения из пароля"""
        try:
            decoded = padded_data.decode('utf-8', errors='ignore')
            return decoded.rstrip('\x00')
        except:
            return "Невозможно декодировать пароль"
    
    def hash_password(self, password):
        """Хеширование пароля с использованием блочного шифра"""
        # Проверяем длину пароля
        if len(password) < 4 or len(password) > 28:
            raise ValueError("Длина пароля должна быть от 4 до 28 символов")
        
        # Дополняем пароль
        padded_password = self.pad_password(password)
        
        # Используем фиксированный ключ для хеширования
        key = b'HASH'  # Фиксированный ключ для хеширования
        
        # Шифруем пароль с помощью блочного шифра
        self.encrypted_data = self.cipher.encrypt(padded_password, key)
        
        # Применяем SHA-256 к зашифрованному результату
        final_hash = hashlib.sha256(self.encrypted_data).digest()
        
        # Сохраняем хеш
        self.stored_hash = final_hash
        
        return final_hash
    
    def get_stored_hash(self):
        """Получить сохраненный хеш"""
        return self.stored_hash
    
    def verify_password(self, password):
        """Проверка пароля против сохраненного хеша"""
        if self.stored_hash is None:
            raise ValueError("Сначала создайте хеш пароля")
        
        new_hash = self.hash_password(password)
        return new_hash == self.stored_hash
    
    def decrypt_encrypted_data(self):
        """Дешифрование зашифрованных данных (до применения SHA-256)"""
        if self.encrypted_data is None:
            raise ValueError("Нет зашифрованных данных для дешифрования")
        
        key = b'HASH'
        try:
            # Дешифруем зашифрованные данные
            decrypted = self.cipher.decrypt(self.encrypted_data, key)
            original_password = self.remove_padding(decrypted)
            return original_password
        except Exception as e:
            return f"Ошибка при дешифровании: {str(e)}"

class PasswordHashApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hasher = PasswordHasher()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Хеширование паролей с блочным шифром")
        self.setGeometry(100, 100, 700, 500)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Хеширование паролей")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Информация о требованиях
        info_label = QLabel("Длина пароля: от 4 до 28 символов")
        info_label.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Поле для ввода пароля
        password_layout = QVBoxLayout()
        password_layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль (4-28 символов)")
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Кнопки операций
        buttons_layout = QHBoxLayout()
        
        self.hash_btn = QPushButton("Захешировать пароль")
        self.hash_btn.clicked.connect(self.hash_password)
        buttons_layout.addWidget(self.hash_btn)
        
        self.verify_btn = QPushButton("Проверить пароль")
        self.verify_btn.clicked.connect(self.verify_password)
        buttons_layout.addWidget(self.verify_btn)
        
        self.decrypt_btn = QPushButton("Расшифровать данные")
        self.decrypt_btn.clicked.connect(self.decrypt_data)
        buttons_layout.addWidget(self.decrypt_btn)
        
        layout.addLayout(buttons_layout)
        
        # Поле для вывода хеша
        hash_layout = QVBoxLayout()
        hash_layout.addWidget(QLabel("Захешированный пароль (hex):"))
        self.hash_output = QTextEdit()
        self.hash_output.setReadOnly(True)
        self.hash_output.setMaximumHeight(80)
        self.hash_output.setPlaceholderText("Здесь появится хеш пароля...")
        hash_layout.addWidget(self.hash_output)
        layout.addLayout(hash_layout)
        
        # Поле для результатов
        result_layout = QVBoxLayout()
        result_layout.addWidget(QLabel("Результат:"))
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Здесь появится результат операций...")
        result_layout.addWidget(self.result_output)
        layout.addLayout(result_layout)
        
        # Кнопка очистки
        self.clear_btn = QPushButton("Очистить все")
        self.clear_btn.clicked.connect(self.clear_all)
        layout.addWidget(self.clear_btn)
        
        # Статус
        self.status_label = QLabel("Готов")
        self.status_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.status_label)
        
        central_widget.setLayout(layout)
    
    def hash_password(self):
        """Хеширование введенного пароля"""
        password = self.password_input.text().strip()
        
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            return
        
        try:
            # Генерируем хеш
            password_hash = self.hasher.hash_password(password)
            
            # Отображаем хеш в hex формате
            hex_hash = password_hash.hex()
            self.hash_output.setPlainText(hex_hash)
            
            self.result_output.setPlainText(
                f"Пароль успешно захеширован!\n"
                f"Длина пароля: {len(password)} символов\n"
                f"Размер хеша: {len(password_hash)} байт\n"
                f"Алгоритм: Блочный шифр → SHA-256"
            )
            self.status_label.setText("Пароль захеширован")
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при хешировании: {str(e)}")
    
    def verify_password(self):
        """Проверка пароля против сохраненного хеша"""
        password = self.password_input.text().strip()
        
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль для проверки")
            return
        
        try:
            is_valid = self.hasher.verify_password(password)
            
            if is_valid:
                self.result_output.setPlainText("✓ Пароль ВЕРНЫЙ - соответствует сохраненному хешу")
                self.result_output.setStyleSheet("color: green; font-weight: bold;")
                self.status_label.setText("Пароль верный")
            else:
                self.result_output.setPlainText("✗ Пароль НЕВЕРНЫЙ - не соответствует сохраненному хешу")
                self.result_output.setStyleSheet("color: red; font-weight: bold;")
                self.status_label.setText("Пароль неверный")
                
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке: {str(e)}")
    
    def decrypt_data(self):
        """Дешифрование зашифрованных данных (до SHA-256)"""
        try:
            result = self.hasher.decrypt_encrypted_data()
            self.result_output.setPlainText(f"Результат дешифрования:\nИсходный пароль: '{result}'")
            self.result_output.setStyleSheet("color: blue;")
            self.status_label.setText("Данные успешно расшифрованы")
            
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при дешифровании: {str(e)}")
    
    def clear_all(self):
        """Очистка всех полей"""
        self.password_input.clear()
        self.hash_output.clear()
        self.result_output.clear()
        self.result_output.setStyleSheet("")
        self.hasher.stored_hash = None
        self.hasher.encrypted_data = None
        self.status_label.setText("Готов")

def main():
    app = QApplication(sys.argv)
    window = PasswordHashApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()