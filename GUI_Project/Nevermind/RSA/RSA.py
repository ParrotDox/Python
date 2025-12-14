from random import randint
from math import gcd
from sympy import randprime
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QTextEdit, QPushButton, 
                               QWidget, QLabel, QMessageBox)
from PySide6.QtCore import Qt

class RSA():
    p, q = randprime(4096, 10000), randprime(4096, 10000)
    n = p * q
    f = (p - 1)*(q - 1) #Euler function
    e = None    #encrypt number
    d = None    #decrypt number
    publicKey = []
    privateKey = []
    
    def __init__(self):
        self.e = self.findE()
        self.d = pow(self.e, -1, self.f)
        self.publicKey = [self.n, self.e]
        self.privateKey = [self.n, self.d]
        print("RSA constructor called")
        print(f"p = {self.p} q = {self.q}")
        print(f"n = {self.n}")
        print(f"f = {self.f}")
        print(f"e = {self.e}")
        print(f"d = {self.d}")
        print(f"Check {self.e * self.d % self.f}")
    
    #Euclidean algorithm
    def findE(self):
        divisors = []
        for e in range(2, self.n):
            if gcd(e, self.f) == 1:
                divisors.append(e)
        return divisors[randint(0, len(divisors)-1)]
    
    def encrypt(self, msg: int):
        return pow(msg, self.e, self.n)
    
    def decrypt(self, encryptedMsg: int):
        return pow(encryptedMsg, self.d, self.n)
    
    def text_to_numbers(self, text: str):
        """Convert text to list of numbers"""
        return [self.encrypt(ord(char)) for char in text]
    
    def numbers_to_text(self, numbers: list):
        """Convert list of numbers back to text"""
        return ''.join([chr(self.decrypt(num)) for num in numbers])


class RSACryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rsa = RSA()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("RSA Encryption Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("RSA Encryption/Decryption Tool")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Info label
        info_label = QLabel(f"Key Info: n={self.rsa.n}, e={self.rsa.e}, d={self.rsa.d}")
        info_label.setStyleSheet("font-size: 10px; color: gray; margin: 5px;")
        layout.addWidget(info_label)
        
        # Horizontal layout for input/output
        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)
        
        # Left side - Input
        left_layout = QVBoxLayout()
        content_layout.addLayout(left_layout)
        
        left_layout.addWidget(QLabel("Original Text:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter text to encrypt here...")
        left_layout.addWidget(self.input_text)
        
        # Right side - Output
        right_layout = QVBoxLayout()
        content_layout.addLayout(right_layout)
        
        right_layout.addWidget(QLabel("Decrypted Text:"))
        self.output_text = QTextEdit()
        self.output_text.setPlaceholderText("Decrypted text will appear here...")
        self.output_text.setReadOnly(True)
        right_layout.addWidget(self.output_text)
        
        # Middle - Buttons
        middle_layout = QVBoxLayout()
        content_layout.addLayout(middle_layout)
        
        middle_layout.addStretch()
        
        self.encrypt_btn = QPushButton("Encrypt →")
        self.encrypt_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; }")
        self.encrypt_btn.clicked.connect(self.encrypt_text)
        middle_layout.addWidget(self.encrypt_btn)
        
        middle_layout.addStretch()
        
        # Encrypted data display
        layout.addWidget(QLabel("Encrypted Data (Numbers):"))
        self.encrypted_display = QTextEdit()
        self.encrypted_display.setPlaceholderText("Encrypted numbers will appear here...")
        self.encrypted_display.setReadOnly(True)
        self.encrypted_display.setMaximumHeight(100)
        layout.addWidget(self.encrypted_display)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 12px; color: green; margin: 5px;")
        layout.addWidget(self.status_label)
    
    def encrypt_text(self):
        try:
            # Get input text
            text = self.input_text.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "Warning", "Please enter some text to encrypt")
                return
            
            # Encrypt text
            encrypted_numbers = self.rsa.text_to_numbers(text)
            
            # Display encrypted numbers
            self.encrypted_display.setPlainText(", ".join(map(str, encrypted_numbers)))
            
            # Decrypt back and display
            decrypted_text = self.rsa.numbers_to_text(encrypted_numbers)
            self.output_text.setPlainText(decrypted_text)
            
            # Update status
            self.status_label.setText(f"✓ Success! Encrypted {len(text)} characters")
            self.status_label.setStyleSheet("font-size: 12px; color: green; margin: 5px;")
            
        except Exception as e:
            error_msg = f"Encryption error: {str(e)}"
            self.status_label.setText(f"✗ {error_msg}")
            self.status_label.setStyleSheet("font-size: 12px; color: red; margin: 5px;")
            QMessageBox.critical(self, "Error", error_msg)


if __name__ == "__main__":
    app = QApplication([])
    
    window = RSACryptoApp()
    window.show()
    
    app.exec()