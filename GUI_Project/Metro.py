import sys
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QPushButton, 
                               QTabWidget, QGroupBox, QSpinBox, QComboBox)
from PySide6.QtCore import QTimer, QDateTime, Qt
from PySide6.QtGui import QFont
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import random

# ==================== ENUMS ====================

class TrainType(Enum):
    PUBLIC = "PUBLIC"
    SERVICE = "SERVICE"

class SensorType(Enum):
    ARRIVAL = "ARRIVAL"
    DEPARTURE = "DEPARTURE"

class ViolationType(Enum):
    ARRIVAL_DELAY = "ARRIVAL_DELAY"
    DEPARTURE_DELAY = "DEPARTURE_DELAY"
    CANCELLATION = "CANCELLATION"

# ==================== DATA CLASSES ====================

@dataclass
class DisplayData:
    data: List[object]
    code: str
    timestamp: datetime

@dataclass
class Station:
    station_id: str
    name: str
    location: str

@dataclass
class Train:
    train_id: str
    train_type: TrainType
    current_station: str
    final_station: str
    is_arrived: bool = False
    is_departed: bool = False
    arrival_time: Optional[datetime] = None
    departure_time: Optional[datetime] = None

@dataclass
class ScheduleItem:
    train_id: str
    route_id: str
    final_station: Station
    planned_arrival: datetime
    planned_departure: datetime
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    arrival_violation_checked: bool = False
    departure_violation_checked: bool = False

@dataclass
class Advertisement:
    ad_id: str
    content: str
    display_order: int
    start_date: datetime
    end_date: datetime
    is_active: bool = True

@dataclass
class ScheduleViolation:
    violation_id: str
    train_id: str
    station_id: str
    planned_time: datetime
    actual_time: datetime
    delay_minutes: int
    violation_type: ViolationType

