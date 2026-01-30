from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
import database
from datetime import datetime

class DashboardScreen(Screen):
    def on_pre_enter(self):
        self.cargar_proximos_turnos()

    def cargar_proximos_turnos(self):
        # Limpiamos la lista
        self.ids.lista_proximos_turnos.clear_widgets()
        
        conn = database.conectar()
        cursor = conn.cursor()
        
        # Obtenemos TODOS los turnos (SQLite no ordena fechas dd/mm/yyyy bien nativamente)
        cursor.execute("SELECT cliente_nombre, servicio, fecha, hora FROM turnos")
        todos = cursor.fetchall()
        conn.close()

        if not todos:
            return # Lista vacía

        # Convertimos a objetos de fecha real para poder ordenar y filtrar
        turnos_obj = []
        hoy = datetime.now().date()
        
        for t in todos:
            try:
                fecha_obj = datetime.strptime(t[2], "%d/%m/%Y").date()
                # Solo queremos turnos de HOY en adelante
                if fecha_obj >= hoy:
                    turnos_obj.append({
                        "cliente": t[0],
                        "servicio": t[1],
                        "fecha_str": t[2],
                        "hora": t[3],
                        "fecha_dt": fecha_obj
                    })
            except:
                pass # Ignoramos fechas mal formadas

        # Ordenamos por fecha (primero lo más cercano)
        turnos_ordenados = sorted(turnos_obj, key=lambda x: (x['fecha_dt'], x['hora']))

        # Tomamos solo los primeros 3 para no saturar el inicio
        proximos = turnos_ordenados[:3]

        # Los agregamos a la lista visual
        for p in proximos:
            item = TwoLineAvatarIconListItem(
                text=f"{p['fecha_str']} - {p['hora']}",
                secondary_text=f"{p['servicio']} con {p['cliente']}",
                on_release=lambda x: self.ir_a_agenda()
            )
            item.add_widget(IconLeftWidget(icon="calendar-arrow-right"))
            self.ids.lista_proximos_turnos.add_widget(item)

    def ir_a_agenda(self):
        MDApp.get_running_app().root.current = 'agenda'