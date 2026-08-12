#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SISTEMA DE GESTIÓN DE PLAYLIST MUSICAL
Estructura de Datos y Algoritmos - CEUMH

Creadores:
- Mitchel Ledesma
- Santiago Arellano
- Xavier Zaldivar
- Brandon Reyes

Estructuras utilizadas:
- Lista doblemente enlazada: playlist y navegación.
- Pila: historial de reproducción.
- Cola FIFO: canciones "a continuación".

Interfaz gráfica creada con Tkinter (incluido con Python). El reproductor
simula el avance de cada canción porque el código original no contiene
archivos de audio. La playlist, cola, historial y todos los controles sí son
funcionales.
"""

from __future__ import annotations

import math
import random
import re
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Iterable, Optional


# ---------------------------------------------------------------------------
# DATOS DEL PROYECTO
# ---------------------------------------------------------------------------

NOMBRE_PROYECTO = "Sistema de Gestión de Playlist Musical"
MATERIA = "Estructura de Datos y Algoritmos"
INSTITUCION = "CEUMH"
CREADORES = (
    "Mitchel Ledesma",
    "Santiago Arellano",
    "Xavier Zaldivar",
    "Brandon Reyes",
)


# ---------------------------------------------------------------------------
# MODELO: CANCIÓN, LISTA DOBLE, PILA Y COLA
# ---------------------------------------------------------------------------


class Cancion:
    """Representa una canción dentro de la playlist."""

    def __init__(self, titulo: str, artista: str, duracion: str):
        self.titulo = titulo.strip()
        self.artista = artista.strip()
        self.duracion = duracion.strip()
        self.favorita = False

    @property
    def segundos(self) -> int:
        minutos, segundos = self.duracion.split(":")
        return int(minutos) * 60 + int(segundos)

    def mostrar(self) -> str:
        return f"{self.titulo} - {self.artista} ({self.duracion})"


class Nodo:
    """Nodo de la lista doblemente enlazada."""

    def __init__(self, cancion: Cancion):
        self.cancion = cancion
        self.siguiente: Optional[Nodo] = None
        self.anterior: Optional[Nodo] = None


class ListaDobleEnlazada:
    """Almacena la playlist y permite recorrerla en ambas direcciones."""

    def __init__(self):
        self.inicio: Optional[Nodo] = None
        self.final: Optional[Nodo] = None
        self.actual: Optional[Nodo] = None
        self.cantidad = 0

    def esta_vacia(self) -> bool:
        return self.inicio is None

    def insertar_inicio(self, cancion: Cancion) -> Nodo:
        nuevo = Nodo(cancion)
        if self.esta_vacia():
            self.inicio = self.final = self.actual = nuevo
        else:
            nuevo.siguiente = self.inicio
            self.inicio.anterior = nuevo
            self.inicio = nuevo
        self.cantidad += 1
        return nuevo

    def insertar_final(self, cancion: Cancion) -> Nodo:
        nuevo = Nodo(cancion)
        if self.esta_vacia():
            self.inicio = self.final = self.actual = nuevo
        else:
            nuevo.anterior = self.final
            self.final.siguiente = nuevo
            self.final = nuevo
        self.cantidad += 1
        return nuevo

    def buscar(self, titulo: str) -> Optional[Nodo]:
        titulo = titulo.casefold().strip()
        for nodo in self.nodos():
            if nodo.cancion.titulo.casefold() == titulo:
                return nodo
        return None

    def buscar_cancion(self, cancion: Cancion) -> Optional[Nodo]:
        for nodo in self.nodos():
            if nodo.cancion is cancion:
                return nodo
        return None

    def eliminar(self, titulo: str) -> Optional[Cancion]:
        nodo = self.buscar(titulo)
        if nodo is None:
            return None
        return self.eliminar_nodo(nodo)

    def eliminar_nodo(self, nodo: Nodo) -> Cancion:
        if nodo.anterior is None:
            self.inicio = nodo.siguiente
        else:
            nodo.anterior.siguiente = nodo.siguiente

        if nodo.siguiente is None:
            self.final = nodo.anterior
        else:
            nodo.siguiente.anterior = nodo.anterior

        if self.actual is nodo:
            self.actual = nodo.siguiente or nodo.anterior

        nodo.anterior = None
        nodo.siguiente = None
        self.cantidad -= 1

        if self.cantidad == 0:
            self.inicio = self.final = self.actual = None
        return nodo.cancion

    def siguiente(self) -> Optional[Cancion]:
        if self.actual is None:
            self.actual = self.inicio
        elif self.actual.siguiente is not None:
            self.actual = self.actual.siguiente
        else:
            return None
        return self.actual.cancion if self.actual else None

    def anterior(self) -> Optional[Cancion]:
        if self.actual is None:
            self.actual = self.inicio
        elif self.actual.anterior is not None:
            self.actual = self.actual.anterior
        else:
            return None
        return self.actual.cancion if self.actual else None

    def nodos(self) -> Iterable[Nodo]:
        actual = self.inicio
        while actual is not None:
            yield actual
            actual = actual.siguiente

    def canciones(self) -> list[Cancion]:
        return [nodo.cancion for nodo in self.nodos()]


class Pila:
    """Pila LIFO utilizada como historial de reproducción."""

    def __init__(self):
        self.elementos: list[Cancion] = []

    def esta_vacia(self) -> bool:
        return not self.elementos

    def push(self, cancion: Cancion) -> None:
        self.elementos.append(cancion)

    def pop(self) -> Optional[Cancion]:
        return self.elementos.pop() if self.elementos else None

    def peek(self) -> Optional[Cancion]:
        return self.elementos[-1] if self.elementos else None

    def limpiar(self) -> None:
        self.elementos.clear()

    def quitar_cancion(self, cancion: Cancion) -> None:
        self.elementos = [item for item in self.elementos if item is not cancion]


class Cola:
    """Cola FIFO para las canciones que se reproducirán a continuación."""

    def __init__(self):
        self.elementos: list[Cancion] = []

    def esta_vacia(self) -> bool:
        return not self.elementos

    def enqueue(self, cancion: Cancion) -> None:
        self.elementos.append(cancion)

    def dequeue(self) -> Optional[Cancion]:
        return self.elementos.pop(0) if self.elementos else None

    def eliminar_indice(self, indice: int) -> Optional[Cancion]:
        if 0 <= indice < len(self.elementos):
            return self.elementos.pop(indice)
        return None

    def limpiar(self) -> None:
        self.elementos.clear()

    def quitar_cancion(self, cancion: Cancion) -> None:
        self.elementos = [item for item in self.elementos if item is not cancion]


class Playlist:
    """Une las tres estructuras y concentra las operaciones del sistema."""

    def __init__(self):
        self.lista = ListaDobleEnlazada()
        self.historial = Pila()
        self.cola = Cola()

    @property
    def cancion_actual(self) -> Optional[Cancion]:
        return self.lista.actual.cancion if self.lista.actual else None

    def seleccionar(self, cancion: Cancion) -> bool:
        nodo = self.lista.buscar_cancion(cancion)
        if nodo is None:
            return False
        self.lista.actual = nodo
        return True

    def agregar(self, cancion: Cancion, al_inicio: bool = False) -> Nodo:
        if al_inicio:
            return self.lista.insertar_inicio(cancion)
        return self.lista.insertar_final(cancion)

    def eliminar(self, cancion: Cancion) -> bool:
        nodo = self.lista.buscar_cancion(cancion)
        if nodo is None:
            return False
        self.lista.eliminar_nodo(nodo)
        self.cola.quitar_cancion(cancion)
        self.historial.quitar_cancion(cancion)
        return True

    def cargar_ejemplo(self) -> None:
        canciones = (
            Cancion("Darkside", "Alan Walker, Au/Ra & Tomine Harket", "3:59"),
            Cancion("Señorita", "Shawn Mendes & Camila Cabello", "3:39"),
            Cancion("Cry Out", "ONE OK ROCK", "3:47"),
            Cancion("Stuck in the Middle", "ONE OK ROCK", "3:32"),
            Cancion("High on Life", "Martin Garrix & Bonn", "3:50"),
            Cancion("Bohemian Rhapsody", "Queen", "5:55"),
            Cancion("Billie Jean", "Michael Jackson", "4:54"),
            Cancion("Hotel California", "Eagles", "6:30"),
        )
        for cancion in canciones:
            self.agregar(cancion)


# ---------------------------------------------------------------------------
# COMPONENTES VISUALES
# ---------------------------------------------------------------------------


class ScrollableFrame(tk.Frame):
    """Frame vertical con desplazamiento para páginas con mucho contenido."""

    def __init__(self, parent: tk.Widget, bg: str):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )
        self.interior = tk.Frame(self.canvas, bg=bg)
        self.ventana = self.canvas.create_window(
            (0, 0), window=self.interior, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.interior.bind("<Configure>", self._actualizar_region)
        self.canvas.bind("<Configure>", self._ajustar_ancho)
        self.canvas.bind("<Enter>", self._activar_rueda)
        self.canvas.bind("<Leave>", self._desactivar_rueda)

    def _actualizar_region(self, _evento=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho(self, evento) -> None:
        self.canvas.itemconfigure(self.ventana, width=evento.width)

    def _activar_rueda(self, _evento=None) -> None:
        self.canvas.bind_all("<MouseWheel>", self._rueda)
        self.canvas.bind_all("<Button-4>", self._rueda_linux)
        self.canvas.bind_all("<Button-5>", self._rueda_linux)

    def _desactivar_rueda(self, _evento=None) -> None:
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _rueda(self, evento) -> None:
        desplazamiento = -1 if evento.delta > 0 else 1
        self.canvas.yview_scroll(desplazamiento * 3, "units")

    def _rueda_linux(self, evento) -> None:
        self.canvas.yview_scroll(-3 if evento.num == 4 else 3, "units")


def mezclar_color(color_a: str, color_b: str, proporcion: float) -> str:
    """Interpola dos colores hexadecimales."""

    color_a = color_a.lstrip("#")
    color_b = color_b.lstrip("#")
    rgb_a = tuple(int(color_a[i : i + 2], 16) for i in (0, 2, 4))
    rgb_b = tuple(int(color_b[i : i + 2], 16) for i in (0, 2, 4))
    rgb = tuple(
        round(a + (b - a) * proporcion) for a, b in zip(rgb_a, rgb_b)
    )
    return "#" + "".join(f"{valor:02x}" for valor in rgb)


def formato_tiempo(segundos: float) -> str:
    segundos = max(0, int(segundos))
    return f"{segundos // 60}:{segundos % 60:02d}"


# ---------------------------------------------------------------------------
# APLICACIÓN GRÁFICA
# ---------------------------------------------------------------------------


class PlaylistApp:
    """Interfaz moderna inspirada en la composición de la imagen de referencia."""

    COLORES = {
        "fondo": "#090E17",
        "barra": "#0D1420",
        "panel": "#121B29",
        "tarjeta": "#182332",
        "tarjeta_clara": "#1D2A3B",
        "linea": "#243347",
        "texto": "#F4F7FB",
        "secundario": "#8D9AAF",
        "acento": "#20D6BE",
        "acento_oscuro": "#139B8C",
        "morado": "#7457F7",
        "coral": "#FF7288",
        "amarillo": "#FFB55F",
        "peligro": "#FF647C",
    }

    PALETAS = (
        ("#126E82", "#17153B"),
        ("#EF476F", "#56203D"),
        ("#6C4AB6", "#1C315E"),
        ("#F77F00", "#6A040F"),
        ("#168AAD", "#184E77"),
        ("#7B2CBF", "#240046"),
        ("#2A9D8F", "#264653"),
        ("#E76F51", "#3D405B"),
    )

    def __init__(self, root: tk.Tk):
        self.root = root
        self.sistema = Playlist()
        self.sistema.cargar_ejemplo()

        self.pagina_actual = "inicio"
        self.reproduciendo = False
        self.transcurrido = 0.0
        self.aleatorio = False
        self.repeticion = "apagada"  # apagada, todas o una
        self._deslizando = False
        self._toast_actual: Optional[tk.Label] = None
        self._toast_id = None

        self.buscar_var = tk.StringVar()
        self.progreso_var = tk.DoubleVar(value=0)
        self.titulo_pagina_var = tk.StringVar(value="Inicio")
        self.titulo_actual_var = tk.StringVar(value="Nada en reproducción")
        self.artista_actual_var = tk.StringVar(value="Selecciona una canción")
        self.tiempo_actual_var = tk.StringVar(value="0:00")
        self.tiempo_total_var = tk.StringVar(value="0:00")

        self._configurar_ventana()
        self._configurar_estilos()
        self._construir_interfaz()
        self._configurar_atajos()
        self.mostrar_pagina("inicio")
        self.actualizar_reproductor()
        self.root.after(1000, self._reloj_reproduccion)

    # ----- Configuración general ------------------------------------------------

    def _configurar_ventana(self) -> None:
        self.root.title("NOVA Player · Playlist Musical")
        self.root.geometry("1360x790")
        self.root.minsize(1080, 680)
        self.root.configure(bg=self.COLORES["fondo"])
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        self.fuente = self._elegir_fuente()
        self.root.option_add("*Font", (self.fuente, 10))
        self.root.option_add("*tearOff", False)

    def _elegir_fuente(self) -> str:
        disponibles = set(self.root.tk.call("font", "families"))
        for candidata in ("Aptos", "Segoe UI", "Helvetica Neue", "Arial"):
            if candidata in disponibles:
                return candidata
        return "TkDefaultFont"

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self.root)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass

        estilo.configure(
            "Vertical.TScrollbar",
            background=self.COLORES["tarjeta_clara"],
            troughcolor=self.COLORES["fondo"],
            bordercolor=self.COLORES["fondo"],
            arrowcolor=self.COLORES["secundario"],
            width=9,
        )
        estilo.configure(
            "Player.Horizontal.TScale",
            background=self.COLORES["barra"],
            troughcolor=self.COLORES["linea"],
            sliderthickness=12,
            borderwidth=0,
        )

    def _configurar_atajos(self) -> None:
        self.root.bind("<space>", self._atajo_play)
        self.root.bind("<Control-f>", self._atajo_buscar)
        self.root.bind("<Control-F>", self._atajo_buscar)
        self.root.bind("<Control-n>", lambda _e: self.abrir_dialogo_agregar())

    def _atajo_play(self, _evento=None):
        if isinstance(self.root.focus_get(), tk.Entry):
            return
        self.alternar_reproduccion()
        return "break"

    def _atajo_buscar(self, _evento=None):
        self.entrada_buscar.focus_set()
        self.entrada_buscar.select_range(0, "end")
        return "break"

    # ----- Construcción de la ventana ------------------------------------------

    def _construir_interfaz(self) -> None:
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self._construir_barra_lateral()
        self._construir_area_central()
        self._construir_reproductor()

    def _construir_barra_lateral(self) -> None:
        c = self.COLORES
        self.barra_lateral = tk.Frame(self.root, bg=c["barra"], width=210)
        self.barra_lateral.grid(row=0, column=0, sticky="nsew")
        self.barra_lateral.grid_propagate(False)

        marca = tk.Frame(self.barra_lateral, bg=c["barra"])
        marca.pack(fill="x", padx=24, pady=(25, 33))
        tk.Label(
            marca,
            text="N",
            bg=c["acento"],
            fg=c["fondo"],
            width=2,
            height=1,
            font=(self.fuente, 18, "bold"),
        ).pack(side="left")
        nombre = tk.Frame(marca, bg=c["barra"])
        nombre.pack(side="left", padx=(10, 0))
        tk.Label(
            nombre,
            text="NOVA",
            bg=c["barra"],
            fg=c["texto"],
            font=(self.fuente, 15, "bold"),
        ).pack(anchor="w")
        tk.Label(
            nombre,
            text="MUSIC PLAYER",
            bg=c["barra"],
            fg=c["acento"],
            font=(self.fuente, 7, "bold"),
        ).pack(anchor="w")

        tk.Label(
            self.barra_lateral,
            text="EXPLORAR",
            bg=c["barra"],
            fg=c["secundario"],
            font=(self.fuente, 8, "bold"),
        ).pack(anchor="w", padx=25, pady=(0, 8))

        opciones = (
            ("inicio", "⌂", "Inicio"),
            ("playlist", "♫", "Mi playlist"),
            ("cola", "≡", "A continuación"),
            ("historial", "↶", "Historial"),
            ("creadores", "◇", "Creadores"),
        )
        self.botones_navegacion: dict[str, tk.Button] = {}
        for clave, icono, texto in opciones:
            boton = tk.Button(
                self.barra_lateral,
                text=f"  {icono}    {texto}",
                command=lambda pagina=clave: self.mostrar_pagina(pagina),
                bg=c["barra"],
                fg=c["secundario"],
                activebackground=c["tarjeta"],
                activeforeground=c["texto"],
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=18,
                pady=12,
                cursor="hand2",
                font=(self.fuente, 10, "bold"),
            )
            boton.pack(fill="x", padx=10, pady=2)
            self.botones_navegacion[clave] = boton

        self._boton(
            self.barra_lateral,
            "+  Agregar canción",
            self.abrir_dialogo_agregar,
            bg=c["acento"],
            fg=c["fondo"],
            active_bg=c["acento_oscuro"],
            fuente=(self.fuente, 10, "bold"),
            padx=15,
            pady=11,
        ).pack(fill="x", padx=18, pady=(25, 10))

        pie = tk.Frame(self.barra_lateral, bg=c["barra"])
        pie.pack(side="bottom", fill="x", padx=23, pady=23)
        tk.Frame(pie, bg=c["linea"], height=1).pack(fill="x", pady=(0, 14))
        tk.Label(
            pie,
            text="Proyecto académico",
            bg=c["barra"],
            fg=c["texto"],
            font=(self.fuente, 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            pie,
            text=f"{MATERIA}\n{INSTITUCION}",
            bg=c["barra"],
            fg=c["secundario"],
            justify="left",
            font=(self.fuente, 8),
        ).pack(anchor="w", pady=(4, 0))

    def _construir_area_central(self) -> None:
        c = self.COLORES
        self.area_central = tk.Frame(self.root, bg=c["fondo"])
        self.area_central.grid(row=0, column=1, sticky="nsew")
        self.area_central.grid_rowconfigure(1, weight=1)
        self.area_central.grid_columnconfigure(0, weight=1)

        superior = tk.Frame(self.area_central, bg=c["fondo"], height=78)
        superior.grid(row=0, column=0, sticky="ew", padx=28)
        superior.grid_columnconfigure(1, weight=1)
        superior.grid_propagate(False)

        tk.Label(
            superior,
            textvariable=self.titulo_pagina_var,
            bg=c["fondo"],
            fg=c["texto"],
            font=(self.fuente, 18, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=21)

        buscador = tk.Frame(superior, bg=c["tarjeta"], height=42)
        buscador.grid(row=0, column=1, sticky="e", padx=(25, 0), pady=17)
        buscador.grid_propagate(False)
        buscador.configure(width=330)
        tk.Label(
            buscador,
            text="⌕",
            bg=c["tarjeta"],
            fg=c["secundario"],
            font=(self.fuente, 16),
        ).pack(side="left", padx=(14, 7))
        self.entrada_buscar = tk.Entry(
            buscador,
            textvariable=self.buscar_var,
            bg=c["tarjeta"],
            fg=c["texto"],
            insertbackground=c["acento"],
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=(self.fuente, 10),
        )
        self.entrada_buscar.pack(side="left", fill="both", expand=True, pady=8)
        self.entrada_buscar.insert(0, "")
        tk.Button(
            buscador,
            text="×",
            command=lambda: self.buscar_var.set(""),
            bg=c["tarjeta"],
            fg=c["secundario"],
            activebackground=c["tarjeta"],
            activeforeground=c["texto"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(self.fuente, 13),
        ).pack(side="right", padx=(4, 10))
        self.buscar_var.trace_add("write", self._al_buscar)

        self.contenido = tk.Frame(self.area_central, bg=c["fondo"])
        self.contenido.grid(row=1, column=0, sticky="nsew", padx=(28, 20))

    def _construir_reproductor(self) -> None:
        c = self.COLORES
        self.panel_reproductor = tk.Frame(self.root, bg=c["barra"], width=335)
        self.panel_reproductor.grid(row=0, column=2, sticky="nsew")
        self.panel_reproductor.grid_propagate(False)

        cabecera = tk.Frame(self.panel_reproductor, bg=c["barra"])
        cabecera.pack(fill="x", padx=23, pady=(23, 15))
        tk.Label(
            cabecera,
            text="EN REPRODUCCIÓN",
            bg=c["barra"],
            fg=c["secundario"],
            font=(self.fuente, 8, "bold"),
        ).pack(side="left")
        tk.Label(
            cabecera,
            text="NOVA",
            bg=c["barra"],
            fg=c["acento"],
            font=(self.fuente, 9, "bold"),
        ).pack(side="right")

        self.portada_actual = tk.Canvas(
            self.panel_reproductor,
            width=289,
            height=218,
            bg=c["tarjeta"],
            highlightthickness=0,
        )
        self.portada_actual.pack(padx=23)

        info = tk.Frame(self.panel_reproductor, bg=c["barra"])
        info.pack(fill="x", padx=23, pady=(17, 6))
        self.etiqueta_titulo_actual = tk.Label(
            info,
            textvariable=self.titulo_actual_var,
            bg=c["barra"],
            fg=c["texto"],
            anchor="w",
            font=(self.fuente, 14, "bold"),
        )
        self.etiqueta_titulo_actual.pack(fill="x")
        self.etiqueta_artista_actual = tk.Label(
            info,
            textvariable=self.artista_actual_var,
            bg=c["barra"],
            fg=c["secundario"],
            anchor="w",
            font=(self.fuente, 8),
        )
        self.etiqueta_artista_actual.pack(fill="x", pady=(4, 0))

        self.escala_progreso = ttk.Scale(
            self.panel_reproductor,
            from_=0,
            to=1,
            variable=self.progreso_var,
            command=self._mover_progreso,
            style="Player.Horizontal.TScale",
        )
        self.escala_progreso.pack(fill="x", padx=23, pady=(8, 0))
        self.escala_progreso.bind("<ButtonPress-1>", self._iniciar_deslizamiento)
        self.escala_progreso.bind("<ButtonRelease-1>", self._terminar_deslizamiento)

        tiempos = tk.Frame(self.panel_reproductor, bg=c["barra"])
        tiempos.pack(fill="x", padx=24, pady=(1, 10))
        tk.Label(
            tiempos,
            textvariable=self.tiempo_actual_var,
            bg=c["barra"],
            fg=c["secundario"],
            font=(self.fuente, 8),
        ).pack(side="left")
        tk.Label(
            tiempos,
            textvariable=self.tiempo_total_var,
            bg=c["barra"],
            fg=c["secundario"],
            font=(self.fuente, 8),
        ).pack(side="right")

        controles = tk.Frame(self.panel_reproductor, bg=c["barra"])
        controles.pack(pady=(0, 12))
        self.boton_anterior = self._boton_icono(
            controles, "◀", self.reproducir_anterior, 12
        )
        self.boton_anterior.pack(side="left", padx=8)
        self.boton_play = tk.Button(
            controles,
            text="▶",
            command=self.alternar_reproduccion,
            bg=c["acento"],
            fg=c["fondo"],
            activebackground=c["acento_oscuro"],
            activeforeground=c["fondo"],
            relief="flat",
            bd=0,
            width=3,
            height=1,
            cursor="hand2",
            font=(self.fuente, 18, "bold"),
        )
        self.boton_play.pack(side="left", padx=8)
        self.boton_siguiente = self._boton_icono(
            controles, "▶", self.reproducir_siguiente, 12
        )
        self.boton_siguiente.pack(side="left", padx=8)

        acciones = tk.Frame(self.panel_reproductor, bg=c["barra"])
        acciones.pack(fill="x", padx=22, pady=(0, 13))
        for columna in range(4):
            acciones.grid_columnconfigure(columna, weight=1)
        self.boton_aleatorio = self._boton_icono(
            acciones, "⤨", self.alternar_aleatorio, 12
        )
        self.boton_aleatorio.grid(row=0, column=0)
        self.boton_repetir = self._boton_icono(
            acciones, "↻", self.alternar_repeticion, 12
        )
        self.boton_repetir.grid(row=0, column=1)
        self.boton_favorito = self._boton_icono(
            acciones, "♡", self.alternar_favorita_actual, 14
        )
        self.boton_favorito.grid(row=0, column=2)
        self.boton_encolar = self._boton_icono(
            acciones, "+", self.encolar_actual, 15
        )
        self.boton_encolar.grid(row=0, column=3)

        tk.Frame(
            self.panel_reproductor, bg=c["linea"], height=1
        ).pack(fill="x", padx=23)
        cola_titulo = tk.Frame(self.panel_reproductor, bg=c["barra"])
        cola_titulo.pack(fill="x", padx=23, pady=(14, 9))
        tk.Label(
            cola_titulo,
            text="A continuación",
            bg=c["barra"],
            fg=c["texto"],
            font=(self.fuente, 10, "bold"),
        ).pack(side="left")
        tk.Button(
            cola_titulo,
            text="Ver cola",
            command=lambda: self.mostrar_pagina("cola"),
            bg=c["barra"],
            fg=c["acento"],
            activebackground=c["barra"],
            activeforeground=c["texto"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(self.fuente, 8, "bold"),
        ).pack(side="right")
        self.vista_cola = tk.Frame(self.panel_reproductor, bg=c["barra"])
        self.vista_cola.pack(fill="both", expand=True, padx=23, pady=(0, 15))

    # ----- Utilidades de widgets ------------------------------------------------

    def _boton(
        self,
        parent: tk.Widget,
        texto: str,
        comando: Callable,
        *,
        bg: Optional[str] = None,
        fg: Optional[str] = None,
        active_bg: Optional[str] = None,
        fuente=None,
        padx: int = 12,
        pady: int = 8,
    ) -> tk.Button:
        c = self.COLORES
        bg = bg or c["tarjeta"]
        fg = fg or c["texto"]
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=bg,
            fg=fg,
            activebackground=active_bg or c["tarjeta_clara"],
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=padx,
            pady=pady,
            cursor="hand2",
            font=fuente or (self.fuente, 9, "bold"),
        )

    def _boton_icono(
        self, parent: tk.Widget, texto: str, comando: Callable, tamano: int
    ) -> tk.Button:
        c = self.COLORES
        return tk.Button(
            parent,
            text=texto,
            command=comando,
            bg=c["barra"],
            fg=c["secundario"],
            activebackground=c["barra"],
            activeforeground=c["acento"],
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2",
            font=(self.fuente, tamano, "bold"),
        )

    def _limpiar(self, contenedor: tk.Widget) -> None:
        for hijo in contenedor.winfo_children():
            hijo.destroy()

    def _al_buscar(self, *_args) -> None:
        if self.pagina_actual not in ("inicio", "playlist"):
            self.mostrar_pagina("playlist")
        else:
            self.refrescar_pagina()

    def _canciones_filtradas(self) -> list[Cancion]:
        termino = self.buscar_var.get().strip().casefold()
        canciones = self.sistema.lista.canciones()
        if not termino:
            return canciones
        return [
            cancion
            for cancion in canciones
            if termino in cancion.titulo.casefold()
            or termino in cancion.artista.casefold()
        ]

    # ----- Navegación y páginas -------------------------------------------------

    def mostrar_pagina(self, pagina: str) -> None:
        titulos = {
            "inicio": "Inicio",
            "playlist": "Mi playlist",
            "cola": "A continuación",
            "historial": "Historial",
            "creadores": "Creadores",
        }
        self.pagina_actual = pagina
        self.titulo_pagina_var.set(titulos[pagina])

        for clave, boton in self.botones_navegacion.items():
            activo = clave == pagina
            boton.configure(
                bg=self.COLORES["tarjeta"] if activo else self.COLORES["barra"],
                fg=self.COLORES["acento"] if activo else self.COLORES["secundario"],
            )
        self.refrescar_pagina()

    def refrescar_pagina(self) -> None:
        self._limpiar(self.contenido)
        constructores = {
            "inicio": self._pagina_inicio,
            "playlist": self._pagina_playlist,
            "cola": self._pagina_cola,
            "historial": self._pagina_historial,
            "creadores": self._pagina_creadores,
        }
        constructores[self.pagina_actual]()

    def _pagina_inicio(self) -> None:
        c = self.COLORES
        scroll = ScrollableFrame(self.contenido, c["fondo"])
        scroll.pack(fill="both", expand=True)
        cuerpo = scroll.interior

        hero = tk.Frame(cuerpo, bg=c["panel"], height=180)
        hero.pack(fill="x", pady=(0, 24))
        hero.pack_propagate(False)
        izquierda = tk.Frame(hero, bg=c["panel"])
        izquierda.pack(side="left", fill="both", expand=True, padx=28, pady=22)
        tk.Label(
            izquierda,
            text="TU MÚSICA, TU RITMO",
            bg=c["panel"],
            fg=c["acento"],
            font=(self.fuente, 8, "bold"),
        ).pack(anchor="w")
        tk.Label(
            izquierda,
            text="Una playlist hecha\npara sonar diferente.",
            bg=c["panel"],
            fg=c["texto"],
            justify="left",
            font=(self.fuente, 21, "bold"),
        ).pack(anchor="w", pady=(5, 12))
        botones = tk.Frame(izquierda, bg=c["panel"])
        botones.pack(anchor="w")
        self._boton(
            botones,
            "▶  Reproducir",
            self._reproducir_primera,
            bg=c["acento"],
            fg=c["fondo"],
            active_bg=c["acento_oscuro"],
        ).pack(side="left")
        self._boton(
            botones,
            "Ver playlist",
            lambda: self.mostrar_pagina("playlist"),
            bg=c["tarjeta_clara"],
        ).pack(side="left", padx=9)

        arte = tk.Canvas(hero, width=260, height=180, highlightthickness=0)
        arte.pack(side="right")
        self._dibujar_hero(arte, 260, 180)

        estadisticas = tk.Frame(cuerpo, bg=c["fondo"])
        estadisticas.pack(fill="x", pady=(0, 25))
        datos = (
            ("CANCIONES", self.sistema.lista.cantidad, c["acento"]),
            ("EN COLA", len(self.sistema.cola.elementos), c["morado"]),
            ("HISTORIAL", len(self.sistema.historial.elementos), c["coral"]),
            (
                "FAVORITAS",
                sum(x.favorita for x in self.sistema.lista.canciones()),
                c["amarillo"],
            ),
        )
        for indice, (etiqueta, valor, color) in enumerate(datos):
            tarjeta = tk.Frame(estadisticas, bg=c["tarjeta"], height=75)
            tarjeta.grid(
                row=0,
                column=indice,
                sticky="ew",
                padx=(0 if indice == 0 else 6, 0 if indice == 3 else 6),
            )
            tarjeta.grid_propagate(False)
            estadisticas.grid_columnconfigure(indice, weight=1)
            tk.Frame(tarjeta, bg=color, width=4).pack(side="left", fill="y")
            bloque = tk.Frame(tarjeta, bg=c["tarjeta"])
            bloque.pack(side="left", padx=14, pady=10)
            tk.Label(
                bloque,
                text=str(valor),
                bg=c["tarjeta"],
                fg=c["texto"],
                font=(self.fuente, 17, "bold"),
            ).pack(anchor="w")
            tk.Label(
                bloque,
                text=etiqueta,
                bg=c["tarjeta"],
                fg=c["secundario"],
                font=(self.fuente, 7, "bold"),
            ).pack(anchor="w")

        canciones = self._canciones_filtradas()
        self._titulo_seccion(
            cuerpo,
            "Añadidas recientemente",
            "Colección destacada",
            accion=lambda: self.mostrar_pagina("playlist"),
        )
        tarjetas = tk.Frame(cuerpo, bg=c["fondo"])
        tarjetas.pack(fill="x", pady=(11, 25))
        for indice, cancion in enumerate(canciones[:4]):
            self._tarjeta_album(tarjetas, cancion).grid(
                row=0, column=indice, sticky="nsew", padx=(0, 10)
            )
            tarjetas.grid_columnconfigure(indice, weight=1)

        self._titulo_seccion(cuerpo, "Todas las canciones", "Tu biblioteca")
        lista = tk.Frame(cuerpo, bg=c["fondo"])
        lista.pack(fill="x", pady=(10, 25))
        if canciones:
            for indice, cancion in enumerate(canciones):
                self._fila_cancion(lista, cancion, indice + 1).pack(
                    fill="x", pady=4
                )
        else:
            self._estado_vacio(
                lista, "No encontramos canciones", "Prueba con otra búsqueda."
            ).pack(fill="x")

    def _pagina_playlist(self) -> None:
        c = self.COLORES
        scroll = ScrollableFrame(self.contenido, c["fondo"])
        scroll.pack(fill="both", expand=True)
        cuerpo = scroll.interior

        cabecera = tk.Frame(cuerpo, bg=c["fondo"])
        cabecera.pack(fill="x", pady=(4, 18))
        info = tk.Frame(cabecera, bg=c["fondo"])
        info.pack(side="left")
        tk.Label(
            info,
            text="Mi playlist",
            bg=c["fondo"],
            fg=c["texto"],
            font=(self.fuente, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info,
            text=f"{self.sistema.lista.cantidad} canciones · Lista doblemente enlazada",
            bg=c["fondo"],
            fg=c["secundario"],
            font=(self.fuente, 9),
        ).pack(anchor="w", pady=(4, 0))
        self._boton(
            cabecera,
            "+  Nueva canción",
            self.abrir_dialogo_agregar,
            bg=c["acento"],
            fg=c["fondo"],
            active_bg=c["acento_oscuro"],
        ).pack(side="right", pady=7)

        encabezados = tk.Frame(cuerpo, bg=c["fondo"])
        encabezados.pack(fill="x", padx=16, pady=(4, 6))
        tk.Label(
            encabezados,
            text="#    TÍTULO",
            bg=c["fondo"],
            fg=c["secundario"],
            font=(self.fuente, 8, "bold"),
        ).pack(side="left")
        tk.Label(
            encabezados,
            text="DURACIÓN      ACCIONES",
            bg=c["fondo"],
            fg=c["secundario"],
            font=(self.fuente, 8, "bold"),
        ).pack(side="right", padx=8)

        canciones = self._canciones_filtradas()
        if canciones:
            for indice, cancion in enumerate(canciones):
                self._fila_cancion(cuerpo, cancion, indice + 1, eliminar=True).pack(
                    fill="x", pady=4
                )
        else:
            self._estado_vacio(
                cuerpo,
                "La playlist está vacía" if not self.buscar_var.get() else "Sin resultados",
                "Agrega una canción para comenzar."
                if not self.buscar_var.get()
                else "Cambia el texto del buscador.",
                boton="Agregar canción" if not self.buscar_var.get() else None,
                comando=self.abrir_dialogo_agregar,
            ).pack(fill="x", pady=15)

    def _pagina_cola(self) -> None:
        c = self.COLORES
        scroll = ScrollableFrame(self.contenido, c["fondo"])
        scroll.pack(fill="both", expand=True)
        cuerpo = scroll.interior

        cabecera = tk.Frame(cuerpo, bg=c["fondo"])
        cabecera.pack(fill="x", pady=(4, 20))
        info = tk.Frame(cabecera, bg=c["fondo"])
        info.pack(side="left")
        tk.Label(
            info,
            text="A continuación",
            bg=c["fondo"],
            fg=c["texto"],
            font=(self.fuente, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info,
            text="La primera canción que entra es la primera que sale (FIFO)",
            bg=c["fondo"],
            fg=c["secundario"],
            font=(self.fuente, 9),
        ).pack(anchor="w", pady=(4, 0))
        if self.sistema.cola.elementos:
            self._boton(
                cabecera,
                "Vaciar cola",
                self.vaciar_cola,
                bg=c["tarjeta"],
                fg=c["peligro"],
            ).pack(side="right", pady=8)

        actual = self.sistema.cancion_actual
        if actual:
            self._titulo_seccion(cuerpo, "Sonando ahora", "Reproducción actual")
            self._fila_cancion(cuerpo, actual, "•", solo_play=True).pack(
                fill="x", pady=(10, 22)
            )

        self._titulo_seccion(
            cuerpo,
            "Cola de reproducción",
            f"{len(self.sistema.cola.elementos)} canciones pendientes",
        )
        cola = tk.Frame(cuerpo, bg=c["fondo"])
        cola.pack(fill="x", pady=(10, 20))
        if self.sistema.cola.elementos:
            for indice, cancion in enumerate(self.sistema.cola.elementos):
                self._fila_cola(cola, cancion, indice).pack(fill="x", pady=4)
        else:
            self._estado_vacio(
                cola,
                "Tu cola está vacía",
                "Usa el botón + de cualquier canción para agregarla.",
                boton="Ver playlist",
                comando=lambda: self.mostrar_pagina("playlist"),
            ).pack(fill="x")

    def _pagina_historial(self) -> None:
        c = self.COLORES
        scroll = ScrollableFrame(self.contenido, c["fondo"])
        scroll.pack(fill="both", expand=True)
        cuerpo = scroll.interior

        cabecera = tk.Frame(cuerpo, bg=c["fondo"])
        cabecera.pack(fill="x", pady=(4, 20))
        info = tk.Frame(cabecera, bg=c["fondo"])
        info.pack(side="left")
        tk.Label(
            info,
            text="Historial",
            bg=c["fondo"],
            fg=c["texto"],
            font=(self.fuente, 24, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info,
            text="La última canción reproducida aparece primero (pila LIFO)",
            bg=c["fondo"],
            fg=c["secundario"],
            font=(self.fuente, 9),
        ).pack(anchor="w", pady=(4, 0))
        if self.sistema.historial.elementos:
            self._boton(
                cabecera,
                "Limpiar historial",
                self.vaciar_historial,
                bg=c["tarjeta"],
                fg=c["peligro"],
            ).pack(side="right", pady=8)

        historial = list(reversed(self.sistema.historial.elementos))
        if historial:
            for indice, cancion in enumerate(historial, start=1):
                self._fila_cancion(cuerpo, cancion, indice, solo_play=True).pack(
                    fill="x", pady=4
                )
        else:
            self._estado_vacio(
                cuerpo,
                "Aún no hay historial",
                "Reproduce varias canciones y aparecerán aquí.",
                boton="Reproducir playlist",
                comando=self._reproducir_primera,
            ).pack(fill="x", pady=10)

    def _pagina_creadores(self) -> None:
        c = self.COLORES
        scroll = ScrollableFrame(self.contenido, c["fondo"])
        scroll.pack(fill="both", expand=True)
        cuerpo = scroll.interior

        portada = tk.Frame(cuerpo, bg=c["panel"], height=175)
        portada.pack(fill="x", pady=(4, 25))
        portada.pack_propagate(False)
        marca = tk.Label(
            portada,
            text="N",
            bg=c["acento"],
            fg=c["fondo"],
            width=3,
            height=1,
            font=(self.fuente, 25, "bold"),
        )
        marca.pack(side="left", padx=28, pady=40)
        texto = tk.Frame(portada, bg=c["panel"])
        texto.pack(side="left", fill="both", expand=True, pady=30)
        tk.Label(
            texto,
            text=NOMBRE_PROYECTO,
            bg=c["panel"],
            fg=c["texto"],
            font=(self.fuente, 21, "bold"),
        ).pack(anchor="w")
        tk.Label(
            texto,
            text=f"{MATERIA} · {INSTITUCION}",
            bg=c["panel"],
            fg=c["acento"],
            font=(self.fuente, 10, "bold"),
        ).pack(anchor="w", pady=(7, 5))
        tk.Label(
            texto,
            text="Aplicación académica que demuestra estructuras de datos\nmediante una experiencia visual e interactiva.",
            bg=c["panel"],
            fg=c["secundario"],
            justify="left",
            font=(self.fuente, 9),
        ).pack(anchor="w")

        self._titulo_seccion(cuerpo, "Creadores", "Equipo del proyecto")
        equipo = tk.Frame(cuerpo, bg=c["fondo"])
        equipo.pack(fill="x", pady=(12, 25))
        colores = (c["acento"], c["morado"], c["coral"], c["amarillo"])
        for indice, nombre in enumerate(CREADORES):
            tarjeta = tk.Frame(equipo, bg=c["tarjeta"], height=120)
            tarjeta.grid(
                row=0,
                column=indice,
                sticky="nsew",
                padx=(0 if indice == 0 else 6, 0 if indice == 3 else 6),
            )
            equipo.grid_columnconfigure(indice, weight=1)
            tarjeta.grid_propagate(False)
            iniciales = "".join(parte[0] for parte in nombre.split()[:2])
            tk.Label(
                tarjeta,
                text=iniciales,
                bg=colores[indice],
                fg=c["fondo"],
                width=4,
                height=2,
                font=(self.fuente, 13, "bold"),
            ).pack(pady=(14, 7))
            tk.Label(
                tarjeta,
                text=nombre,
                bg=c["tarjeta"],
                fg=c["texto"],
                font=(self.fuente, 9, "bold"),
            ).pack()
            tk.Label(
                tarjeta,
                text="Creador",
                bg=c["tarjeta"],
                fg=c["secundario"],
                font=(self.fuente, 7),
            ).pack(pady=(2, 0))

        self._titulo_seccion(cuerpo, "Estructuras implementadas", "Núcleo del sistema")
        estructuras = tk.Frame(cuerpo, bg=c["fondo"])
        estructuras.pack(fill="x", pady=(12, 30))
        datos = (
            (
                "Lista doblemente enlazada",
                "Conecta cada canción con la anterior y la siguiente para navegar en ambos sentidos.",
                c["acento"],
            ),
            (
                "Pila · LIFO",
                "Guarda el historial; la última canción registrada es la primera en recuperarse.",
                c["morado"],
            ),
            (
                "Cola · FIFO",
                "Organiza 'A continuación'; la primera canción agregada se reproduce primero.",
                c["coral"],
            ),
        )
        for indice, (titulo, descripcion, color) in enumerate(datos):
            tarjeta = tk.Frame(estructuras, bg=c["tarjeta"], height=115)
            tarjeta.grid(
                row=0,
                column=indice,
                sticky="nsew",
                padx=(0 if indice == 0 else 7, 0 if indice == 2 else 7),
            )
            tarjeta.grid_columnconfigure(1, weight=1)
            tarjeta.grid_propagate(False)
            tk.Frame(tarjeta, bg=color, width=5).grid(row=0, column=0, sticky="ns")
            contenido = tk.Frame(tarjeta, bg=c["tarjeta"])
            contenido.grid(row=0, column=1, sticky="nsew", padx=16, pady=15)
            tk.Label(
                contenido,
                text=titulo,
                bg=c["tarjeta"],
                fg=c["texto"],
                font=(self.fuente, 10, "bold"),
            ).pack(anchor="w")
            tk.Label(
                contenido,
                text=descripcion,
                bg=c["tarjeta"],
                fg=c["secundario"],
                justify="left",
                wraplength=190,
                font=(self.fuente, 8),
            ).pack(anchor="w", pady=(7, 0))

    # ----- Componentes de las páginas ------------------------------------------

    def _titulo_seccion(
        self,
        parent: tk.Widget,
        titulo: str,
        subtitulo: str,
        accion: Optional[Callable] = None,
    ) -> None:
        c = self.COLORES
        fila = tk.Frame(parent, bg=c["fondo"])
        fila.pack(fill="x")
        textos = tk.Frame(fila, bg=c["fondo"])
        textos.pack(side="left")
        tk.Label(
            textos,
            text=titulo,
            bg=c["fondo"],
            fg=c["texto"],
            font=(self.fuente, 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            textos,
            text=subtitulo,
            bg=c["fondo"],
            fg=c["secundario"],
            font=(self.fuente, 8),
        ).pack(anchor="w", pady=(2, 0))
        if accion:
            tk.Button(
                fila,
                text="Ver todo  →",
                command=accion,
                bg=c["fondo"],
                fg=c["acento"],
                activebackground=c["fondo"],
                activeforeground=c["texto"],
                relief="flat",
                bd=0,
                cursor="hand2",
                font=(self.fuente, 8, "bold"),
            ).pack(side="right", pady=8)

    def _tarjeta_album(self, parent: tk.Widget, cancion: Cancion) -> tk.Frame:
        c = self.COLORES
        tarjeta = tk.Frame(parent, bg=c["tarjeta"], height=205, cursor="hand2")
        tarjeta.grid_propagate(False)
        tarjeta.grid_columnconfigure(0, weight=1)

        portada = tk.Canvas(tarjeta, height=118, highlightthickness=0, cursor="hand2")
        portada.grid(row=0, column=0, sticky="ew", padx=9, pady=(9, 7))
        portada.bind("<Configure>", lambda e, cv=portada, x=cancion: self._dibujar_portada(cv, x, e.width, 118))
        portada.bind("<Button-1>", lambda _e, x=cancion: self.reproducir_cancion(x))

        titulo = tk.Label(
            tarjeta,
            text=cancion.titulo,
            bg=c["tarjeta"],
            fg=c["texto"],
            anchor="w",
            font=(self.fuente, 9, "bold"),
        )
        titulo.grid(row=1, column=0, sticky="ew", padx=11)
        titulo.bind("<Button-1>", lambda _e, x=cancion: self.reproducir_cancion(x))
        tk.Label(
            tarjeta,
            text=cancion.artista,
            bg=c["tarjeta"],
            fg=c["secundario"],
            anchor="w",
            font=(self.fuente, 7),
        ).grid(row=2, column=0, sticky="ew", padx=11, pady=(3, 0))
        acciones = tk.Frame(tarjeta, bg=c["tarjeta"])
        acciones.grid(row=3, column=0, sticky="ew", padx=7, pady=(4, 7))
        tk.Label(
            acciones,
            text=cancion.duracion,
            bg=c["tarjeta"],
            fg=c["secundario"],
            font=(self.fuente, 7),
        ).pack(side="left", padx=4)
        tk.Button(
            acciones,
            text="＋",
            command=lambda x=cancion: self.encolar(x),
            bg=c["tarjeta"],
            fg=c["acento"],
            activebackground=c["tarjeta"],
            activeforeground=c["texto"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(self.fuente, 12, "bold"),
        ).pack(side="right")
        return tarjeta

    def _fila_cancion(
        self,
        parent: tk.Widget,
        cancion: Cancion,
        numero,
        eliminar: bool = False,
        solo_play: bool = False,
    ) -> tk.Frame:
        c = self.COLORES
        activa = self.sistema.cancion_actual is cancion
        fondo = c["tarjeta_clara"] if activa else c["tarjeta"]
        fila = tk.Frame(parent, bg=fondo, height=64)
        fila.pack_propagate(False)

        tk.Label(
            fila,
            text=str(numero),
            bg=fondo,
            fg=c["acento"] if activa else c["secundario"],
            width=3,
            font=(self.fuente, 9, "bold"),
        ).pack(side="left", padx=(8, 2))

        portada = tk.Canvas(fila, width=46, height=46, highlightthickness=0)
        portada.pack(side="left", padx=(0, 11), pady=9)
        self._dibujar_portada(portada, cancion, 46, 46, compacta=True)

        info = tk.Frame(fila, bg=fondo)
        info.pack(side="left", fill="both", expand=True, pady=11)
        etiqueta_titulo = tk.Label(
            info,
            text=cancion.titulo,
            bg=fondo,
            fg=c["acento"] if activa else c["texto"],
            anchor="w",
            font=(self.fuente, 10, "bold"),
            cursor="hand2",
        )
        etiqueta_titulo.pack(fill="x")
        etiqueta_titulo.bind(
            "<Button-1>", lambda _e, x=cancion: self.reproducir_cancion(x)
        )
        tk.Label(
            info,
            text=cancion.artista,
            bg=fondo,
            fg=c["secundario"],
            anchor="w",
            font=(self.fuente, 8),
        ).pack(fill="x", pady=(2, 0))

        tk.Label(
            fila,
            text=cancion.duracion,
            bg=fondo,
            fg=c["secundario"],
            width=7,
            font=(self.fuente, 8),
        ).pack(side="left", padx=4)

        if not solo_play:
            tk.Button(
                fila,
                text="♥" if cancion.favorita else "♡",
                command=lambda x=cancion: self.alternar_favorita(x),
                bg=fondo,
                fg=c["coral"] if cancion.favorita else c["secundario"],
                activebackground=fondo,
                activeforeground=c["coral"],
                relief="flat",
                bd=0,
                width=3,
                cursor="hand2",
                font=(self.fuente, 12),
            ).pack(side="left")
            tk.Button(
                fila,
                text="＋",
                command=lambda x=cancion: self.encolar(x),
                bg=fondo,
                fg=c["secundario"],
                activebackground=fondo,
                activeforeground=c["acento"],
                relief="flat",
                bd=0,
                width=3,
                cursor="hand2",
                font=(self.fuente, 13, "bold"),
            ).pack(side="left")

        tk.Button(
            fila,
            text="❚❚" if activa and self.reproduciendo else "▶",
            command=lambda x=cancion: self._play_desde_fila(x),
            bg=c["acento"] if activa else fondo,
            fg=c["fondo"] if activa else c["texto"],
            activebackground=c["acento_oscuro"],
            activeforeground=c["fondo"],
            relief="flat",
            bd=0,
            width=4,
            height=2,
            cursor="hand2",
            font=(self.fuente, 9, "bold"),
        ).pack(side="left", padx=(5, 7))

        if eliminar:
            tk.Button(
                fila,
                text="×",
                command=lambda x=cancion: self.eliminar_cancion(x),
                bg=fondo,
                fg=c["secundario"],
                activebackground=fondo,
                activeforeground=c["peligro"],
                relief="flat",
                bd=0,
                width=3,
                cursor="hand2",
                font=(self.fuente, 13),
            ).pack(side="left", padx=(0, 6))
        return fila

    def _fila_cola(
        self, parent: tk.Widget, cancion: Cancion, indice: int
    ) -> tk.Frame:
        c = self.COLORES
        fila = tk.Frame(parent, bg=c["tarjeta"], height=65)
        fila.pack_propagate(False)
        tk.Label(
            fila,
            text=f"{indice + 1:02d}",
            bg=c["tarjeta"],
            fg=c["acento"] if indice == 0 else c["secundario"],
            width=4,
            font=(self.fuente, 9, "bold"),
        ).pack(side="left", padx=(9, 2))
        portada = tk.Canvas(fila, width=46, height=46, highlightthickness=0)
        portada.pack(side="left", padx=(0, 11))
        self._dibujar_portada(portada, cancion, 46, 46, compacta=True)
        info = tk.Frame(fila, bg=c["tarjeta"])
        info.pack(side="left", fill="both", expand=True, pady=11)
        tk.Label(
            info,
            text=cancion.titulo,
            bg=c["tarjeta"],
            fg=c["texto"],
            anchor="w",
            font=(self.fuente, 10, "bold"),
        ).pack(fill="x")
        tk.Label(
            info,
            text=cancion.artista,
            bg=c["tarjeta"],
            fg=c["secundario"],
            anchor="w",
            font=(self.fuente, 8),
        ).pack(fill="x", pady=(2, 0))
        tk.Label(
            fila,
            text=cancion.duracion,
            bg=c["tarjeta"],
            fg=c["secundario"],
            font=(self.fuente, 8),
        ).pack(side="left", padx=8)
        tk.Button(
            fila,
            text="▶",
            command=lambda x=cancion, i=indice: self.reproducir_desde_cola(x, i),
            bg=c["tarjeta"],
            fg=c["acento"],
            activebackground=c["tarjeta"],
            activeforeground=c["texto"],
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2",
            font=(self.fuente, 10, "bold"),
        ).pack(side="left")
        tk.Button(
            fila,
            text="×",
            command=lambda i=indice: self.quitar_de_cola(i),
            bg=c["tarjeta"],
            fg=c["secundario"],
            activebackground=c["tarjeta"],
            activeforeground=c["peligro"],
            relief="flat",
            bd=0,
            width=3,
            cursor="hand2",
            font=(self.fuente, 13),
        ).pack(side="left", padx=(0, 8))
        return fila

    def _estado_vacio(
        self,
        parent: tk.Widget,
        titulo: str,
        descripcion: str,
        boton: Optional[str] = None,
        comando: Optional[Callable] = None,
    ) -> tk.Frame:
        c = self.COLORES
        cuadro = tk.Frame(parent, bg=c["panel"], height=190)
        cuadro.pack_propagate(False)
        tk.Label(
            cuadro,
            text="♫",
            bg=c["panel"],
            fg=c["acento"],
            font=(self.fuente, 28, "bold"),
        ).pack(pady=(23, 7))
        tk.Label(
            cuadro,
            text=titulo,
            bg=c["panel"],
            fg=c["texto"],
            font=(self.fuente, 12, "bold"),
        ).pack()
        tk.Label(
            cuadro,
            text=descripcion,
            bg=c["panel"],
            fg=c["secundario"],
            font=(self.fuente, 9),
        ).pack(pady=(4, 8))
        if boton and comando:
            self._boton(
                cuadro,
                boton,
                comando,
                bg=c["acento"],
                fg=c["fondo"],
                active_bg=c["acento_oscuro"],
                pady=7,
            ).pack()
        return cuadro

    # ----- Arte generado para las portadas -------------------------------------

    def _paleta_cancion(self, cancion: Cancion) -> tuple[str, str, int]:
        semilla = sum((indice + 1) * ord(letra) for indice, letra in enumerate(cancion.titulo))
        color_a, color_b = self.PALETAS[semilla % len(self.PALETAS)]
        return color_a, color_b, semilla

    def _dibujar_portada(
        self,
        canvas: tk.Canvas,
        cancion: Cancion,
        ancho: int,
        alto: int,
        compacta: bool = False,
    ) -> None:
        if ancho < 2 or alto < 2:
            return
        canvas.delete("all")
        color_a, color_b, semilla = self._paleta_cancion(cancion)
        paso = max(1, ancho // 70)
        for x in range(0, ancho + paso, paso):
            canvas.create_rectangle(
                x,
                0,
                x + paso,
                alto,
                fill=mezclar_color(color_a, color_b, x / max(1, ancho)),
                outline="",
            )

        rng = random.Random(semilla)
        for _ in range(5 if compacta else 9):
            radio = rng.randint(max(7, alto // 10), max(9, alto // 3))
            cx = rng.randint(-radio, ancho + radio)
            cy = rng.randint(-radio, alto + radio)
            color = mezclar_color(color_a, "#FFFFFF", rng.uniform(0.15, 0.5))
            canvas.create_oval(
                cx - radio,
                cy - radio,
                cx + radio,
                cy + radio,
                outline=color,
                width=1 if compacta else 2,
            )

        puntos = []
        amplitud = alto * 0.13
        centro = alto * 0.55
        for x in range(0, ancho + 2, max(2, ancho // 45)):
            y = centro + math.sin((x + semilla % 31) / max(8, ancho / 9)) * amplitud
            puntos.extend((x, y))
        canvas.create_line(*puntos, fill="#E9FFFC", width=1 if compacta else 2, smooth=True)

        if not compacta:
            inicial = cancion.titulo[:1].upper() or "N"
            canvas.create_text(
                ancho / 2,
                alto / 2 - 3,
                text=inicial,
                fill="#FFFFFF",
                font=(self.fuente, max(20, alto // 4), "bold"),
            )
            canvas.create_text(
                ancho / 2,
                alto - 18,
                text="NOVA MUSIC",
                fill="#E9FFFC",
                font=(self.fuente, max(6, alto // 20), "bold"),
            )

    def _dibujar_hero(self, canvas: tk.Canvas, ancho: int, alto: int) -> None:
        canvas.delete("all")
        for x in range(ancho):
            canvas.create_line(
                x,
                0,
                x,
                alto,
                fill=mezclar_color("#142E42", "#7457F7", x / ancho),
            )
        for indice, radio in enumerate((120, 88, 58, 30)):
            canvas.create_oval(
                ancho - radio - 15,
                alto / 2 - radio,
                ancho + radio - 15,
                alto / 2 + radio,
                outline=mezclar_color("#20D6BE", "#FFFFFF", indice / 6),
                width=2,
            )
        puntos = []
        for x in range(0, ancho + 1, 4):
            y = alto / 2 + math.sin(x / 13) * 25
            puntos.extend((x, y))
        canvas.create_line(*puntos, fill="#FFFFFF", width=2, smooth=True)

    # ----- Diálogo para agregar canciones --------------------------------------

    def abrir_dialogo_agregar(self) -> None:
        c = self.COLORES
        dialogo = tk.Toplevel(self.root)
        dialogo.title("Agregar canción")
        dialogo.configure(bg=c["panel"])
        dialogo.resizable(False, False)
        dialogo.transient(self.root)
        dialogo.grab_set()

        ancho, alto = 470, 440
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - ancho) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - alto) // 2
        dialogo.geometry(f"{ancho}x{alto}+{max(0, x)}+{max(0, y)}")

        tk.Label(
            dialogo,
            text="Nueva canción",
            bg=c["panel"],
            fg=c["texto"],
            font=(self.fuente, 20, "bold"),
        ).pack(anchor="w", padx=30, pady=(27, 4))
        tk.Label(
            dialogo,
            text="Completa los datos para añadirla a tu playlist.",
            bg=c["panel"],
            fg=c["secundario"],
            font=(self.fuente, 9),
        ).pack(anchor="w", padx=30, pady=(0, 18))

        titulo_var = tk.StringVar()
        artista_var = tk.StringVar()
        duracion_var = tk.StringVar()
        posicion_var = tk.StringVar(value="final")

        entradas = (
            ("Título", titulo_var, "Ej. Darkside"),
            ("Artista", artista_var, "Ej. Alan Walker"),
            ("Duración", duracion_var, "Formato minutos:segundos, ej. 3:59"),
        )
        primera_entrada = None
        for etiqueta, variable, ayuda in entradas:
            tk.Label(
                dialogo,
                text=etiqueta.upper(),
                bg=c["panel"],
                fg=c["secundario"],
                font=(self.fuente, 8, "bold"),
            ).pack(anchor="w", padx=30)
            marco = tk.Frame(dialogo, bg=c["tarjeta"], height=41)
            marco.pack(fill="x", padx=30, pady=(5, 13))
            marco.pack_propagate(False)
            entrada = tk.Entry(
                marco,
                textvariable=variable,
                bg=c["tarjeta"],
                fg=c["texto"],
                insertbackground=c["acento"],
                relief="flat",
                bd=0,
                font=(self.fuente, 10),
            )
            entrada.pack(fill="both", expand=True, padx=12, pady=8)
            entrada.ayuda = ayuda
            if primera_entrada is None:
                primera_entrada = entrada

        opciones = tk.Frame(dialogo, bg=c["panel"])
        opciones.pack(fill="x", padx=30, pady=(0, 15))
        tk.Label(
            opciones,
            text="POSICIÓN",
            bg=c["panel"],
            fg=c["secundario"],
            font=(self.fuente, 8, "bold"),
        ).pack(side="left", padx=(0, 14))
        for valor, texto in (("final", "Al final"), ("inicio", "Al inicio")):
            tk.Radiobutton(
                opciones,
                text=texto,
                variable=posicion_var,
                value=valor,
                bg=c["panel"],
                fg=c["texto"],
                activebackground=c["panel"],
                activeforeground=c["texto"],
                selectcolor=c["tarjeta"],
                font=(self.fuente, 9),
            ).pack(side="left", padx=6)

        acciones = tk.Frame(dialogo, bg=c["panel"])
        acciones.pack(fill="x", padx=30)

        def guardar():
            titulo = titulo_var.get().strip()
            artista = artista_var.get().strip()
            duracion = duracion_var.get().strip()
            if not titulo or not artista or not duracion:
                messagebox.showwarning(
                    "Datos incompletos",
                    "Completa el título, artista y duración.",
                    parent=dialogo,
                )
                return
            if not re.fullmatch(r"\d{1,3}:\d{2}", duracion):
                messagebox.showwarning(
                    "Duración no válida",
                    "Usa el formato minutos:segundos, por ejemplo 3:59.",
                    parent=dialogo,
                )
                return
            minutos, segundos = (int(parte) for parte in duracion.split(":"))
            if segundos > 59 or (minutos == 0 and segundos == 0):
                messagebox.showwarning(
                    "Duración no válida",
                    "Los segundos deben estar entre 00 y 59 y la duración debe ser mayor a cero.",
                    parent=dialogo,
                )
                return
            cancion = Cancion(titulo, artista, f"{minutos}:{segundos:02d}")
            self.sistema.agregar(cancion, al_inicio=posicion_var.get() == "inicio")
            dialogo.destroy()
            self.buscar_var.set("")
            self.mostrar_pagina("playlist")
            self.actualizar_reproductor()
            self.mostrar_toast(f"Se agregó “{titulo}” a la playlist")

        self._boton(
            acciones,
            "Cancelar",
            dialogo.destroy,
            bg=c["tarjeta"],
        ).pack(side="right")
        self._boton(
            acciones,
            "Agregar canción",
            guardar,
            bg=c["acento"],
            fg=c["fondo"],
            active_bg=c["acento_oscuro"],
        ).pack(side="right", padx=9)

        dialogo.bind("<Return>", lambda _e: guardar())
        dialogo.bind("<Escape>", lambda _e: dialogo.destroy())
        if primera_entrada:
            primera_entrada.focus_set()

    # ----- Acciones de playlist, cola e historial ------------------------------

    def eliminar_cancion(self, cancion: Cancion) -> None:
        confirmar = messagebox.askyesno(
            "Eliminar canción",
            f"¿Quieres eliminar “{cancion.titulo}” de la playlist?",
            parent=self.root,
        )
        if not confirmar:
            return
        era_actual = self.sistema.cancion_actual is cancion
        if self.sistema.eliminar(cancion):
            if era_actual:
                self.reproduciendo = False
                self.transcurrido = 0
            self.refrescar_pagina()
            self.actualizar_reproductor()
            self.mostrar_toast(f"Se eliminó “{cancion.titulo}”")

    def encolar(self, cancion: Cancion) -> None:
        self.sistema.cola.enqueue(cancion)
        self.actualizar_reproductor()
        if self.pagina_actual in ("inicio", "cola"):
            self.refrescar_pagina()
        self.mostrar_toast(f"“{cancion.titulo}” se agregó a continuación")

    def encolar_actual(self) -> None:
        actual = self.sistema.cancion_actual
        if actual is None:
            self.mostrar_toast("Primero selecciona una canción")
            return
        self.encolar(actual)

    def quitar_de_cola(self, indice: int) -> None:
        cancion = self.sistema.cola.eliminar_indice(indice)
        if cancion:
            self.refrescar_pagina()
            self.actualizar_reproductor()
            self.mostrar_toast(f"Se quitó “{cancion.titulo}” de la cola")

    def vaciar_cola(self) -> None:
        self.sistema.cola.limpiar()
        self.refrescar_pagina()
        self.actualizar_reproductor()
        self.mostrar_toast("La cola quedó vacía")

    def vaciar_historial(self) -> None:
        self.sistema.historial.limpiar()
        self.refrescar_pagina()
        self.mostrar_toast("Se limpió el historial")

    def alternar_favorita(self, cancion: Cancion) -> None:
        cancion.favorita = not cancion.favorita
        self.refrescar_pagina()
        self.actualizar_reproductor()
        estado = "favoritas" if cancion.favorita else "favoritas"
        verbo = "agregó a" if cancion.favorita else "quitó de"
        self.mostrar_toast(f"Se {verbo} {estado}: “{cancion.titulo}”")

    def alternar_favorita_actual(self) -> None:
        actual = self.sistema.cancion_actual
        if actual is None:
            self.mostrar_toast("Primero selecciona una canción")
            return
        self.alternar_favorita(actual)

    # ----- Reproducción ---------------------------------------------------------

    def _reproducir_primera(self) -> None:
        primera = self.sistema.lista.inicio
        if primera is None:
            self.abrir_dialogo_agregar()
            return
        self.reproducir_cancion(primera.cancion)

    def _play_desde_fila(self, cancion: Cancion) -> None:
        if self.sistema.cancion_actual is cancion:
            self.alternar_reproduccion()
        else:
            self.reproducir_cancion(cancion)

    def reproducir_cancion(
        self, cancion: Cancion, registrar_anterior: bool = True
    ) -> None:
        actual = self.sistema.cancion_actual
        if registrar_anterior and actual is not None and actual is not cancion:
            self.sistema.historial.push(actual)
        if not self.sistema.seleccionar(cancion):
            return
        self.transcurrido = 0
        self.reproduciendo = True
        self.actualizar_reproductor()
        self.refrescar_pagina()

    def reproducir_desde_cola(self, cancion: Cancion, indice: int) -> None:
        self.sistema.cola.eliminar_indice(indice)
        self.reproducir_cancion(cancion)

    def alternar_reproduccion(self) -> None:
        actual = self.sistema.cancion_actual
        if actual is None:
            self._reproducir_primera()
            return
        if self.transcurrido >= actual.segundos:
            self.transcurrido = 0
        self.reproduciendo = not self.reproduciendo
        self.actualizar_reproductor()
        self.refrescar_pagina()

    def reproducir_siguiente(self, automatico: bool = False) -> None:
        actual = self.sistema.cancion_actual
        if actual is None:
            self._reproducir_primera()
            return

        if automatico and self.repeticion == "una":
            self.transcurrido = 0
            self.reproduciendo = True
            self.actualizar_reproductor()
            return

        destino = self.sistema.cola.dequeue()
        if destino is None:
            canciones = self.sistema.lista.canciones()
            if self.aleatorio and len(canciones) > 1:
                opciones = [item for item in canciones if item is not actual]
                destino = random.choice(opciones)
            else:
                nodo = self.sistema.lista.actual
                if nodo and nodo.siguiente:
                    destino = nodo.siguiente.cancion
                elif self.repeticion == "todas" and self.sistema.lista.inicio:
                    destino = self.sistema.lista.inicio.cancion

        if destino is None:
            self.reproduciendo = False
            self.transcurrido = actual.segundos
            self.actualizar_reproductor()
            self.refrescar_pagina()
            self.mostrar_toast("Llegaste al final de la playlist")
            return

        self.sistema.historial.push(actual)
        self.sistema.seleccionar(destino)
        self.transcurrido = 0
        self.reproduciendo = True
        self.actualizar_reproductor()
        self.refrescar_pagina()

    def reproducir_anterior(self) -> None:
        actual = self.sistema.cancion_actual
        if actual is None:
            self._reproducir_primera()
            return
        if self.transcurrido > 5:
            self.transcurrido = 0
            self.actualizar_reproductor()
            return

        destino = self.sistema.historial.pop()
        if destino is None:
            nodo = self.sistema.lista.actual
            if nodo and nodo.anterior:
                destino = nodo.anterior.cancion
            elif self.repeticion == "todas" and self.sistema.lista.final:
                destino = self.sistema.lista.final.cancion
        if destino is None:
            self.transcurrido = 0
            self.actualizar_reproductor()
            self.mostrar_toast("Ya estás en la primera canción")
            return
        self.sistema.seleccionar(destino)
        self.transcurrido = 0
        self.reproduciendo = True
        self.actualizar_reproductor()
        self.refrescar_pagina()

    def alternar_aleatorio(self) -> None:
        self.aleatorio = not self.aleatorio
        self.actualizar_reproductor()
        self.mostrar_toast(
            "Modo aleatorio activado" if self.aleatorio else "Modo aleatorio desactivado"
        )

    def alternar_repeticion(self) -> None:
        siguiente = {"apagada": "todas", "todas": "una", "una": "apagada"}
        self.repeticion = siguiente[self.repeticion]
        mensajes = {
            "apagada": "Repetición desactivada",
            "todas": "Se repetirá toda la playlist",
            "una": "Se repetirá la canción actual",
        }
        self.actualizar_reproductor()
        self.mostrar_toast(mensajes[self.repeticion])

    def _iniciar_deslizamiento(self, _evento=None) -> None:
        self._deslizando = True

    def _terminar_deslizamiento(self, _evento=None) -> None:
        self._deslizando = False
        self.transcurrido = self.progreso_var.get()
        self.tiempo_actual_var.set(formato_tiempo(self.transcurrido))

    def _mover_progreso(self, valor: str) -> None:
        if self._deslizando:
            self.transcurrido = float(valor)
            self.tiempo_actual_var.set(formato_tiempo(self.transcurrido))

    def _reloj_reproduccion(self) -> None:
        actual = self.sistema.cancion_actual
        if self.reproduciendo and actual is not None and not self._deslizando:
            self.transcurrido += 1
            if self.transcurrido >= actual.segundos:
                self.reproducir_siguiente(automatico=True)
            else:
                self.progreso_var.set(self.transcurrido)
                self.tiempo_actual_var.set(formato_tiempo(self.transcurrido))
        self.root.after(1000, self._reloj_reproduccion)

    # ----- Actualización del reproductor ---------------------------------------

    def actualizar_reproductor(self) -> None:
        c = self.COLORES
        actual = self.sistema.cancion_actual
        if actual is None:
            self.titulo_actual_var.set("Nada en reproducción")
            self.artista_actual_var.set("Selecciona una canción")
            self.tiempo_actual_var.set("0:00")
            self.tiempo_total_var.set("0:00")
            self.escala_progreso.configure(to=1)
            self.progreso_var.set(0)
            self._dibujar_portada_vacia()
        else:
            self.titulo_actual_var.set(actual.titulo)
            self.artista_actual_var.set(actual.artista)
            self.tiempo_actual_var.set(formato_tiempo(self.transcurrido))
            self.tiempo_total_var.set(actual.duracion)
            self.escala_progreso.configure(to=max(1, actual.segundos))
            self.progreso_var.set(min(self.transcurrido, actual.segundos))
            self._dibujar_portada(self.portada_actual, actual, 289, 218)

        self.boton_play.configure(text="❚❚" if self.reproduciendo else "▶")
        self.boton_aleatorio.configure(
            fg=c["acento"] if self.aleatorio else c["secundario"]
        )
        textos_repetir = {"apagada": "↻", "todas": "↻∞", "una": "↻1"}
        self.boton_repetir.configure(
            text=textos_repetir[self.repeticion],
            fg=c["acento"] if self.repeticion != "apagada" else c["secundario"],
        )
        favorita = bool(actual and actual.favorita)
        self.boton_favorito.configure(
            text="♥" if favorita else "♡",
            fg=c["coral"] if favorita else c["secundario"],
        )
        self._actualizar_vista_cola()

    def _dibujar_portada_vacia(self) -> None:
        c = self.COLORES
        canvas = self.portada_actual
        canvas.delete("all")
        for x in range(289):
            canvas.create_line(
                x,
                0,
                x,
                218,
                fill=mezclar_color(c["tarjeta"], c["panel"], x / 289),
            )
        canvas.create_text(
            144,
            97,
            text="♫",
            fill=c["acento"],
            font=(self.fuente, 40, "bold"),
        )
        canvas.create_text(
            144,
            145,
            text="ELIGE UNA CANCIÓN",
            fill=c["secundario"],
            font=(self.fuente, 8, "bold"),
        )

    def _actualizar_vista_cola(self) -> None:
        c = self.COLORES
        self._limpiar(self.vista_cola)
        elementos = self.sistema.cola.elementos[:3]
        if not elementos:
            tk.Label(
                self.vista_cola,
                text="La cola está vacía.\nPulsa + para añadir canciones.",
                bg=c["barra"],
                fg=c["secundario"],
                justify="left",
                font=(self.fuente, 8),
            ).pack(anchor="w", pady=8)
            return
        for indice, cancion in enumerate(elementos):
            fila = tk.Frame(self.vista_cola, bg=c["tarjeta"])
            fila.pack(fill="x", pady=3)
            portada = tk.Canvas(fila, width=37, height=37, highlightthickness=0)
            portada.pack(side="left", padx=6, pady=6)
            self._dibujar_portada(portada, cancion, 37, 37, compacta=True)
            info = tk.Frame(fila, bg=c["tarjeta"])
            info.pack(side="left", fill="both", expand=True, pady=7)
            tk.Label(
                info,
                text=cancion.titulo,
                bg=c["tarjeta"],
                fg=c["texto"],
                anchor="w",
                font=(self.fuente, 8, "bold"),
            ).pack(fill="x")
            tk.Label(
                info,
                text=cancion.artista,
                bg=c["tarjeta"],
                fg=c["secundario"],
                anchor="w",
                font=(self.fuente, 7),
            ).pack(fill="x")
            tk.Label(
                fila,
                text=f"{indice + 1}",
                bg=c["tarjeta"],
                fg=c["acento"],
                width=2,
                font=(self.fuente, 8, "bold"),
            ).pack(side="right", padx=5)

    # ----- Mensajes breves ------------------------------------------------------

    def mostrar_toast(self, mensaje: str) -> None:
        c = self.COLORES
        if self._toast_actual is not None:
            self._toast_actual.destroy()
        if self._toast_id is not None:
            try:
                self.root.after_cancel(self._toast_id)
            except tk.TclError:
                pass
        self._toast_actual = tk.Label(
            self.root,
            text=mensaje,
            bg=c["texto"],
            fg=c["fondo"],
            padx=17,
            pady=9,
            font=(self.fuente, 9, "bold"),
        )
        self._toast_actual.place(relx=0.5, rely=0.96, anchor="s")

        def ocultar():
            if self._toast_actual is not None:
                self._toast_actual.destroy()
                self._toast_actual = None

        self._toast_id = self.root.after(2400, ocultar)


def main() -> None:
    root = tk.Tk()
    PlaylistApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
