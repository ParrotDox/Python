import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QLabel, QLineEdit, 
                               QPushButton, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt

class CRC16Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('CRC16')
        self.setGeometry(100, 100, 700, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Группа для ввода данных
        input_group = QGroupBox("Входные данные")
        input_layout = QVBoxLayout(input_group)
        
        self.input_label = QLabel("Введите двоичную последовательность (только 0 и 1):")
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Например: 110010")
        self.input_text.textChanged.connect(self.calculate_crc)
        
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_text)
        
        # Группа для результатов
        result_group = QGroupBox("Процесс расчета CRC16")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(300)
        
        result_layout.addWidget(self.result_text)
        
        # Группа для проверки целостности
        verify_group = QGroupBox("Проверка целостности данных")
        verify_layout = QVBoxLayout(verify_group)
        
        verify_input_layout = QHBoxLayout()
        self.verify_label = QLabel("CRC16 для проверки (бинарный):")
        self.verify_input = QLineEdit()
        self.verify_input.setPlaceholderText("Введите FCS16 для проверки...")
        self.verify_btn = QPushButton("Проверить")
        self.verify_btn.clicked.connect(self.verify_fcs)
        
        verify_input_layout.addWidget(self.verify_label)
        verify_input_layout.addWidget(self.verify_input)
        verify_input_layout.addWidget(self.verify_btn)
        
        self.verify_result = QLabel("")
        self.verify_result.setAlignment(Qt.AlignCenter)
        self.verify_result.setStyleSheet("font-weight: bold; padding: 10px;")
        
        verify_layout.addLayout(verify_input_layout)
        verify_layout.addWidget(self.verify_result)
        
        layout.addWidget(input_group)
        layout.addWidget(result_group)
        layout.addWidget(verify_group)
        
        self.calculate_crc()
    
    def binary_string_to_bits(self, binary_str):
        """Преобразует бинарную строку в список битов"""
        return [int(bit) for bit in binary_str if bit in '01']
    
    def bits_to_binary_string(self, bits):
        """Преобразует список битов в бинарную строку"""
        return ''.join(str(bit) for bit in bits)
    
    def crc16(self, data_bits):
        """Алгоритм CRC16"""
        # Полином CRC16: x^16 + x^12 + x^5 + 1 = 0x11021
        # В бинарном виде: 1 0001 0000 0010 0001
        poly_bits = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]  # 16 бит + 1 неявный
        
        process_log = []
        
        # Добавляем 16 нулей к данным
        frame_bits = data_bits + [0] * 16
        process_log.append(f"Исходные данные: {self.bits_to_binary_string(data_bits)}")
        process_log.append(f"Данные с 16 нулями: {self.bits_to_binary_string(frame_bits)}")
        process_log.append(f"Полином (ключ): {self.bits_to_binary_string(poly_bits)}")
        process_log.append("")
        
        # Начинаем с первых 16 бит
        current_bits = frame_bits[:16]
        remaining_bits = frame_bits[16:]
        
        step = 1
        while len(remaining_bits) > 0:
            process_log.append(f"Шаг {step}:")
            process_log.append(f"  Текущие биты: {self.bits_to_binary_string(current_bits)}")
            
            # Если старший бит = 1, делаем XOR с полиномом
            if current_bits[0] == 1:
                process_log.append(f"  Старший бит = 1 => XOR с полиномом")
                # XOR с полиномом
                new_bits = []
                for i in range(16):
                    new_bits.append(current_bits[i] ^ poly_bits[i])
                current_bits = new_bits
                process_log.append(f"  После XOR: {self.bits_to_binary_string(current_bits)}")
            else:
                process_log.append(f"  Старший бит = 0 → пропускаем")
            
            # Сдвигаем влево и добавляем следующий бит
            current_bits = current_bits[1:] + [remaining_bits[0]]
            remaining_bits = remaining_bits[1:]
            
            process_log.append(f"  После сдвига: {self.bits_to_binary_string(current_bits)}")
            process_log.append("")
            step += 1
        
        # Финальный результат - оставшиеся 16 бит
        FCS_bits = current_bits
        crc_value = int(self.bits_to_binary_string(FCS_bits), 2)
        
        process_log.append(f"Финальный FCS16: {self.bits_to_binary_string(FCS_bits)} = 0x{crc_value:04X}")
        
        return FCS_bits, crc_value, process_log
    
    def calculate_crc(self):
        input_data = self.input_text.text().strip()
        
        if not input_data:
            self.result_text.setPlainText("Введите двоичную последовательность")
            return
        
        # Проверяем, что ввод содержит только 0 и 1
        if not all(bit in '01' for bit in input_data):
            self.result_text.setPlainText("Ошибка: вводите только двоичные цифры (0 и 1)")
            return
        
        data_bits = self.binary_string_to_bits(input_data)
        FCS_bits, crc_value, process_log = self.crc16(data_bits)
        
        result = "\n".join(process_log)
        result += f"\n\nИтоговые данные для передачи:"
        result += f"\nДанные: {input_data}"
        result += f"\nFCS16: {self.bits_to_binary_string(FCS_bits)}"
        result += f"\nКадр: {input_data}{self.bits_to_binary_string(FCS_bits)}"
        result += f"\n\nFCS16 в разных форматах:"
        result += f"\n- Двоичный: {self.bits_to_binary_string(FCS_bits)}"
        result += f"\n- Шестнадцатеричный: 0x{crc_value:04X}"
        result += f"\n- Десятичный: {crc_value}"
        
        self.result_text.setPlainText(result)
    
    def verify_fcs(self):
        """Правильная проверка целостности данных"""
        input_data = self.input_text.text().strip()
        verify_fcs = self.verify_input.text().strip()

        if not input_data:
            self.verify_result.setText("Введите данные для проверки")
            self.verify_result.setStyleSheet("color: orange; font-weight: bold; padding: 10px;")
            return

        if not verify_fcs:
            self.verify_result.setText("Введите FCS16 для проверки")
            self.verify_result.setStyleSheet("color: orange; font-weight: bold; padding: 10px;")
            return

        # Проверяем формат CRC
        if not all(bit in '01' for bit in verify_fcs) or len(verify_fcs) != 16:
            self.verify_result.setText("Ошибка: FCS16 должен быть 16 бит (16 цифр 0/1)")
            self.verify_result.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
            return

        # 1. Берем данные и полученный CRC
        data_bits = self.binary_string_to_bits(input_data)
        received_FCS_bits = self.binary_string_to_bits(verify_fcs)

        # 2. Формируем кадр: данные + полученный CRC
        frame_bits = data_bits + received_FCS_bits

        # 3. Проверяем кадр: frame_bits + 16 нулей → алгоритм
        check_bits = frame_bits + [0] * 16
        current_bits = check_bits[:16]
        remaining_bits = check_bits[16:]

        # Выполняем тот же алгоритм
        poly_bits = [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]

        while len(remaining_bits) > 0:
            if current_bits[0] == 1:
                # XOR с полиномом
                new_bits = []
                for i in range(16):
                    new_bits.append(current_bits[i] ^ poly_bits[i])
                current_bits = new_bits

            # Сдвигаем и добавляем следующий бит
            current_bits = current_bits[1:] + [remaining_bits[0]]
            remaining_bits = remaining_bits[1:]

        # 4. Проверяем результат
        result_bits = current_bits
        is_valid = all(bit == 0 for bit in result_bits)

        if is_valid:
            self.verify_result.setText("Целостность данных подтверждена!\nОстаток = 0")
            self.verify_result.setStyleSheet("color: green; font-weight: bold; padding: 10px;")
        else:
            result_str = self.bits_to_binary_string(result_bits)
            self.verify_result.setText(f"Обнаружена ошибка в данных!\nОстаток: {result_str}")
            self.verify_result.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
def main():
    app = QApplication(sys.argv)
    window = CRC16Calculator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()