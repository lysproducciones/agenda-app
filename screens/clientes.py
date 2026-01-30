from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.modalview import ModalView
from kivy.metrics import dp
import database

class ClientesScreen(Screen):
    cliente_seleccionado_id = None

    def on_pre_enter(self):
        self.cargar_lista()
        self.resetear_formulario()

    def mostrar_aviso(self, texto, color_bg=(0.2, 0.2, 0.2, 1)):
        try:
            aviso = Snackbar(
                MDLabel(text=texto, theme_text_color="Custom", text_color=(1, 1, 1, 1)),
                bg_color=color_bg,
                size_hint_x=0.9,
                pos_hint={"center_x": 0.5, "bottom": 1},
                padding=dp(10)
            )
            aviso.open()
        except: pass

    # --- VENTANA SEGURA (ModalView) ---
    def ver_detalle_cliente(self, datos_cliente):
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT fecha, hora, detalle FROM turnos WHERE cliente_nombre = ?", (datos_cliente[1],))
        turnos = cursor.fetchall()
        conn.close()

        texto_detalle = f"📞 Tel: {datos_cliente[2]}\n"
        if datos_cliente[3]:
            texto_detalle += f"📞 Alt: {datos_cliente[3]}\n"
        texto_detalle += f"🏠 Dir: {datos_cliente[4]}\n\n"
        
        if turnos:
            texto_detalle += "[b]Próximos Turnos:[/b]\n"
            for t in turnos:
                texto_detalle += f"• {t[0]} {t[1]} ({t[2]})\n"
        else:
            texto_detalle += "No tiene turnos agendados."

        vista = ModalView(size_hint=(0.85, None), height=dp(400), auto_dismiss=True, background_color=(0,0,0,0.5))
        
        card = MDCard(orientation='vertical', padding=dp(20), spacing=dp(10), radius=[15])
        card.add_widget(MDLabel(text=datos_cliente[1], font_style="H6", size_hint_y=None, height=dp(30)))
        card.add_widget(MDLabel(text=texto_detalle, theme_text_color="Secondary", markup=True))
        
        box_botones = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(50), adaptive_width=True, pos_hint={'right': 1})
        
        app = MDApp.get_running_app()
        btn_cerrar = MDFlatButton(text="CERRAR", on_release=lambda x: vista.dismiss())
        btn_editar = MDRaisedButton(text="EDITAR", md_bg_color=app.theme_cls.primary_color, 
                                    on_release=lambda x: [vista.dismiss(), self.activar_edicion(datos_cliente)])
        
        box_botones.add_widget(btn_cerrar)
        box_botones.add_widget(btn_editar)
        card.add_widget(box_botones)
        
        vista.add_widget(card)
        vista.open()

    def activar_edicion(self, datos_cliente):
        self.cliente_seleccionado_id = datos_cliente[0]
        self.ids.nombre_cliente.text = datos_cliente[1]
        self.ids.telefono_cliente.text = datos_cliente[2]
        self.ids.telefono_alt.text = datos_cliente[3]
        self.ids.direccion_cliente.text = datos_cliente[4]

    def guardar_datos(self):
        nombre = self.ids.nombre_cliente.text
        tel = self.ids.telefono_cliente.text
        tel_alt = self.ids.telefono_alt.text
        dir = self.ids.direccion_cliente.text

        if not nombre.strip():
            self.mostrar_aviso("¡Falta el nombre!", (1, 0, 0, 1))
            return

        conn = database.conectar()
        cursor = conn.cursor()

        try:
            if self.cliente_seleccionado_id:
                cursor.execute("""
                    UPDATE clientes SET nombre=?, telefono=?, telefono_alt=?, direccion=? WHERE id=?
                """, (nombre, tel, tel_alt, dir, self.cliente_seleccionado_id))
                mensaje = "✅ Cliente Modificado"
            else:
                cursor.execute("""
                    INSERT INTO clientes (nombre, telefono, telefono_alt, direccion) VALUES (?, ?, ?, ?)
                """, (nombre, tel, tel_alt, dir))
                mensaje = "✅ Cliente Guardado"

            conn.commit()
            self.mostrar_aviso(mensaje, (0, 0.7, 0, 1))
            self.resetear_formulario()
            self.cargar_lista()

        except Exception as e:
            self.mostrar_aviso(f"Error: {e}", (1, 0, 0, 1))
        finally:
            conn.close()

    def eliminar_cliente(self, id_cliente):
        try:
            conn = database.conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
            conn.commit()
            conn.close()
            self.mostrar_aviso("🗑️ Cliente Eliminado", (1, 0, 0, 1))
            self.cargar_lista()
            self.resetear_formulario()
        except Exception as e:
            self.mostrar_aviso(f"Error al borrar: {e}")

    def resetear_formulario(self):
        self.cliente_seleccionado_id = None
        self.ids.nombre_cliente.text = ""
        self.ids.telefono_cliente.text = ""
        self.ids.telefono_alt.text = ""
        self.ids.direccion_cliente.text = ""

    def cargar_lista(self):
        self.ids.container_lista.clear_widgets()
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, telefono, telefono_alt, direccion FROM clientes")
        mis_clientes = cursor.fetchall()
        conn.close()

        for c in mis_clientes:
            item = TwoLineAvatarIconListItem(
                text=c[1],
                secondary_text=f"Tel: {c[2]}",
                on_release=lambda x, datos=c: self.ver_detalle_cliente(datos)
            )
            item.add_widget(IconLeftWidget(icon="account"))
            boton_borrar = IconRightWidget(icon="trash-can", theme_text_color="Custom", text_color=(1, 0, 0, 1),
                                           on_release=lambda x, id_cli=c[0]: self.eliminar_cliente(id_cli))
            item.add_widget(boton_borrar)
            self.ids.container_lista.add_widget(item)

    def buscar_en_lista(self, texto):
        # Filtro simple visual
        self.ids.container_lista.clear_widgets()
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, telefono, telefono_alt, direccion FROM clientes WHERE nombre LIKE ?", (f'%{texto}%',))
        mis_clientes = cursor.fetchall()
        conn.close()
        
        for c in mis_clientes:
            item = TwoLineAvatarIconListItem(
                text=c[1], secondary_text=f"Tel: {c[2]}",
                on_release=lambda x, datos=c: self.ver_detalle_cliente(datos)
            )
            item.add_widget(IconLeftWidget(icon="account"))
            self.ids.container_lista.add_widget(item)