@dataclass  
class ManagementRequest:
    request_id: str
    request_type: str
    board_id: str
    data: Optional[Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# ==================== CORE CLASSES ====================

class Sensor:
    def __init__(self, sensor_id: str, sensor_type: SensorType, station_id: str):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.station_id = station_id
        self.is_active = True
        
    def send_signal(self, train: Train):
        """Base method for sending signals"""
        print(f"Sensor {self.sensor_id} sent {self.sensor_type.value} signal for train {train.train_id}")

class ArrivalSensor(Sensor):
    def __init__(self, sensor_id: str, station_id: str):
        super().__init__(sensor_id, SensorType.ARRIVAL, station_id)
        
    def detect_arrival(self, train: Train):
        """Detect train arrival"""
        self.send_signal(train)

class DepartureSensor(Sensor):
    def __init__(self, sensor_id: str, station_id: str):
        super().__init__(sensor_id, SensorType.DEPARTURE, station_id)
        
    def detect_departure(self, train: Train):
        """Detect train departure"""
        self.send_signal(train)

class Timer:
    def __init__(self, interval_seconds: int = 5):
        self.interval = interval_seconds
        self.is_running = False
        self.qt_timer = QTimer()
        
    def start(self, callback):
        """Start the timer"""
        self.is_running = True
        self.qt_timer.timeout.connect(callback)
        self.qt_timer.start(self.interval * 1000)
        
    def stop(self):
        """Stop the timer"""
        self.is_running = False
        self.qt_timer.stop()
        
    def tick(self):
        """Trigger timer tick - called by Qt timer"""
        pass

class Schedule:
    def __init__(self, schedule_id: str):
        self.schedule_id = schedule_id
        self.last_update = datetime.now()
        self.items: List[ScheduleItem] = []
        self.stations: Dict[str, Station] = {}
        
    def get_train_schedule(self, train_id: str) -> Optional[ScheduleItem]:
        """Get schedule for specific train"""
        for item in self.items:
            if item.train_id == train_id:
                return item
        return None
    
    def get_station_schedule(self, station_id: str) -> List[ScheduleItem]:
        """Get schedule for specific station"""
        return [item for item in self.items if item.final_station.station_id == station_id]
    
    def find_violations(self) -> List[ScheduleViolation]:
        """Find schedule violations automatically"""
        violations = []
        now = datetime.now()
        
        for item in self.items:
            # Check arrival violations
            if (item.planned_arrival < now and 
                not item.actual_arrival and 
                not item.arrival_violation_checked):
                
                delay = (now - item.planned_arrival).total_seconds() / 60
                if delay > 2:
                    violations.append(ScheduleViolation(
                        violation_id=f"viol_auto_arr_{len(violations)+1}",
                        train_id=item.train_id,
                        station_id=item.final_station.station_id,
                        planned_time=item.planned_arrival,
                        actual_time=now,
                        delay_minutes=int(delay),
                        violation_type=ViolationType.ARRIVAL_DELAY
                    ))
                    item.arrival_violation_checked = True
            
            # Check departure violations
            if (item.planned_departure < now and 
                not item.actual_departure and 
                not item.departure_violation_checked):
                
                delay = (now - item.planned_departure).total_seconds() / 60
                if delay > 2:
                    violations.append(ScheduleViolation(
                        violation_id=f"viol_auto_dep_{len(violations)+1}",
                        train_id=item.train_id,
                        station_id=item.final_station.station_id,
                        planned_time=item.planned_departure,
                        actual_time=now,
                        delay_minutes=int(delay),
                        violation_type=ViolationType.DEPARTURE_DELAY
                    ))
                    item.departure_violation_checked = True
        
        return violations

class AdvertisementManager:
    def __init__(self):
        self.active_ads: List[Advertisement] = []
        self.max_ads = 20
        self.current_index = 0
        
    def get_next_ad(self) -> Optional[Advertisement]:
        """Get next advertisement in rotation"""
        if not self.active_ads:
            return None
            
        ad = self.active_ads[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.active_ads)
        return ad
    
    def update_ads(self, new_ads: List[Advertisement]):
        """Update advertisements list"""
        valid_ads = [ad for ad in new_ads if self.validate_ad(ad)]
        self.active_ads = valid_ads[:self.max_ads]
        self.current_index = 0
    
    def validate_ad(self, ad: Advertisement) -> bool:
        """Validate advertisement"""
        now = datetime.now()
        return (ad.is_active and 
                ad.start_date <= now <= ad.end_date and
                len(ad.content) > 0)

class BoardMemory:
    def __init__(self):
        self.current_schedule: Optional[Schedule] = None
        self.advertisements: List[Advertisement] = []
        self.current_trains: Dict[str, Train] = {}
        self.departure_times: Dict[str, datetime] = {}
        self.violations: List[ScheduleViolation] = []
        self.arrived_trains: Dict[str, Train] = {}
        
    def get_train_final_station(self, train_id: str) -> Optional[str]:
        """Get train's final station"""
        if self.current_schedule:
            item = self.current_schedule.get_train_schedule(train_id)
            return item.final_station.name if item else None
        return None
    
    def save_departure_time(self, train_id: str, time: datetime):
        """Save departure time for train"""
        self.departure_times[train_id] = time
        if train_id in self.arrived_trains:
            train = self.arrived_trains[train_id]
            train.departure_time = time
            train.is_departed = True
        
    def get_violations(self) -> List[ScheduleViolation]:
        """Get all violations"""
        return self.violations
    
    def update_schedule(self, new_schedule: Schedule):
        """Update current schedule"""
        self.current_schedule = new_schedule
        
    def get_advertisements(self) -> List[Advertisement]:
        """Get active advertisements"""
        return [ad for ad in self.advertisements if ad.is_active]
    
    def add_arrived_train(self, train: Train):
        """Add train to arrived trains list"""
        self.arrived_trains[train.train_id] = train
        
    def get_arrived_trains(self) -> List[Train]:
        """Get trains that are currently at the station"""
        return [train for train in self.arrived_trains.values() if not train.is_departed]
    
    def is_train_arrived(self, train_id: str) -> bool:
        """Check if train has arrived"""
        return train_id in self.arrived_trains and not self.arrived_trains[train_id].is_departed
    
    def add_violation(self, violation: ScheduleViolation):
        """Add violation to memory"""
        self.violations.append(violation)
    
    def is_train_departed(self, train_id: str) -> bool:
        """Check if train has departed"""
        train = self.current_trains.get(train_id)
        return train is not None and train.is_departed

class BoardProcessor:
    def __init__(self, memory: BoardMemory, display):
        self.memory = memory
        self.display = display
        self.ad_manager = AdvertisementManager()
        
    def process_timer_tick(self):
        """Process timer tick - update main information"""
        current_time = datetime.now()
        
        # Check for automatic violations
        if self.memory.current_schedule:
            auto_violations = self.memory.current_schedule.find_violations()
            for violation in auto_violations:
                self.memory.add_violation(violation)
        
        display_data = self.format_display_data(
            data=[
                self.memory.current_schedule,
                self._get_next_arriving_train_info(),
                current_time,
                self._get_last_departure_time(),
                self.ad_manager.get_next_ad(),
                self.memory.get_arrived_trains()
            ],
            code="MAIN_UPDATE"
        )
        
        self.display.update_display(display_data)
        
    def process_arrival_signal(self, train: Train):
        """Process arrival signal from sensor"""
        if train.is_arrived:
            return
            
        train.arrival_time = datetime.now()
        train.is_arrived = True
        train.is_departed = False
        self.memory.current_trains[train.train_id] = train
        self.memory.add_arrived_train(train)
        
        self._check_arrival_violation(train, train.arrival_time)
        self.process_timer_tick()
        
    def process_departure_signal(self, train: Train):
        """Process departure signal from sensor"""
        if not train.is_arrived or train.is_departed:
            return
            
        departure_time = datetime.now()
        train.departure_time = departure_time
        train.is_departed = True
        self.memory.save_departure_time(train.train_id, departure_time)
        
        self._check_departure_violation(train, departure_time)
        self.process_timer_tick()
        
    def handle_management_request(self, request: ManagementRequest) -> List[ScheduleViolation]:
        """Handle request from management center"""
        if request.request_type == "GET_VIOLATIONS":
            return self.memory.get_violations()
        elif request.request_type == "GET_SCHEDULE":
            return [self.memory.current_schedule] if self.memory.current_schedule else []
        elif request.request_type == "GET_STATUS":
            return [{
                'arrived_trains': len(self.memory.get_arrived_trains()),
                'violations': len(self.memory.get_violations()),
                'timestamp': datetime.now()
            }]
        return []
        
    def format_display_data(self, data: List[object], code: str) -> DisplayData:
        """Format data for display"""
        return DisplayData(data=data, code=code, timestamp=datetime.now())
    
    def _get_last_departure_time(self) -> Optional[datetime]:
        """Get last departure time"""
        if self.memory.departure_times:
            return max(self.memory.departure_times.values())
        return None
    
    def _get_next_arriving_train_info(self) -> List[str]:
        """Get information about the NEXT arriving train only"""
        next_train = self._find_next_arriving_train()
        
        if next_train:
            train_info, time_diff = next_train
            if time_diff < 0:
                status = f"🚨 ОПОЗДАНИЕ {abs(int(time_diff))} мин."
            elif time_diff <= 1:
                status = "🟢 Прибывает"
            else:
                status = f"🕒 Через {int(time_diff)} мин."
                
            return [f"{train_info.train_id} -> {train_info.final_station.name} ({status})"]
        
        return ["Нет прибывающих поездов"]
    
    def _find_next_arriving_train(self) -> Optional[tuple]:
        """Find the next arriving train"""
        if not self.memory.current_schedule:
            return None
        
        now = datetime.now()
        next_train = None
        min_time_diff = float('inf')
        
        for item in self.memory.current_schedule.items:
            # Skip departed trains and already arrived trains
            if (self.memory.is_train_departed(item.train_id) or 
                self.memory.is_train_arrived(item.train_id)):
                continue
                
            time_diff = (item.planned_arrival - now).total_seconds() / 60
            
            # Find the closest train (even if it's late)
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                next_train = item
        
        return (next_train, min_time_diff) if next_train else None
    
    def _check_arrival_violation(self, train: Train, actual_time: datetime):
        """Check for arrival violation"""
        if self.memory.current_schedule:
            item = self.memory.current_schedule.get_train_schedule(train.train_id)
            if item and not item.arrival_violation_checked:
                delay = (actual_time - item.planned_arrival).total_seconds() / 60
                if delay > 1:
                    violation = ScheduleViolation(
                        violation_id=f"viol_arr_{len(self.memory.violations)+1}",
                        train_id=train.train_id,
                        station_id=train.current_station,
                        planned_time=item.planned_arrival,
                        actual_time=actual_time,
                        delay_minutes=int(delay),
                        violation_type=ViolationType.ARRIVAL_DELAY
                    )
                    self.memory.add_violation(violation)
                    item.arrival_violation_checked = True
    
    def _check_departure_violation(self, train: Train, actual_time: datetime):
        """Check for departure violation"""
        if self.memory.current_schedule:
            item = self.memory.current_schedule.get_train_schedule(train.train_id)
            if item and not item.departure_violation_checked:
                delay = (actual_time - item.planned_departure).total_seconds() / 60
                if delay > 1:
                    violation = ScheduleViolation(
                        violation_id=f"viol_dep_{len(self.memory.violations)+1}",
                        train_id=train.train_id,
                        station_id=train.current_station,
                        planned_time=item.planned_departure,
                        actual_time=actual_time,
                        delay_minutes=int(delay),
                        violation_type=ViolationType.DEPARTURE_DELAY
                    )
                    self.memory.add_violation(violation)
                    item.departure_violation_checked = True

class CurrentDisplay(QWidget):
    def __init__(self):
        super().__init__()
        self.current_time: str = ""
        self.last_departure_time: str = ""
        self.arriving_train_final: str = ""
        self.current_ad: Optional[Advertisement] = None
        self.current_schedule = None
        self.memory = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        title = QLabel("ИНФОРМАЦИОННОЕ ТАБЛО МЕТРО")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #2E86AB; color: white; padding: 10px;")
        layout.addWidget(title)
        
        # Current time
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("background-color: #A23B72; color: white; padding: 5px;")
        layout.addWidget(self.time_label)
        
        # Last departure
        self.departure_label = QLabel()
        self.departure_label.setFont(QFont("Arial", 12))
        self.departure_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        layout.addWidget(self.departure_label)
        
        # Next arriving train - ТОЛЬКО ОДИН ПОЕЗД
        self.arrival_label = QLabel()
        self.arrival_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.arrival_label.setStyleSheet("padding: 5px; border: 2px solid #4CAF50; background-color: #F0F8FF;")
        layout.addWidget(QLabel("Следующий прибывающий поезд:"))
        layout.addWidget(self.arrival_label)
        
        # Trains at station
        self.arrived_label = QLabel()
        self.arrived_label.setFont(QFont("Arial", 12))
        self.arrived_label.setStyleSheet("padding: 5px; border: 1px solid #ccc; background-color: #F0FFF0;")
        layout.addWidget(QLabel("Поезда на станции:"))
        layout.addWidget(self.arrived_label)
        
        # Advertisement
        self.ad_label = QLabel()
        self.ad_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.ad_label.setStyleSheet("color: #FF6B6B; background-color: #FFFACD; padding: 8px; border: 2px dashed #FFD700;")
        self.ad_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.ad_label)
        
        # Schedule
        self.schedule_text = QTextEdit()
        self.schedule_text.setMaximumHeight(180)
        self.schedule_text.setReadOnly(True)
        self.schedule_text.setStyleSheet("font-family: 'Courier New'; font-size: 10pt;")
        layout.addWidget(QLabel("Расписание:"))
        layout.addWidget(self.schedule_text)
        
        self.setLayout(layout)
        
    def update_display(self, display_data: DisplayData):
        """Update display with new data"""
        data = display_data.data
        code = display_data.code
        
        if code == "MAIN_UPDATE":
            self._update_main_display(data)
        
    def _update_main_display(self, data: List[object]):
        schedule, arriving_trains, current_time, last_departure, current_ad, arrived_trains = data
        
        # Update time
        self.time_label.setText(f"🕒 Текущее время: {current_time.strftime('%H:%M:%S')}")
        
        # Last departure
        if last_departure:
            time_diff = (datetime.now() - last_departure).seconds
            minutes = time_diff // 60
            seconds = time_diff % 60
            self.departure_label.setText(
                f"🚆 Последний поезд отправился: {last_departure.strftime('%H:%M:%S')} ({minutes} мин. {seconds} сек. назад)"
            )
        else:
            self.departure_label.setText("🚆 Последний поезд: информация отсутствует")
        
        # Next arriving train - ТОЛЬКО ОДИН
        if arriving_trains and arriving_trains[0] != "Нет прибывающих поездов":
            self.arrival_label.setText(arriving_trains[0])
        else:
            self.arrival_label.setText("Нет прибывающих поездов")
        
        # Trains at station
        if arrived_trains:
            arrived_text = "\n".join([f"🚊 {train.train_id} -> {train.final_station} (прибыл: {train.arrival_time.strftime('%H:%M')})" 
                                    for train in arrived_trains])
            self.arrived_label.setText(arrived_text)
        else:
            self.arrived_label.setText("На станции нет поездов")
        
        # Advertisement
        if current_ad:
            self.ad_label.setText(f"🎯 {current_ad.content} 🎯")
        else:
            self.ad_label.setText("")
        
        # Schedule
        if schedule:
            self._update_schedule_display(schedule, arrived_trains)
    
    def _update_schedule_display(self, schedule, arrived_trains):
        schedule_text = ""
        now = datetime.now()
        
        for item in schedule.items[:8]:
            time_diff = (item.planned_arrival - now).total_seconds() / 60
            
            # Check train status
            is_on_station = any(train.train_id == item.train_id for train in arrived_trains)
            is_departed = self.memory and self.memory.is_train_departed(item.train_id)
            
            # Status determination
            if is_departed:
                status = "🚆 Отправился"
            elif is_on_station:
                status = "✅ На станции"
            elif time_diff < -2:
                status = f"🚨 ОПОЗДАНИЕ {int(abs(time_diff))} мин."
            elif time_diff < 0:
                status = "🟢 Прибывает"
            else:
                status = f"🕒 Через {int(time_diff)} мин."
            
            schedule_text += f"{item.train_id:6} -> {item.final_station.name:12} {item.planned_arrival.strftime('%H:%M'):5} {status}\n"
        
        self.schedule_text.setText(schedule_text)
    
    def show_default_message(self):
        """Show default message when no data"""
        self.time_label.setText("🕒 Текущее время: --:--:--")
        self.departure_label.setText("🚆 Последний поезд: информация отсутствует")
        self.arrival_label.setText("Нет прибывающих поездов")
        self.arrived_label.setText("На станции нет поездов")
        self.ad_label.setText("")
        self.schedule_text.setText("Расписание не загружено")

