from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
import database
import collections

# Diseño visual incrustado
KV_REPORTES = """
<ReportesScreen>:
    name: 'reportes'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.95, 0.95, 0.97, 1
        
        MDTopAppBar:
            title: "Estadísticas"
            elevation: 0
            left_action_items: [["arrow-left", lambda x: app.ir_al_menu()]]

        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                spacing: dp(20)
                adaptive_height: True

                # TARJETA 1: RESUMEN GENERAL
                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(120)
                    radius: [15]
                    elevation: 3
                    
                    MDLabel:
                        text: "Total Turnos Agendados"
                        halign: "center"
                        theme_text_color: "Secondary"
                    
                    MDLabel:
                        id: lbl_total_turnos
                        text: "0"
                        halign: "center"
                        font_style: "H3"
                        bold: True
                        theme_text_color: "Primary"

                MDLabel:
                    text: "Destacados"
                    font_style: "H6"
                    size_hint_y: None
                    height: dp(30)

                # TARJETA 2: SERVICIO ESTRELLA
                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    radius: [15]
                    elevation: 2
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        
                        MDIcon:
                            icon: "star-circle"
                            theme_text_color: "Custom"
                            text_color: 1, 0.8, 0, 1
                            font_size: dp(40)
                            size_hint_x: None
                            width: dp(60)
                        
                        MDBoxLayout:
                            orientation: 'vertical'
                            MDLabel:
                                text: "Servicio Más Solicitado"
                                font_style: "Caption"
                            MDLabel:
                                id: lbl_top_servicio
                                text: "-"
                                font_style: "H6"
                                bold: True

                # TARJETA 3: MEJOR CLIENTE
                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    radius: [15]
                    elevation: 2
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        
                        MDIcon:
                            icon: "trophy"
                            theme_text_color: "Custom"
                            text_color: 0, 0.5, 0.8, 1
                            font_size: dp(40)
                            size_hint_x: None
                            width: dp(60)
                        
                        MDBoxLayout:
                            orientation: 'vertical'
                            MDLabel:
                                text: "Cliente Frecuente"
                                font_style: "Caption"
                            MDLabel:
                                id: lbl_top_cliente
                                text: "-"
                                font_style: "H6"
                                bold: True

"""

Builder.load_string(KV_REPORTES)

class ReportesScreen(Screen):
    def on_pre_enter(self):
        self.calcular_estadisticas()

    def calcular_estadisticas(self):
        conn = database.conectar()
        cursor = conn.cursor()
        
        # 1. Total de Turnos
        cursor.execute("SELECT COUNT(*) FROM turnos")
        total = cursor.fetchone()[0]
        self.ids.lbl_total_turnos.text = str(total)

        # 2. Obtener todos los turnos para analizar
        cursor.execute("SELECT cliente_nombre, servicio FROM turnos")
        datos = cursor.fetchall()
        conn.close()

        if not datos:
            self.ids.lbl_top_servicio.text = "Sin datos"
            self.ids.lbl_top_cliente.text = "Sin datos"
            return

        # Separamos en listas
        lista_clientes = [fila[0] for fila in datos]
        lista_servicios = [fila[1] for fila in datos]

        # 3. Calcular Top Servicio
        if lista_servicios:
            contador_servicios = collections.Counter(lista_servicios)
            top_servicio = contador_servicios.most_common(1)[0] # Retorna ('Corte', 5)
            self.ids.lbl_top_servicio.text = f"{top_servicio[0]} ({top_servicio[1]})"
        else:
            self.ids.lbl_top_servicio.text = "-"

        # 4. Calcular Top Cliente
        if lista_clientes:
            contador_clientes = collections.Counter(lista_clientes)
            top_cliente = contador_clientes.most_common(1)[0]
            self.ids.lbl_top_cliente.text = f"{top_cliente[0]} ({top_cliente[1]})"
        else:
            self.ids.lbl_top_cliente.text = "-"