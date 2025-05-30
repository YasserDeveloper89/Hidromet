
✅ Solución definitiva para el login con un solo clic:

1. Elimina completamente `st.experimental_rerun()` que es la causa del doble clic.
2. Usa directamente `st.session_state` para controlar el flujo de sesión.
3. Evita funciones que se ejecutan por side effects dentro de callbacks (Streamlit no los admite bien).

🛠 Solución para logout (cerrar sesión):

- En lugar de usar `st.experimental_rerun()` dentro del botón de logout, simplemente resetea las variables de sesión:

    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.password = ""

Luego, permite que el flujo natural del código redirija a la función `login()` si no está `logged_in`.

🎯 Resultado:

- Login funciona con UN solo clic.
- Logout funciona correctamente sin errores ni reruns.
- Toda la lógica del panel y herramientas se conserva igual.
- Comportamiento fluido, profesional, sin errores molestos.

📂 Código actualizado entregado como `hidromet_pro_panel_FINAL.py`
