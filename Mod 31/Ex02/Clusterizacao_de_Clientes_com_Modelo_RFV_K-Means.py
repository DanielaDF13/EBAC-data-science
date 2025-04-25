import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from kneed import KneeLocator

st.set_page_config(page_title="Clusterização RFV com K-Means", layout="wide")

st.title("📊 Clusterização de Clientes com Modelo RFV + K-Means")

st.markdown("Este aplicativo permite segmentar clientes com base nos seus comportamentos de compra utilizando o modelo RFV (Recência, Frequência, Valor) e algoritmo de clusterização K-Means.")

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df['DiaCompra'] = pd.to_datetime(df['DiaCompra'])
    return df

uploaded_file = st.sidebar.file_uploader("📁 Faça upload do arquivo CSV", type="csv")

if uploaded_file:
    df = load_data(uploaded_file)

    required_cols = ['ID_cliente', 'CodigoCompra', 'DiaCompra', 'ValorTotal']
    if not all(col in df.columns for col in required_cols):
        st.error("❌ O arquivo deve conter as colunas: ID_cliente, CodigoCompra, DiaCompra, ValorTotal")
    else:
        st.subheader("📄 Dados brutos")
        st.dataframe(
            df.head(20).style
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]),
            use_container_width=True,
            height=400
        )

        # Construção do RFV
        data_base = df['DiaCompra'].max() + pd.Timedelta(days=1)

        rfv = df.groupby('ID_cliente').agg({
            'DiaCompra': lambda x: (data_base - x.max()).days,
            'CodigoCompra': 'nunique',
            'ValorTotal': 'sum'
        }).reset_index()

        rfv.columns = ['ID_cliente', 'Recencia', 'Frequencia', 'Valor']
        rfv[['Recencia', 'Frequencia', 'Valor']] = rfv[['Recencia', 'Frequencia', 'Valor']].round(2)

        st.subheader("📊 Tabela RFV")
        st.markdown("A tabela RFV contém as métricas calculadas para cada cliente:\n- **Recência**: Dias desde a última compra.\n- **Frequência**: Quantidade de compras realizadas.\n- **Valor**: Total gasto pelo cliente.")
        st.dataframe(
            rfv.head(20).style
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]),
            use_container_width=True,
            height=400
        )

        # Normalização
        scaler = StandardScaler()
        rfv_scaled = scaler.fit_transform(rfv[['Recencia', 'Frequencia', 'Valor']])

        # Método do cotovelo
        inertias = []
        k_values = list(range(1, 11))

        for k_test in k_values:
            kmeans_test = KMeans(n_clusters=k_test, random_state=415)
            kmeans_test.fit(rfv_scaled)
            inertias.append(kmeans_test.inertia_)

        knee = KneeLocator(k_values, inertias, curve="convex", direction="decreasing")
        k_sugerido = knee.knee or 4

        st.subheader("📉 Método do cotovelo - Melhor número de clusters")
        st.markdown("O método do cotovelo ajuda a identificar o número ideal de clusters. O ponto onde a curva começa a 'dobrar' é considerado o melhor valor para K.")
        fig_elbow, ax_elbow = plt.subplots()
        ax_elbow.plot(k_values, inertias, 'bo-')
        ax_elbow.axvline(k_sugerido, color='red', linestyle='--', label=f"Sugerido: K = {k_sugerido}")
        ax_elbow.set_xlabel("Número de Clusters (K)")
        ax_elbow.set_ylabel("Inércia")
        ax_elbow.set_title("Método do cotovelo")
        ax_elbow.legend()
        st.pyplot(fig_elbow)

        st.info(f"🔎 K sugerido pelo método do cotovelo: **{k_sugerido}**")

        # Slider na sidebar
        k = st.sidebar.slider("🔢 Selecione o número de clusters (K)", min_value=2, max_value=10, value=k_sugerido)

        # Aplicar KMeans
        kmeans = KMeans(n_clusters=k, random_state=415)
        rfv['Cluster'] = kmeans.fit_predict(rfv_scaled)

        st.subheader("📁 Clientes com seus respectivos clusters")
        st.dataframe(
            rfv.drop(columns=['ID_cliente']).head(20).style
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]),
            use_container_width=True,
            height=500
        )

        # Botão de download
        csv_data = rfv.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar dados com clusters (CSV)",
            data=csv_data,
            file_name='clientes_clusterizados.csv',
            mime='text/csv'
        )

        # Recência vs Valor
        st.subheader("📈 Visualização dos Clusters (Recência vs Valor)")
        st.markdown("Gráfico de dispersão mostrando como os clusters se distribuem em relação à **recência** e ao **valor** gasto.")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=rfv, x='Recencia', y='Valor', hue='Cluster', palette='Set2', ax=ax)
        ax.set_title("Clusters baseados em Recência e Valor")
        ax.set_xlabel("Recência")
        ax.set_ylabel("Valor")
        st.pyplot(fig)

        # Frequência vs Valor
        st.subheader("📈 Visualização dos Clusters (Frequência vs Valor)")
        st.markdown("Gráfico de dispersão mostrando como os clusters se distribuem em relação à **frequência de compras** e ao **valor** gasto.")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=rfv, x='Frequencia', y='Valor', hue='Cluster', palette='Set2', ax=ax2)
        ax2.set_title("Clusters baseados em Frequência e Valor")
        ax2.set_xlabel("Frequência")
        ax2.set_ylabel("Valor")
        st.pyplot(fig2)

        # Resumo por cluster
        st.subheader("📋 Resumo por Cluster")
        st.markdown("Aqui está o valor médio de **Recência**, **Frequência** e **Valor** para cada cluster identificado.")
        resumo = rfv.groupby('Cluster')[['Recencia', 'Frequencia', 'Valor']].mean().round(2)
        st.dataframe(
            resumo.style
              .set_properties(**{'text-align': 'center'})
              .set_table_styles([{'selector': 'th', 'props': [('text-align', 'center')]}]),
            use_container_width=True
        )

