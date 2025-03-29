
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

st.set_page_config(page_title="La Cucharita de Oro - Créditos", layout="centered")
st.markdown("<h1 style='text-align: center;'>💰 La Cucharita de Oro - Créditos</h1>", unsafe_allow_html=True)

capital = 500000
interes = 0.15
total_pagar = capital * (1 + interes)
comision_socio = capital * 0.02
ganancia_neta = total_pagar - capital - comision_socio

archivo_excel = "historial_creditos_pagos_flexibles.xlsx"

if os.path.exists(archivo_excel):
    df_registros = pd.read_excel(archivo_excel)
else:
    df_registros = pd.DataFrame(columns=[
        'Cliente', 'Cédula', 'Celular', 'Correo',
        'Fecha', 'Valor del préstamo', 'Cuotas', 'Cuotas pagadas', 'Cuota mensual',
        'Total pagado', 'Saldo restante',
        'Comisión socio', 'Ganancia neta', 'Total a pagar'
    ])

menu = st.sidebar.radio("Menú Principal", ["📋 Registro de Clientes", "💵 Registro de Pagos", "🔍 Consulta", "📊 Reportes"])


if menu == "📋 Registro de Clientes":
    st.subheader("📝 Registrar nuevo préstamo")
    cliente = st.text_input("Nombre del cliente")
    cedula = st.text_input("Cédula")
    celular = st.text_input("Celular")
    correo = st.text_input("Correo (opcional)")
    valor_prestamo = st.number_input("Valor del préstamo", min_value=100000, step=50000)
    fecha = st.date_input("Fecha del préstamo", value=datetime.today())
    cuotas = st.selectbox("Número de cuotas", [1, 2, 3, 4])

    if st.button("Registrar préstamo"):
        if not cliente or not cedula or not celular or not valor_prestamo:
            st.warning("⚠️ Por favor, completa todos los campos obligatorios.")
        else:
            interes = 0.15
            total_pagar = valor_prestamo * (1 + interes)
            comision_socio = valor_prestamo * 0.02
            ganancia_neta = total_pagar - valor_prestamo - comision_socio
            cuota_mensual = round(total_pagar / cuotas, 2)

            registro = {
                'Cliente': cliente,
                'Cédula': cedula,
                'Celular': celular,
                'Correo': correo,
                'Fecha': fecha.strftime("%Y-%m-%d"),
                'Valor del préstamo': valor_prestamo,
                'Cuotas': cuotas,
                'Cuotas pagadas': 0,
                'Cuota mensual': cuota_mensual,
                'Total pagado': 0,
                'Saldo restante': total_pagar,
                'Comisión socio': comision_socio,
                'Ganancia neta': ganancia_neta,
                'Total a pagar': total_pagar
            }

            df_registros = pd.concat([df_registros, pd.DataFrame([registro])], ignore_index=True)
            df_registros.to_excel(archivo_excel, index=False)
            st.success("✅ Cliente registrado exitosamente.")
            st.write(registro)


elif menu == "💵 Registro de Pagos":
    st.subheader("💵 Registrar pago de cuotas")
    if not df_registros.empty:
        cedula_pago = st.text_input("Buscar cliente por cédula")
        cliente_df = df_registros[df_registros['Cédula'].astype(str) == cedula_pago]
        if not cliente_df.empty:
            st.write(cliente_df[['Cliente', 'Cuotas', 'Cuotas pagadas', 'Cuota mensual', 'Saldo restante']])
            pago_opcion = st.radio("¿Cómo desea registrar el pago?", ["Por número de cuotas", "Por monto exacto"])
            index = cliente_df.index[0]

            if pago_opcion == "Por número de cuotas":
                cuotas_a_pagar = st.number_input("¿Cuántas cuotas está pagando?", min_value=1, max_value=10, step=1)
                if st.button("Registrar pago por cuotas"):
                    cuotas_restantes = df_registros.at[index, 'Cuotas'] - df_registros.at[index, 'Cuotas pagadas']
                    cuotas_registradas = min(cuotas_a_pagar, cuotas_restantes)
                    df_registros.at[index, 'Cuotas pagadas'] += cuotas_registradas
                    df_registros.at[index, 'Total pagado'] = df_registros.at[index, 'Cuotas pagadas'] * df_registros.at[index, 'Cuota mensual']
                    df_registros.at[index, 'Saldo restante'] = df_registros.at[index, 'Total a pagar'] - df_registros.at[index, 'Total pagado']
                    df_registros.to_excel(archivo_excel, index=False)
                    st.success(f"✅ Se registraron {cuotas_registradas} cuota(s) pagada(s).")
            else:
                monto = st.number_input("Monto exacto pagado", min_value=0.0, step=1000.0)
                if st.button("Registrar pago por monto"):
                    pago_total = df_registros.at[index, 'Total pagado'] + monto
                    saldo_total = df_registros.at[index, 'Total a pagar']
                    pago_final = min(pago_total, saldo_total)
                    cuotas_estimadas = int(pago_final / df_registros.at[index, 'Cuota mensual'])
                    df_registros.at[index, 'Cuotas pagadas'] = min(cuotas_estimadas, df_registros.at[index, 'Cuotas'])
                    df_registros.at[index, 'Total pagado'] = pago_final
                    df_registros.at[index, 'Saldo restante'] = saldo_total - pago_final
                    df_registros.to_excel(archivo_excel, index=False)
                    st.success("✅ Pago por monto registrado correctamente.")
        else:
            st.info("No se encontró ningún cliente con esa cédula.")
    else:
        st.info("Aún no hay registros.")

elif menu == "🔍 Consulta":
    st.subheader("🔍 Buscar cliente por nombre o cédula")
    if not df_registros.empty:
        filtro = st.text_input("Escriba nombre o cédula")
        if filtro:
            resultado = df_registros[df_registros['Cliente'].str.lower().str.contains(filtro.lower()) |
                                     df_registros['Cédula'].astype(str).str.contains(filtro)]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("No se encontraron coincidencias.")
    else:
        st.info("No hay datos registrados.")

elif menu == "📊 Reportes":
    st.subheader("📊 Reporte General")
    if not df_registros.empty:
        st.dataframe(df_registros)
        st.write(f"👥 Total clientes registrados: {len(df_registros)}")
        st.write(f"💸 Ganancia neta total: ${df_registros['Ganancia neta'].sum():,.0f}")
        st.write(f"🤝 Comisión total pagada: ${df_registros['Comisión socio'].sum():,.0f}")
        st.write(f"💰 Total recaudado: ${df_registros['Total pagado'].sum():,.0f}")
        st.write(f"📉 Saldo total pendiente: ${df_registros['Saldo restante'].sum():,.0f}")
        
        buffer = io.BytesIO()
        try:
            df_registros.to_excel(buffer, index=False, engine='xlsxwriter')
        except:
            try:
                df_registros.to_excel(buffer, index=False, engine='openpyxl')
            except:
                st.warning("⚠️ No se pudo generar el archivo Excel. Instale 'openpyxl' o 'xlsxwriter'.")
                buffer = None

        if buffer:
            buffer.seek(0)
            st.download_button("⬇️ Descargar Excel completo",
                               data=buffer,
                               file_name="historial_creditos_pagos_flexibles.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Aún no hay datos.")
