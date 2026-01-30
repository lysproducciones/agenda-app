from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.snackbar import Snackbar
from datetime import datetime
import database

# --- DISEÑO VISUAL INCRUSTADO ---
# Esto garantiza que Kivy encuentre los IDs sí o sí.
KV_PAGOS = """
<CajaScreen>:
    name: 'pagos'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Caja y Pagos"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: app.ir_al_menu()]]

        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            adaptive_height: True

            MDTextField:
                id: input_cliente
                hint_text: "Cliente"
                icon_right: "account-search"
                mode: "rectangle"
                on_text: root.buscar_cliente(self.text)

            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(10)
                adaptive_height: True

                MDTextField:
                    id: input_monto
                    hint_text: "Monto ($)"
                    input_filter: "float"
                    mode: "rectangle"
                    size_hint_x: 0.5

                MDTextField:
                    id: input_nota
                    hint_text: "Nota"
                    mode: "rectangle"
                    size_hint_x: 0.5

            MDRaisedButton:
                text: "REGISTRAR PAGO"
                size_hint_x: 1
                md_bg_color: 0, 0.6, 0, 1
                on_release: root.guardar_pago()

        MDLabel:
            text: "Historial"
            theme_text_color: "Primary"
            font_style: "H6"
            size_hint_y: None
            height: dp(40)
            padding_x: dp(20)

        ScrollView:
            MDList:
                id: lista_pagos
"""

# Cargamos el diseño en memoria
Builder.load_string(KV_PAGOS)

class CajaScreen(Screen):
    def on_pre_enter(self):
        self.cargar_pagos()

    def buscar_cliente(self, texto):
        # Aquí iría el menú desplegable, pero lo simplificamos para asegurar estabilidad primero
        pass 

    def guardar_pago(self):
        cliente = self.ids.input_cliente.text
        monto = self.ids.input_monto.text
        nota = self.ids.input_nota.text

        if not cliente or not monto:
            self.mostrar_aviso("Faltan datos")
            return

        try:
            val_monto = float(monto.replace(',', '.'))
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            conn = database.conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pagos (cliente_nombre, fecha, monto, nota) VALUES (?, ?, ?, ?)", 
                           (cliente, fecha, val_monto, nota))
            conn.commit()
            conn.close()

            self.ids.input_cliente.text = ""
            self.ids.input_monto.text = ""
            self.ids.input_nota.text = ""
            
            self.mostrar_aviso("Pago Guardado")
            self.cargar_pagos()

        except Exception as e:
            self.mostrar_aviso(f"Error: {e}")

    def cargar_pagos(self):
        try:
            self.ids.lista_pagos.clear_widgets()
            
            conn = database.conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, cliente_nombre, fecha, monto, nota FROM pagos ORDER BY id DESC")
            pagos = cursor.fetchall()
            conn.close()

            for p in pagos:
                item = TwoLineIconListItem(
                    text=f"${p[3]} - {p[1]}", 
                    secondary_text=f"{p[2]} {p[4]}"
                )
                item.add_widget(IconLeftWidget(icon="cash"))
                
                btn_borrar = IconRightWidget(
                    icon="trash-can", 
                    on_release=lambda x, id_p=p[0]: self.eliminar(id_p)
                )
                item.add_widget(btn_borrar)
                
                self.ids.lista_pagos.add_widget(item)

        except Exception as e:
            print(f"Error cargando lista: {e}")

    def eliminar(self, id_pago):
        try:
            conn = database.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pagos WHERE id=?", (id_pago,))
            conn.commit()
            conn.close()
            self.cargar_pagos()
        except: pass

    def mostrar_aviso(self, texto):
        try:
            Snackbar(text=texto).open()
        except: pass