class ManagementCenter:
    def __init__(self, center_id: str):
        self.center_id = center_id
        self.boards: List['InformationBoard'] = []
        self.main_schedule: Optional[Schedule] = None
        self.ad_manager = AdvertisementManager()
        
    def send_schedule_update(self, board_id: str, schedule: Schedule):
        """Send schedule update to specific board"""
        self.main_schedule = schedule
        for board in self.boards:
            if board.board_id == board_id:
                board.memory.update_schedule(schedule)
                break
        
    def send_advertisement_update(self, board_id: str, ads: List[Advertisement]):
        """Send advertisement update to specific board"""
        self.ad_manager.update_ads(ads)
        for board in self.boards:
            if board.board_id == board_id:
                board.memory.advertisements = ads
                board.processor.ad_manager.update_ads(ads)
                break
        
    def request_violations(self, board_id: str) -> List[ScheduleViolation]:
        """Request violations from specific board"""
        for board in self.boards:
            if board.board_id == board_id:
                request = ManagementRequest(
                    request_id=f"req_{datetime.now().strftime('%H%M%S')}",
                    request_type="GET_VIOLATIONS",
                    board_id=board_id
                )
                return board.processor.handle_management_request(request)
        return []
    
    def sync_time(self):
        """Sync time across all boards"""
        sync_time = datetime.now()
        print(f"Management Center: Time synced to {sync_time}")
        return sync_time

