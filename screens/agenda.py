from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.modalview import ModalView
from kivy.metrics import dp
import database
import webbrowser
from urllib.parse import quote
from datetime import datetime # <--- NECESARIO PARA COMPARAR FECHAS

class AgendaScreen(Screen):
    fecha_seleccionada = ""
    hora_seleccionada = ""
    turno_seleccionado_id = None
    menu_clientes = None
    menu_servicios = None

    def on_pre_enter(self):
        self.cargar_turnos()
        self.resetear_formulario()

    # --- LÓGICA DE SERVICIOS ---
    def abrir_menu_servicios(self):
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM servicios")
        resultados = cursor.fetchall()
        conn.close()

        items_menu = []
        if resultados:
            for r in resultados:
                items_menu.append({
                    "viewclass": "OneLineListItem",
                    "text": r[0],
                    "height": dp(56),
                    "on_release": lambda x=r[0]: self.seleccionar_servicio(x),
                })
        else:
             items_menu.append({
                "viewclass": "OneLineListItem",
                "text": "Sin servicios",
                "height": dp(56),
                "on_release": lambda x: self.menu_servicios.dismiss(),
            })

        self.menu_servicios = MDDropdownMenu(
            caller=self.ids.input_servicio,
            items=items_menu,
            width_mult=4,
            max_height=dp(200),
        )
        self.menu_servicios.open()

    def seleccionar_servicio(self, nombre_servicio):
        self.ids.input_servicio.text = nombre_servicio
        self.menu_servicios.dismiss()

    # --- LÓGICA DE CLIENTES ---
    def buscar_cliente(self, texto_busqueda):
        if self.menu_clientes:
            self.menu_clientes.dismiss()
            self.menu_clientes = None
        if not texto_busqueda: return

        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT nombre FROM clientes WHERE nombre LIKE ?", (f'%{texto_busqueda}%',))
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            items_menu = [{
                "viewclass": "OneLineListItem",
                "text": r[0],
                "height": dp(56),
                "on_release": lambda x=r[0]: self.seleccionar_cliente(x),
            } for r in resultados]
            self.menu_clientes = MDDropdownMenu(
                caller=self.ids.input_cliente,
                items=items_menu,
                width_mult=4,
                max_height=dp(200),
            )
            self.menu_clientes.open()

    def seleccionar_cliente(self, nombre_elegido):
        self.ids.input_cliente.text = nombre_elegido
        if self.menu_clientes: self.menu_clientes.dismiss()

    # --- FECHA Y HORA ---
    def abrir_calendario(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.fijar_fecha)
        date_dialog.open()

    def fijar_fecha(self, instance, value, date_range):
        self.fecha_seleccionada = value.strftime("%d/%m/%Y")
        self.ids.btn_fecha.text = self.fecha_seleccionada
        self.ids.btn_fecha.md_bg_color = (0, 0.7, 0, 1)

    def abrir_reloj(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.fijar_hora)
        time_dialog.open()

    def fijar_hora(self, instance, time):
        self.hora_seleccionada = time.strftime("%H:%M")
        self.ids.btn_hora.text = self.hora_seleccionada
        self.ids.btn_hora.md_bg_color = (0, 0.7, 0, 1)

    # --- CRUD TURNOS ---
    def guardar_turno(self):
        cliente = self.ids.input_cliente.text
        servicio = self.ids.input_servicio.text
        nota = self.ids.input_nota.text

        if not cliente or not servicio or not self.fecha_seleccionada or not self.hora_seleccionada:
            self.mostrar_aviso("Faltan datos obligatorios")
            return

        conn = database.conectar()
        cursor = conn.cursor()

        try:
            if self.turno_seleccionado_id:
                cursor.execute("""
                    UPDATE turnos SET cliente_nombre=?, servicio=?, fecha=?, hora=?, detalle=? 
                    WHERE id=?
                """, (cliente, servicio, self.fecha_seleccionada, self.hora_seleccionada, nota, self.turno_seleccionado_id))
                mensaje = "Turno Modificado"
            else:
                cursor.execute("""
                    INSERT INTO turnos (cliente_nombre, servicio, fecha, hora, detalle) 
                    VALUES (?, ?, ?, ?, ?)
                """, (cliente, servicio, self.fecha_seleccionada, self.hora_seleccionada, nota))
                mensaje = "Turno Agendado"

            conn.commit()
            self.mostrar_aviso(mensaje)
            self.resetear_formulario()
            self.cargar_turnos()

        except Exception as e:
            self.mostrar_aviso(f"Error: {e}")
        finally:
            conn.close()

    def cargar_turnos(self):
        self.ids.lista_turnos.clear_widgets()
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cliente_nombre, servicio, fecha, hora, detalle FROM turnos")
        turnos_crudos = cursor.fetchall()
        conn.close()

        # Obtenemos fecha y hora actual
        ahora = datetime.now()

        # Procesamos los turnos para ordenarlos correctamente por fecha
        lista_ordenada = []
        for t in turnos_crudos:
            try:
                # Convertimos strings a objeto datetime real
                fecha_hora_str = f"{t[3]} {t[4]}"
                dt_obj = datetime.strptime(fecha_hora_str, "%d/%m/%Y %H:%M")
            except:
                # Si falla la fecha (ej: datos viejos), la ponemos al final
                dt_obj = datetime.max 
            
            lista_ordenada.append({
                "data": t,
                "dt": dt_obj
            })
        
        # Ordenamos: Más antiguos primero (o puedes poner reverse=True si prefieres lo nuevo arriba)
        lista_ordenada.sort(key=lambda x: x["dt"])

        for item_dict in lista_ordenada:
            t = item_dict["data"]
            dt_turno = item_dict["dt"]

            # Determinamos si ya pasó
            es_pasado = dt_turno < ahora

            texto_principal = f"{t[3]} - {t[4]} | {t[1]}"
            texto_secundario = f"👉 {t[2]}"
            
            item = TwoLineAvatarIconListItem(
                text=texto_principal,
                secondary_text=texto_secundario,
                on_release=lambda x, datos=t: self.ver_detalle_turno(datos)
            )

            # --- EFECTO VISUAL DE "PASADO" ---
            if es_pasado:
                item.opacity = 0.4  # 40% de visibilidad (Gris/Transparente)
            else:
                item.opacity = 1.0  # 100% visible (Normal)

            item.add_widget(IconLeftWidget(icon="clock-outline"))
            
            boton_borrar = IconRightWidget(
                icon="trash-can",
                theme_text_color="Custom",
                text_color=(1, 0, 0, 1),
                on_release=lambda x, id_t=t[0]: self.eliminar_turno(id_t)
            )
            # También bajamos la opacidad del botón borrar si es pasado, para que combine
            if es_pasado:
                boton_borrar.opacity = 0.5

            item.add_widget(boton_borrar)
            self.ids.lista_turnos.add_widget(item)

    # --- DETALLE + WHATSAPP ---
    def ver_detalle_turno(self, datos_turno):
        id_t, cliente, servicio, fecha, hora, nota = datos_turno
        
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT telefono FROM clientes WHERE nombre = ?", (cliente,))
        res = cursor.fetchone()
        conn.close()
        telefono = res[0] if res else ""

        texto_info = f"📅 {fecha}  ⏰ {hora}\n👤 {cliente}\n📞 {telefono}\n💼 {servicio}\n📝 {nota}"

        vista = ModalView(size_hint=(0.9, None), height=dp(400), auto_dismiss=True, background_color=(0,0,0,0.6))
        card = MDCard(orientation='vertical', padding=dp(20), spacing=dp(15), radius=[20])
        
        card.add_widget(MDLabel(text="Detalle del Turno", font_style="H5", bold=True, size_hint_y=None, height=dp(30)))
        card.add_widget(MDLabel(text=texto_info, theme_text_color="Secondary"))

        box_botones = MDBoxLayout(orientation='horizontal', spacing=dp(10), adaptive_height=True)
        
        btn_wsp = MDRaisedButton(
            text="WHATSAPP",
            icon="whatsapp",
            md_bg_color=(0.1, 0.8, 0.3, 1),
            size_hint_x=0.5,
            on_release=lambda x: self.enviar_whatsapp(telefono, cliente, servicio, fecha, hora)
        )

        btn_cerrar = MDFlatButton(
            text="CERRAR",
            size_hint_x=0.3,
            on_release=lambda x: vista.dismiss()
        )
        
        box_botones.add_widget(btn_cerrar)
        box_botones.add_widget(btn_wsp)
        
        card.add_widget(box_botones)
        vista.add_widget(card)
        vista.open()

    def enviar_whatsapp(self, telefono, nombre, servicio, fecha, hora):
        if not telefono:
            self.mostrar_aviso("El cliente no tiene teléfono")
            return
            
        num = ''.join(filter(str.isdigit, telefono))
        if len(num) == 10: 
            num = "549" + num

        mensaje = f"Hola {nombre}, te recuerdo tu turno para *{servicio}* el día *{fecha}* a las *{hora}*. ¡Nos vemos!"
        url = f"https://wa.me/{num}?text={quote(mensaje)}"
        webbrowser.open(url)

    def eliminar_turno(self, id_turno):
        conn = database.conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM turnos WHERE id=?", (id_turno,))
        conn.commit()
        conn.close()
        self.mostrar_aviso("Turno Eliminado")
        self.cargar_turnos()

    def resetear_formulario(self):
        self.turno_seleccionado_id = None
        self.ids.input_cliente.text = ""
        self.ids.input_servicio.text = ""
        self.ids.input_nota.text = ""
        self.ids.btn_fecha.text = "ELEGIR FECHA"
        self.ids.btn_fecha.md_bg_color = (.3, .3, .3, 1)
        self.ids.btn_hora.text = "ELEGIR HORA"
        self.ids.btn_hora.md_bg_color = (.3, .3, .3, 1)
        self.fecha_seleccionada = ""
        self.hora_seleccionada = ""

    def mostrar_aviso(self, texto):
        aviso = Snackbar(
            bg_color=(0.2, 0.2, 0.2, 1),
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5, "bottom": 1},
            padding=dp(10)
        )
        aviso.add_widget(MDLabel(text=texto, theme_text_color="Custom", text_color=(1, 1, 1, 1)))
        aviso.open()