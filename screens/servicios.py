from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder
# Importamos MDLabel para poder poner texto dentro del aviso
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
import database

# Diseño visual incrustado
KV_SERVICIOS = """
<ServiciosScreen>:
    name: 'servicios'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Mis Servicios"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.ir_al_menu()]]

        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            adaptive_height: True

            MDTextField:
                id: input_nuevo_servicio
                hint_text: "Nombre del Servicio (ej: Corte de Pelo)"
                mode: "rectangle"
                icon_right: "briefcase-plus"

            MDRaisedButton:
                text: "AGREGAR SERVICIO"
                size_hint_x: 1
                md_bg_color: 0, 0.4, 0.8, 1
                on_release: root.agregar_servicio()

        MDLabel:
            text: "Lista de Servicios Disponibles"
            theme_text_color: "Primary"
            font_style: "H6"
            size_hint_y: None
            height: dp(40)
            padding_x: dp(20)

        ScrollView:
            MDList:
                id: lista_servicios
"""

Builder.load_string(KV_SERVICIOS)

class ServiciosScreen(Screen):
    def on_pre_enter(self):
        self.cargar_lista()

    def agregar_servicio(self):
        nombre = self.ids.input_nuevo_servicio.text.strip()
        if not nombre:
            return

        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO servicios (nombre) VALUES (?)", (nombre,))
        conn.commit()
        conn.close()

        self.ids.input_nuevo_servicio.text = ""
        self.cargar_lista()
        self.mostrar_aviso("Servicio Agregado") # <--- Usamos la nueva función

    def cargar_lista(self):
        self.ids.lista_servicios.clear_widgets()
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM servicios ORDER BY nombre ASC")
        resultados = cursor.fetchall()
        conn.close()

        for r in resultados:
            # Usamos el item correcto para iconos a ambos lados
            item = OneLineAvatarIconListItem(text=r[1])
            
            item.add_widget(IconLeftWidget(icon="briefcase"))
            
            btn_borrar = IconRightWidget(
                icon="trash-can", 
                on_release=lambda x, id_s=r[0]: self.eliminar_servicio(id_s)
            )
            item.add_widget(btn_borrar)
            
            self.ids.lista_servicios.add_widget(item)

    def eliminar_servicio(self, id_servicio):
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM servicios WHERE id=?", (id_servicio,))
        conn.commit()
        conn.close()
        self.cargar_lista()
        self.mostrar_aviso("Servicio Eliminado") # <--- Usamos la nueva función

    # --- FUNCIÓN CORREGIDA PARA MOSTRAR AVISOS ---
    def mostrar_aviso(self, texto):
        # En esta versión de KivyMD, Snackbar es un contenedor.
        # Creamos el Snackbar y le agregamos un MDLabel adentro.
        aviso = Snackbar(
            bg_color=(0.2, 0.2, 0.2, 1),
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5, "bottom": 1},
        )
        # Agregamos el texto manualmente como un widget hijo
        aviso.add_widget(MDLabel(
            text=texto,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        ))
        aviso.open()