class InformationBoard(QMainWindow):
    def __init__(self, board_id: str, station: str):
        super().__init__()
        self.board_id = board_id
        self.station = station
        self.memory = BoardMemory()
        self.display = CurrentDisplay()
        self.processor = BoardProcessor(self.memory, self.display)
        self.timer = Timer(3)
        
        # Connect memory to display for data access
        self.display.memory = self.memory
        
        self.arrival_sensor = ArrivalSensor("arrival_1", station)
        self.departure_sensor = DepartureSensor("departure_1", station)
        
        self.management_center = ManagementCenter("main_center")
        self.management_center.boards.append(self)
        
        self.init_ui()
        self.setup_initial_data()
        self.timer.start(self.processor.process_timer_tick)
        
    def init_ui(self):
        self.setWindowTitle(f"Информационное табло - {self.station} (ID: {self.board_id})")
        self.setGeometry(100, 100, 800, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Main display
        layout.addWidget(self.display)
        
        # Control panel
        control_group = QGroupBox("Управление симуляцией")
        control_layout = QVBoxLayout()
        
        # Train selection and buttons
        train_layout = QHBoxLayout()
        train_layout.addWidget(QLabel("Поезд:"))
        self.train_combo = QComboBox()
        self.train_combo.currentTextChanged.connect(self.on_train_selected)
        train_layout.addWidget(self.train_combo)
        
        self.arrival_btn = QPushButton("🚊 Прибытие")
        self.arrival_btn.clicked.connect(self.simulate_arrival)
        self.arrival_btn.setEnabled(False)
        train_layout.addWidget(self.arrival_btn)
        
        self.departure_btn = QPushButton("🚆 Отправление")
        self.departure_btn.clicked.connect(self.simulate_departure)
        self.departure_btn.setEnabled(False)
        train_layout.addWidget(self.departure_btn)
        
        control_layout.addLayout(train_layout)
        
        # Management center controls
        mgmt_layout = QHBoxLayout()
        self.sync_time_btn = QPushButton("🕒 Синхронизировать время")
        self.sync_time_btn.clicked.connect(self.sync_time)
        mgmt_layout.addWidget(self.sync_time_btn)
        
        self.get_violations_btn = QPushButton("📊 Запросить нарушения")
        self.get_violations_btn.clicked.connect(self.request_violations)
        mgmt_layout.addWidget(self.get_violations_btn)
        
        control_layout.addLayout(mgmt_layout)
        
        # Train status
        self.train_status_label = QLabel("Выберите поезд")
        self.train_status_label.setStyleSheet("padding: 5px; background-color: #F5F5F5;")
        control_layout.addWidget(self.train_status_label)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Violations
        violations_group = QGroupBox("Нарушения расписания")
        violations_layout = QVBoxLayout()
        self.violations_text = QTextEdit()
        self.violations_text.setMaximumHeight(120)
        self.violations_text.setReadOnly(True)
        self.violations_text.setStyleSheet("color: red; font-weight: bold; background-color: #FFF0F0;")
        violations_layout.addWidget(self.violations_text)
        violations_group.setLayout(violations_layout)
        layout.addWidget(violations_group)
        
        central_widget.setLayout(layout)
        
    def update_general_data(self, data: List[object], code: str):
        """Update board with general data"""
        display_data = DisplayData(data=data, code=code, timestamp=datetime.now())
        self.display.update_display(display_data)
        
    def display_information(self):
        """Display current information"""
        self.processor.process_timer_tick()
        
    def receive_sensor_signal(self, sensor_type: str, train_data: Train):
        """Receive signal from sensor"""
        if sensor_type == SensorType.ARRIVAL.value:
            self.processor.process_arrival_signal(train_data)
        elif sensor_type == SensorType.DEPARTURE.value:
            self.processor.process_departure_signal(train_data)
        
    def on_train_selected(self, train_id):
        """Update button states when train is selected"""
        if not train_id:
            return
            
        is_arrived = self.memory.is_train_arrived(train_id)
        is_departed = self.memory.is_train_departed(train_id)
        
        if is_departed:
            status = "🚆 Уехал"
            self.arrival_btn.setEnabled(False)
            self.departure_btn.setEnabled(False)
        elif is_arrived:
            status = "🚊 На станции"
            self.arrival_btn.setEnabled(False)
            self.departure_btn.setEnabled(True)
        else:
            status = "🕒 В пути"
            self.arrival_btn.setEnabled(True)
            self.departure_btn.setEnabled(False)
            
        self.train_status_label.setText(f"Статус {train_id}: {status}")
        
    def setup_initial_data(self):
        """Initialize with sample data"""
        # Create stations
        stations = [
            Station("st1", "Киевская", "центр"),
            Station("st2", "Парк Победы", "запад"),
            Station("st3", "Щёлковская", "восток"),
            Station("st4", "Речной вокзал", "север"),
            Station("st5", "Красногвардейская", "юг"),
        ]
        
        # Create schedule
        schedule = Schedule("sched_1")
        now = datetime.now()
        
        # Add 8 trains to schedule
        for i in range(8):
            train_id = f"train{i+1}"
            arrival_time = now + timedelta(minutes=1 + i*7)
            departure_time = arrival_time + timedelta(minutes=3)
            
            schedule_item = ScheduleItem(
                train_id=train_id,
                route_id=f"route{i+1}",
                final_station=random.choice(stations),
                planned_arrival=arrival_time,
                planned_departure=departure_time
            )
            schedule.items.append(schedule_item)
        
        self.memory.update_schedule(schedule)
        self.management_center.send_schedule_update(self.board_id, schedule)
        
        # Create advertisements
        ads = []
        ad_messages = [
            "Купите проездной онлайн - выгодно!",
            "Новый маршрут до аэропорта",
            "Бесплатный Wi-Fi на всех станциях",
            "Скидка 20% в кафе у эскалаторов",
            "Мобильное приложение метро - удобно!",
        ]
        
        for i in range(5):
            ad = Advertisement(
                ad_id=f"ad{i+1}",
                content=ad_messages[i],
                display_order=i+1,
                start_date=now,
                end_date=now + timedelta(days=30)
            )
            ads.append(ad)
        
        self.memory.advertisements = ads
        self.management_center.send_advertisement_update(self.board_id, ads)
        
        # Populate train combo
        self.train_combo.addItems([f"train{i+1}" for i in range(8)])
        
    def simulate_arrival(self):
        """Simulate train arrival"""
        train_id = self.train_combo.currentText()
        if self.memory.is_train_arrived(train_id):
            return
            
        # Find train info from schedule
        final_station = self.memory.get_train_final_station(train_id) or "Неизвестно"
        
        train = Train(
            train_id=train_id,
            train_type=TrainType.PUBLIC,
            current_station=self.station,
            final_station=final_station
        )
        
        # Use sensor to detect arrival
        self.arrival_sensor.detect_arrival(train)
        self.receive_sensor_signal(SensorType.ARRIVAL.value, train)
        self.on_train_selected(train_id)
        self.update_violations_display()
        
    def simulate_departure(self):
        """Simulate train departure"""
        train_id = self.train_combo.currentText()
        if not self.memory.is_train_arrived(train_id):
            return
            
        train = self.memory.arrived_trains.get(train_id)
        if train and not train.is_departed:
            # Use sensor to detect departure
            self.departure_sensor.detect_departure(train)
            self.receive_sensor_signal(SensorType.DEPARTURE.value, train)
            self.on_train_selected(train_id)
            self.update_violations_display()
    
    def sync_time(self):
        """Sync time with management center"""
        sync_time = self.management_center.sync_time()
        print(f"Board {self.board_id}: Time synced to {sync_time}")
    
    def request_violations(self):
        """Request violations from management center"""
        violations = self.management_center.request_violations(self.board_id)
        self.update_violations_display()
        print(f"Board {self.board_id}: Received {len(violations)} violations")
    
    def update_violations_display(self):
        """Update violations display"""
        violations = self.memory.get_violations()
        violations_text = ""
        
        for violation in violations[-8:]:
            time_str = violation.actual_time.strftime('%H:%M')
            type_str = "прибытие" if violation.violation_type == ViolationType.ARRIVAL_DELAY else "отправление"
            violations_text += f"🚨 {violation.train_id}: опоздание {violation.delay_minutes} мин. ({type_str} в {time_str})\n"
        
        self.violations_text.setText(violations_text if violations_text else "Нарушений нет")

def main():
    app = QApplication(sys.argv)
    
    # Create information board for specific station
    board = InformationBoard("board_1", "Площадь Революции")
    board.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()