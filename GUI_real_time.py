import sys
import os
from PyQt5.QtCore import Qt, QTimer,QPoint,QSize
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QPolygon,QPixmap,QTransform,QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,QPushButton, QComboBox, QGridLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore
import folium
import math
import random
from firebase import firebase

firebaseConfig = {
  "apiKey": "AIzaSyDaHsbdevx4fH7yUuaJ43N1J8vAfeF_Q1o",
  "authDomain": "gpstracker-85f4d.firebaseapp.com",
  "databaseURL": "https://gpstracker-85f4d-default-rtdb.firebaseio.com",
  "projectId": "gpstracker-85f4d",
  "storageBucket": "gpstracker-85f4d.appspot.com",
  "messagingSenderId": "958754309164",
  "appId": "1:958754309164:web:030d6ba5129c1ad317bd89",
  "measurementId": "G-YJ9N1VQQYX"
}

firebase = firebase.FirebaseApplication(firebaseConfig['databaseURL'], None)

class CompassWidget(QWidget):
    def __init__(self, label_text):
        super().__init__()
        self.label = QLabel(label_text)
        self.label.setStyleSheet("QLabel { font-weight: bold; color: #4CAF50; }")
        self.angle = 0.0
        self.angle_display = QLabel("0.0")
        self.angle_layout = QHBoxLayout()
        self.angle_layout.addWidget(self.angle_display)
        self.setMinimumSize(250, 250)
        self.setMaximumSize(250, 250)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.label)
        main_layout.addLayout(self.angle_layout)

        self.graphics_view = QGraphicsView(self)
        self.graphics_view.setMinimumSize(250, 250)
        self.graphics_view.setMaximumSize(250, 250)
        main_layout.addWidget(self.graphics_view)

        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)

        self.compass_item = QGraphicsPixmapItem()
        compass_pixmap = QPixmap("compass1.png")
        self.compass_item.setPixmap(compass_pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
        self.scene.addItem(self.compass_item)

        self.arrow_item = QGraphicsPixmapItem()
        arrow_pixmap = QPixmap("arrow.png")
        self.arrow_item.setPixmap(arrow_pixmap.scaled(150,100, Qt.AspectRatioMode.KeepAspectRatio))
        self.arrow_item.setOffset(76 ,48)
        self.scene.addItem(self.arrow_item)

    def set_angle(self, angle):
        self.angle = angle
        self.angle_display.setText(str(angle))
        self.update_arrow_rotation()

    def update_arrow_rotation(self):
        transform = QTransform()
        transform.translate(125, 125)
        transform.rotate(self.angle)
        transform.translate(-125, -125)
        self.arrow_item.setTransform(transform)

    def sizeHint(self):
        return QtCore.QSize(250, 250)

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mission Planner GUI")
        self.setGeometry(200, 100, 1500, 800)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        left_layout = QGridLayout()
        right_layout = QVBoxLayout()

        lat_label = QLabel("Latitude:")
        lon_label = QLabel("Longitude:")
        self.lat_edit = QLineEdit()
        self.lon_edit = QLineEdit()
        self.speed_label = QLabel("Speed (in m/s):")
        self.speed_edit = QLineEdit()
        self.distance_label = QLabel("Distance/radius/length (in mts):")
        self.distance_edit = QLineEdit()
        self.heading_label = QLabel("Heading Angle (in degrees):")
        self.heading_edit = QLineEdit()
        trajectory_label = QLabel("Choose Trajectory:")
        self.trajectory_combo = QComboBox()
        self.trajectory_combo.addItem("Straight Line")
        self.trajectory_combo.addItem("Circular Path")
        self.trajectory_combo.addItem("S Shape")
        self.trajectory_combo.currentIndexChanged.connect(self.show_details)
        generate_button = QPushButton("Generate Waypoints")
        generate_button.clicked.connect(self.generate_waypoints)
        start_button = QPushButton("Start Simulation")
        start_button.clicked.connect(self.start_simulation)
        real_button=QPushButton("Real time tracking")
        real_button.clicked.connect(self.start_real_time_tracking)
        self.map_view = QWebEngineView()
        
        self.speed_label_display1 = QLabel()
        self.speed_label_display2 = QLabel()
        self.lat_label_display1 = QLabel()
        self.lon_label_display1 = QLabel()
        self.heading_label_display1 = QLabel()
        self.lat_label_display2 = QLabel()
        self.lon_label_display2 = QLabel()
        self.heading_label_display2 = QLabel()
        self.compass_yaw = CompassWidget("Yaw")
        self.compass_pitch = CompassWidget("Pitch")
        self.compass_roll = CompassWidget("Roll")

        left_layout.addWidget(trajectory_label, 0, 0, 1, 2)
        left_layout.addWidget(self.trajectory_combo, 1, 0, 1, 2)
        left_layout.addWidget(lat_label, 2, 0)
        left_layout.addWidget(self.lat_edit, 3, 0)
        left_layout.addWidget(lon_label, 2, 1)
        left_layout.addWidget(self.lon_edit, 3, 1)
        left_layout.addWidget(self.speed_label, 4, 0)
        left_layout.addWidget(self.speed_edit, 5, 0)
        left_layout.addWidget(self.distance_label, 6, 0)
        left_layout.addWidget(self.distance_edit, 6, 1)
        left_layout.addWidget(self.heading_label, 4, 1)
        left_layout.addWidget(self.heading_edit, 5, 1)
        left_layout.addWidget(generate_button, 7, 0, 1, 2)
        left_layout.addWidget(self.speed_label_display1, 9, 0, 1, 2)
        left_layout.addWidget(self.speed_label_display2, 9, 1, 1, 2)
        left_layout.addWidget(self.lat_label_display1, 10, 0, 1, 2)
        left_layout.addWidget(self.lat_label_display2, 10, 1, 1, 2)
        left_layout.addWidget(self.lon_label_display1, 11, 0, 1, 2)
        left_layout.addWidget(self.lon_label_display2, 11, 1, 1, 2)
        left_layout.addWidget(self.heading_label_display1, 12, 0, 1, 2)
        left_layout.addWidget(self.heading_label_display2, 12, 1, 1, 2)
        left_layout.addWidget(self.compass_yaw, 13, 1, 1, 2)
        left_layout.addWidget(self.compass_pitch, 14, 0, 1, 2)
        left_layout.addWidget(self.compass_roll, 14,1, 1, 2)
        left_layout.addWidget(start_button, 8,0,1,1)
        left_layout.addWidget(real_button, 8,1,1,1)
        right_layout.addWidget(self.map_view)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 2)
        self.timer = QTimer()
        self.lat_label_display1.setText("\t\tLatitude : ")
        self.lat_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
        self.lat_label_display2.setText("<font color='blue'>{}</font>")
        self.lon_label_display1.setText("\t\tLongitude : ")
        self.lon_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
        self.lon_label_display2.setText("<font color='blue'>{}</font>")
        self.timer.timeout.connect(self.update_display_values)
        self.timer.start(2000)

        self.timer2 = QtCore.QTimer()
        self.timer2.timeout.connect(self.mark_gps_locations_on_map)       
        self.previous_location = None
        self.m = None

        self.waypoints = []
        self.current_waypoint_index = 0
        self.map = None
        self.generate_map()

    def update_display_values(self):
        speed = self.speed_edit.text()
        heading = self.heading_edit.text()
        self.speed_label_display1.setText("\t\tSpeed : ")
        self.speed_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
        self.speed_label_display2.setText("<font color='blue'>{} m/s</font> ".format(speed))
        self.heading_label_display1.setText("\t\tHeading Angle : ")
        self.heading_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
        self.heading_label_display2.setText("<font color='blue'>{}°</font>".format(heading))

    def show_details(self, index):
        trajectory = self.trajectory_combo.currentText()
        if trajectory == "Straight Line":
            self.speed_edit.setEnabled(True)
            self.distance_edit.setEnabled(True)
            self.heading_edit.setEnabled(True)
            self.distance_label.setVisible(True)
            self.heading_label.setVisible(True)
            self.speed_label.setVisible(True)
            self.heading_label_display1.setVisible(True)
            self.heading_label_display2.setVisible(True)
        elif trajectory == "Circular Path":
            self.speed_edit.setEnabled(False)
            self.distance_edit.setEnabled(True)
            self.heading_edit.setEnabled(False)
            self.distance_label.setVisible(True)
            self.heading_label.setVisible(False)
            self.speed_label.setVisible(False)
            self.heading_label_display1.setVisible(False)
            self.heading_label_display2.setVisible(False)
        elif trajectory == "S Shape":
            self.speed_edit.setEnabled(True)
            self.distance_edit.setEnabled(True)
            self.heading_edit.setEnabled(True)
            self.distance_label.setVisible(True)
            self.heading_label.setVisible(True)
            self.speed_label.setVisible(True)
            self.heading_label_display1.setVisible(True)
            self.heading_label_display2.setVisible(True)

    def generate_waypoints(self):
        trajectory = self.trajectory_combo.currentText()
        if trajectory == "Straight Line":
            lat = float(self.lat_edit.text())
            lon = float(self.lon_edit.text())
            speed = float(self.speed_edit.text())
            distance = float(self.distance_edit.text())
            heading = float(self.heading_edit.text())
            if (distance % speed) == 0:
                num_waypoints = int(distance / speed) + 1
            else:
                num_waypoints = int(distance / speed) + 2
            angular_distance = speed / 6371000
            heading_rad = math.radians(heading)
            current_lat = lat
            current_lon = lon
            self.waypoints = []
            for _ in range(num_waypoints):
                self.waypoints.append((current_lat, current_lon))
                current_lat += math.degrees(angular_distance) * math.cos(heading_rad)
                current_lon += math.degrees(angular_distance) * math.sin(heading_rad)
            self.update_map()

        elif trajectory == "Circular Path":
            lat = float(self.lat_edit.text())
            lon = float(self.lon_edit.text())
            distance = float(self.distance_edit.text())
            num_waypoints = 16

            center_lat = lat + math.degrees(distance / 6371000)
            center_lon = lon
            self.waypoints = []
            for i in range(num_waypoints):
                angle = math.radians(float(i * 360) / num_waypoints)
                dx = distance * math.cos(angle)
                dy = distance * math.sin(angle)
                waypoint_lat = center_lat + math.degrees(dy / 6371000)
                waypoint_lon = center_lon + math.degrees(dx / (6371000 * math.cos(math.radians(center_lat))))
                self.waypoints.append((waypoint_lat, waypoint_lon))
            self.update_map2()

        elif trajectory == "S Shape":
            lat = float(self.lat_edit.text())
            lon = float(self.lon_edit.text())
            distance_between_waypoints = float(self.distance_edit.text())
            self.waypoints = []
            current_lat = lat
            current_lon = lon
            self.waypoints.append((current_lat, current_lon))
            current_lon += math.degrees(distance_between_waypoints / 6371000)
            self.waypoints.append((current_lat, current_lon))
            current_lat += math.degrees(distance_between_waypoints / (6371000 * math.cos(math.radians(current_lat))))
            self.waypoints.append((current_lat, current_lon))
            current_lon -= math.degrees(distance_between_waypoints / 6371000)
            self.waypoints.append((current_lat, current_lon))
            current_lat += math.degrees(distance_between_waypoints / (6371000 * math.cos(math.radians(current_lat))))
            self.waypoints.append((current_lat, current_lon))
            current_lon += math.degrees(distance_between_waypoints / 6371000)
            self.waypoints.append((current_lat, current_lon))
            self.update_map3()

    def generate_map(self):
        m = folium.Map(location=[20, 78], zoom_start=4)
        map_file = "map.html"
        m.save(map_file)
        self.map_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath(map_file)))

    def update_map(self):
        self.map_view.page().runJavaScript("map.remove();")
        initial_lat = float(self.lat_edit.text())
        initial_lon = float(self.lon_edit.text())
        self.map = folium.Map(location=[initial_lat, initial_lon], zoom_start=18)
        total_waypoints = len(self.waypoints)
        for i, waypoint in enumerate(self.waypoints):
            lat, lon = waypoint
            if i == 0 or i == total_waypoints - 1:
                folium.Marker(location=[lat, lon], popup=f"Waypoint {i + 1}\nLatitude: {lat}\nLongitude: {lon}",
                              icon=folium.Icon(color="green")).add_to(self.map)
            else:
                folium.Marker(location=[lat, lon], popup=f"Waypoint {i + 1}\nLatitude: {lat}\nLongitude: {lon}").add_to(self.map)
        folium.PolyLine(locations=self.waypoints, color="red").add_to(self.map)
        
        map_file = "map.html"
        self.map.save(map_file)
        self.map_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath(map_file)))


    def update_map2(self):
        self.map_view.page().runJavaScript("map.remove();")
        initial_lat = float(self.lat_edit.text())
        initial_lon = float(self.lon_edit.text())
        self.map = folium.Map(location=[initial_lat, initial_lon], zoom_start=18)
        total_waypoints = len(self.waypoints)
        initial_lat = float(self.lat_edit.text())
        initial_lon = float(self.lon_edit.text())

        for i, waypoint in enumerate(self.waypoints):
            lat, lon = waypoint
            if lat == initial_lat and lon == initial_lon:
                folium.Marker(location=[lat, lon], popup=f"Waypoint {i + 1}\nLatitude: {lat}\nLongitude: {lon}",
                              icon=folium.Icon(color="green")).add_to(self.map)
            else:
                folium.Marker(location=[lat, lon], popup=f"Waypoint {i + 1}\nLatitude: {lat}\nLongitude: {lon}").add_to(self.map)

        folium.PolyLine(locations=self.waypoints, color="red").add_to(self.map)
        map_file = "map.html"
        self.map.save(map_file)
        self.map_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath(map_file)))

    def update_map3(self):
        self.map_view.page().runJavaScript("map.remove();")
        initial_lat = float(self.lat_edit.text())
        initial_lon = float(self.lon_edit.text())
        self.map = folium.Map(location=[initial_lat, initial_lon], zoom_start=18)
        total_waypoints = len(self.waypoints)
        initial_lat = float(self.lat_edit.text())
        initial_lon = float(self.lon_edit.text())

        for i, waypoint in enumerate(self.waypoints):
            lat, lon = waypoint
            if lat == initial_lat and lon == initial_lon:
                folium.Marker(location=[lat, lon], popup=f"Waypoint {i + 1}\nLatitude: {lat}\nLongitude: {lon}",
                              icon=folium.Icon(color="green")).add_to(self.map)
            else:
                angle = math.radians(float(self.heading_edit.text()))
                dx = math.cos(angle) * (lon - initial_lon) - math.sin(angle) * (lat - initial_lat)
                dy = math.sin(angle) * (lon - initial_lon) + math.cos(angle) * (lat - initial_lat)
                new_lat = initial_lat + dy
                new_lon = initial_lon + dx
                self.waypoints[i] = (new_lat, new_lon)
                folium.Marker(location=[new_lat, new_lon],
                              popup=f"Waypoint {i + 1}\nLatitude: {new_lat}\nLongitude: {new_lon}").add_to(self.map)

        folium.PolyLine(locations=self.waypoints, color="red").add_to(self.map)
        map_file = "map.html"
        self.map.save(map_file)
        self.map_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath(map_file)))

    def start_simulation(self):
        self.current_waypoint_index = 0
        self.move_to_next_waypoint()

    def move_to_next_waypoint(self):
        if self.current_waypoint_index < len(self.waypoints):
            lat, lon = self.waypoints[self.current_waypoint_index]
            print(f"Moving to waypoint {self.current_waypoint_index + 1} - Latitude: {lat}, Longitude: {lon}")
            self.lat_label_display1.setText("\t\tCurrent Latitude:  ")
            self.lat_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
            self.lat_label_display2.setText(f"<font color='blue'>{lat}</font>")
            self.lon_label_display1.setText("\t\tCurrent Longitude:  ")
            self.lon_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
            self.lon_label_display2.setText(f"<font color='blue'>{lon}</font>")
            delay = 2000
            icon = folium.CustomIcon(icon_image="rover.png", icon_size=(30, 30))
            m = folium.Map(location=[lat, lon], zoom_start=18)

            for i, waypoint in enumerate(self.waypoints):
                wpt_lat, wpt_lon = waypoint
                if i == self.current_waypoint_index:
                    folium.Marker(location=[wpt_lat, wpt_lon],
                                popup=f"Current Waypoint - Latitude: {wpt_lat}, Longitude: {wpt_lon}",
                                icon=icon).add_to(m)
                else:
                    folium.Marker(location=[wpt_lat, wpt_lon],
                                popup=f"Waypoint {i + 1} - Latitude: {wpt_lat}, Longitude: {wpt_lon}",
                                icon=folium.Icon(icon="cloud")).add_to(m)

            m.save("map.html")
            self.map_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath("map.html")))
            self.current_waypoint_index += 1
            QtCore.QTimer.singleShot(delay, self.move_to_next_waypoint)
            self.timer.timeout.connect(self.update_compass_values)
        else:
            self.timer.stop()
            print("Simulation finished")

    def start_real_time_tracking(self):
        try:
            self.timer2.start(5000)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def mark_gps_locations_on_map(self):
        initial_lat = float(self.lat_edit.text())
        initial_lon = float(self.lon_edit.text())
        gps_data = firebase.get('/', 'data')
        print("gps_data type:", type(gps_data))
        print("gps_data:", gps_data)

        if isinstance(gps_data, dict):
            if self.m is None:
                self.m = folium.Map(location=[initial_lat, initial_lon], zoom_start=18)

            lat = None
            lon = None

            for key, value in gps_data.items():
                if key == 'LAT':
                    lat = value
                elif key == 'LNG':
                    lon = value

            if lat is not None and lon is not None:
                folium.Marker(location=[lat, lon],
                              popup=f"Latitude: {lat}, Longitude: {lon}",
                              icon=folium.Icon(icon="cloud")).add_to(self.m)

                if self.previous_location is not None:
                    folium.PolyLine([self.previous_location, (lat, lon)],
                                    color="blue",
                                    weight=2.5,
                                    opacity=1).add_to(self.m)

                self.previous_location = (lat, lon)

                self.m.save("map.html")
                self.map_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath("map.html")))
                self.lat_label_display1.setText("\t\tCurrent Latitude:  ")
                self.lat_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
                self.lat_label_display2.setText(f"<font color='blue'>{lat}</font>")
                self.lon_label_display1.setText("\t\tCurrent Longitude:  ")
                self.lon_label_display2.setStyleSheet("border: 2px solid black; padding: 2px;")
                self.lon_label_display2.setText(f"<font color='blue'>{lon}</font>")
                self.timer2.timeout.connect(self.update_compass_values)
        else:
            print("No GPS data available")
            self.timer2.stop()
    
    def update_compass_values(self):
        yaw_angle = int(random.uniform(0.0, 360.0))
        pitch_angle = int(random.uniform(-90.0, 90.0))
        roll_angle = int(random.uniform(-180.0, 180.0))
        self.compass_yaw.set_angle(yaw_angle)
        self.compass_pitch.set_angle(pitch_angle)
        self.compass_roll.set_angle(roll_angle)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QPushButton { background-color: #4CAF50 !important; color: black; }"
                      "QPushButton:hover { background-color: #45A049 !important; }"
                      "QLabel { color: #FF5733;font-weight: bold;}"
                      "QLineEdit { background-color: #F0F0F0; color: blue;font-weight: bold;}"
                      "QComboBox { background-color: #F0F0F0;color: blue; }"
                      "QWidget { background-color:  #D3D3D3; }"
                      "QGraphicsView { background-color: #303030; }")

    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
