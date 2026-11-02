import json
import uuid

import streamlit as st
from streamlit_flow import (
    ManualLayout,
    StreamlitFlowEdge,
    StreamlitFlowNode,
    StreamlitFlowState,
    streamlit_flow,
)

STATE_KEY = "editor_nodos_estado"
COMPONENT_KEY = "editor_nodos_flujo"


def nuevo_nodo(texto, pos):
    return StreamlitFlowNode(
        id=f"nodo-{uuid.uuid4().hex[:8]}",
        pos=pos,
        data={"content": texto},
        source_position="right",
        target_position="left",
        draggable=True,
        selectable=True,
        connectable=True,
        deletable=True,
        style={
            "background": "#eef2ff",
            "color": "#1e1b4b",
            "border": "1px solid #818cf8",
            "borderRadius": "10px",
            "padding": "10px 14px",
            "fontSize": "13px",
            "width": "240px",
        },
    )


def nueva_conexion(origen, destino, etiqueta=""):
    return StreamlitFlowEdge(
        id=f"conexion-{uuid.uuid4().hex[:8]}",
        source=origen,
        target=destino,
        edge_type="smoothstep",
        animated=True,
        deletable=True,
        label=etiqueta,
        label_show_bg=True,
        label_style={"fill": "#4338ca", "fontSize": "11px"},
        label_bg_style={"fill": "#ffffff"},
        style={"stroke": "#6366f1", "strokeWidth": 2},
        marker_end={"type": "arrowclosed", "color": "#6366f1"},
    )


def ejemplo():
    inicio = nuevo_nodo("Inicio", (40, 40))
    decision = nuevo_nodo("¿Hay stock?", (360, 40))
    si = nuevo_nodo("Registrar venta", (680, 40))
    no = nuevo_nodo("Pedir al proveedor", (680, 200))
    return StreamlitFlowState(
        [inicio, decision, si, no],
        [
            nueva_conexion(inicio.id, decision.id),
            nueva_conexion(decision.id, si.id, "Sí"),
            nueva_conexion(decision.id, no.id, "No"),
        ],
    )


def posicion_siguiente(estado):
    total = len(estado.nodes)
    return (60 + (total % 3) * 280, 60 + (total // 3) * 170)


def main():
    st.set_page_config(page_title="Editor de nodos", layout="wide")

    if STATE_KEY not in st.session_state:
        st.session_state[STATE_KEY] = ejemplo()

    st.title("Editor de nodos")
    st.caption("Arrastrá un nodo para moverlo. Tirá desde el conector derecho de un nodo hacia otro para conectarlos. Click derecho sobre un nodo o el lienzo abre el menú. Todo queda en esta sesión; no modifica la base de datos.")

    estado = st.session_state[STATE_KEY]

    with st.sidebar:
        st.header("Agregar")
        texto = st.text_input("Texto del nodo", "Nueva decisión")
        if st.button("Agregar nodo", width="stretch"):
            nodo = nuevo_nodo(texto, posicion_siguiente(estado))
            st.session_state[STATE_KEY] = StreamlitFlowState(
                estado.nodes + [nodo], estado.edges
            )
            st.rerun()

        st.divider()
        st.header("Sesión")
        if st.button("Cargar ejemplo", width="stretch"):
            st.session_state[STATE_KEY] = ejemplo()
            st.rerun()
        if st.button("Borrar todo", width="stretch"):
            st.session_state[STATE_KEY] = StreamlitFlowState([], [])
            st.rerun()

        seleccion = estado.selected_id
        nodo_sel = next((n for n in estado.nodes if n.id == seleccion), None)
        arista_sel = next((e for e in estado.edges if e.id == seleccion), None)

        if nodo_sel is not None:
            st.divider()
            st.header("Nodo seleccionado")
            contenido = st.text_area(
                "Contenido", value=nodo_sel.data.get("content", "")
            )
            if st.button("Guardar contenido", width="stretch"):
                nodo_sel.data["content"] = contenido
                st.session_state[STATE_KEY] = estado
                st.rerun()

        if arista_sel is not None:
            st.divider()
            st.header("Conexión seleccionada")
            etiqueta = st.text_input("Etiqueta", value=arista_sel.label)
            if st.button("Guardar etiqueta", width="stretch"):
                datos = arista_sel.asdict()
                datos["label"] = etiqueta
                nueva = StreamlitFlowEdge.from_dict(datos)
                st.session_state[STATE_KEY] = StreamlitFlowState(
                    estado.nodes,
                    [nueva if e.id == arista_sel.id else e for e in estado.edges],
                )
                st.rerun()

        st.divider()
        datos_json = json.dumps(
            {
                "nodes": [n.asdict() for n in estado.nodes],
                "edges": [e.asdict() for e in estado.edges],
            },
            indent=2,
            ensure_ascii=False,
        )
        st.download_button(
            "Descargar JSON",
            datos_json,
            "nodos.json",
            "application/json",
            width="stretch",
        )
        archivo = st.file_uploader("Cargar JSON", type=["json"])
        if archivo is not None and st.button("Aplicar JSON", width="stretch"):
            try:
                cargado = json.load(archivo)
                nodos = [StreamlitFlowNode.from_dict(n) for n in cargado["nodes"]]
                aristas = [StreamlitFlowEdge.from_dict(e) for e in cargado["edges"]]
                st.session_state[STATE_KEY] = StreamlitFlowState(nodos, aristas)
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudo cargar el JSON: {exc}")

    estado = streamlit_flow(
        COMPONENT_KEY,
        st.session_state[STATE_KEY],
        height=700,
        fit_view=True,
        show_controls=True,
        show_minimap=True,
        allow_new_edges=True,
        animate_new_edges=True,
        get_node_on_click=True,
        get_edge_on_click=True,
        enable_node_menu=True,
        enable_edge_menu=True,
        enable_pane_menu=True,
        layout=ManualLayout(),
        hide_watermark=True,
    )
    st.session_state[STATE_KEY] = estado

    st.caption(f"{len(estado.nodes)} nodos · {len(estado.edges)} conexiones")

    with st.expander("Ver JSON del grafo"):
        st.json(
            {
                "nodes": [n.asdict() for n in estado.nodes],
                "edges": [e.asdict() for e in estado.edges],
            }
        )


main()
