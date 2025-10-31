import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QTextEdit, QPushButton, 
                               QLabel, QFileDialog, QMessageBox, QSpinBox)
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

class CryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cipher = BlockCipher()
        self.current_file_path = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Блочное шифрование - 64 бита")
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout()
        
        # Поле для ввода ключа
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Ключ (4 байта):"))
        self.key_input = QTextEdit()
        self.key_input.setMaximumHeight(60)
        self.key_input.setPlaceholderText("Введите ключ длиной 4 символа (ASCII)")
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)
        
        # Настройки
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Количество раундов:"))
        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 32)
        self.rounds_spin.setValue(16)
        self.rounds_spin.valueChanged.connect(self.update_rounds)
        settings_layout.addWidget(self.rounds_spin)
        settings_layout.addStretch()
        layout.addLayout(settings_layout)
        
        # Информация о файле
        self.file_info_label = QLabel("Файл не выбран")
        self.file_info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.file_info_label)
        
        # Поля для ввода текста
        text_layout = QHBoxLayout()
        
        # Исходный текст
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Исходный текст:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Введите текст для шифрования или загрузите файл...")
        left_layout.addWidget(self.input_text)
        
        # Результат
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Результат:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Здесь появится результат шифрования/дешифрования...")
        right_layout.addWidget(self.output_text)
        
        text_layout.addLayout(left_layout)
        text_layout.addLayout(right_layout)
        layout.addLayout(text_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.encrypt_btn = QPushButton("Зашифровать текст")
        self.encrypt_btn.clicked.connect(self.encrypt_text)
        button_layout.addWidget(self.encrypt_btn)
        
        self.decrypt_btn = QPushButton("Расшифровать текст")
        self.decrypt_btn.clicked.connect(self.decrypt_text)
        button_layout.addWidget(self.decrypt_btn)
        
        self.load_file_btn = QPushButton("Загрузить файл")
        self.load_file_btn.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_file_btn)
        
        self.save_file_btn = QPushButton("Сохранить результат")
        self.save_file_btn.clicked.connect(self.save_file)
        button_layout.addWidget(self.save_file_btn)
        
        layout.addLayout(button_layout)
        
        # Статус
        self.status_label = QLabel("Готов")
        layout.addWidget(self.status_label)
        
        central_widget.setLayout(layout)
    
    def update_rounds(self):
        self.cipher.rounds = self.rounds_spin.value()
        self.status_label.setText(f"Установлено раундов: {self.rounds_spin.value()}")
    
    def get_key(self):
        """Получение ключа из поля ввода"""
        key_text = self.key_input.toPlainText().strip()
        if len(key_text) < 4:
            QMessageBox.warning(self, "Ошибка", "Ключ должен содержать минимум 4 символа")
            return None
        
        # Берем первые 4 символа и преобразуем в байты
        return key_text[:4].encode('utf-8')
    
    def encrypt_text(self):
        key = self.get_key()
        if key is None:
            return
        
        try:
            plaintext = self.input_text.toPlainText().encode('utf-8')
            ciphertext = self.cipher.encrypt(plaintext, key)
            
            # Отображаем в hex формате для наглядности
            hex_result = ciphertext.hex()
            self.output_text.setPlainText(hex_result)
            self.status_label.setText(f"Текст зашифрован: {len(plaintext)} байт → {len(ciphertext)} байт")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при шифровании: {str(e)}")
    
    def decrypt_text(self):
        key = self.get_key()
        if key is None:
            return
        
        try:
            # Пытаемся интерпретировать ввод как hex
            ciphertext_hex = self.input_text.toPlainText().strip()
            ciphertext = bytes.fromhex(ciphertext_hex)
            
            plaintext = self.cipher.decrypt(ciphertext, key)
            
            # Пытаемся декодировать как UTF-8, удаляем нулевые байты дополнения
            try:
                text_result = plaintext.decode('utf-8').rstrip('\x00')
            except:
                text_result = f"Бинарные данные (hex): {plaintext.hex()}"
            
            self.output_text.setPlainText(text_result)
            self.status_label.setText(f"Текст расшифрован: {len(ciphertext)} байт → {len(plaintext)} байт")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при дешифровании: {str(e)}")
    
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            try:
                self.current_file_path = file_path
                
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Показываем информацию о файле
                file_size = len(content)
                file_name = os.path.basename(file_path)
                self.file_info_label.setText(f"Файл: {file_name} | Размер: {file_size} байт")
                
                # Пытаемся показать как текст, если это текстовый файл
                try:
                    text_content = content.decode('utf-8')
                    self.input_text.setPlainText(text_content)
                    self.status_label.setText(f"Загружен текстовый файл: {file_name}")
                except UnicodeDecodeError:
                    # Если не текстовый файл, показываем информацию и очищаем поле
                    self.input_text.clear()
                    self.status_label.setText(f"Загружен бинарный файл: {file_name} (используйте кнопки шифрования/дешифрования файлов)")
                    QMessageBox.information(self, "Информация", 
                                          f"Загружен бинарный файл.\n"
                                          f"Для работы с бинарными файлами используйте специальные кнопки.")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")
    
    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить результат")
        if file_path:
            try:
                # Для сохранения пытаемся получить данные из output_text
                output_text = self.output_text.toPlainText().strip()
                
                if not output_text:
                    QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
                    return
                
                # Если вывод в hex формате, конвертируем обратно в bytes
                if all(c in '0123456789abcdefABCDEF' for c in output_text.replace('\n', '').replace(' ', '')):
                    content = bytes.fromhex(output_text.replace('\n', '').replace(' ', ''))
                else:
                    # Иначе сохраняем как текст
                    content = output_text.encode('utf-8')
                
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                self.status_label.setText(f"Результат сохранен в: {file_path}")
                QMessageBox.information(self, "Успех", f"Файл успешно сохранен!\nРазмер: {len(content)} байт")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = CryptoApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()