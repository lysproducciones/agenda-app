from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.lang import Builder
from kivy.core.window import Window
import database

# Importamos las pantallas
from screens.dashboard import DashboardScreen
from screens.agenda import AgendaScreen
from screens.clientes import ClientesScreen
from screens.servicios import ServiciosScreen
from screens.reportes import ReportesScreen  # <--- IMPORTAR REPORTES

Window.size = (500, 850)

class AgendaApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.theme_style = "Light"
        
        database.crear_tablas()
        
        # Cargar KV
        Builder.load_file("ui/dashboard.kv")
        Builder.load_file("ui/agenda.kv")
        Builder.load_file("ui/clientes.kv")

        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name='menu'))
        sm.add_widget(AgendaScreen(name='agenda'))
        sm.add_widget(ClientesScreen(name='clientes'))
        sm.add_widget(ServiciosScreen(name='servicios'))
        sm.add_widget(ReportesScreen(name='reportes')) # <--- AGREGAR PANTALLA
        
        return sm

    def ir_al_menu(self):
        self.root.current = 'menu'

if __name__ == "__main__":
    AgendaApp().run()