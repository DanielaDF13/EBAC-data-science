




# Imports
import pandas            as pd
import streamlit         as st


# Função para ler os dados
@st.cache_data
def load_data(file_data):
    return pd.read_csv(file_data, sep=';')

# Função para filtrar baseado na multiseleção de categorias
@st.cache_resource
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função principal da aplicação    
def main():

    # Configuração inicial da página da aplicação
    st.set_page_config(page_title = 'Telemarketing analisys', \
        page_icon = '../img/telmarketing_icon.png',
        layout="wide",
        initial_sidebar_state='expanded'
    )

    bank_raw = load_data('../data/input/bank-additional-full-40.csv')
    bank = bank_raw.copy()

   
    with st.sidebar.form(key='my_form'):
            # IDADES
            max_age = int(bank.age.max())
            min_age = int(bank.age.min())
            idades = st.slider(label='Idade', 
                                        min_value = min_age,
                                        max_value = max_age, 
                                        value = (min_age, max_age),
                                        step = 1)
            # DURAÇÃO
            max_duration = int(bank.duration.max())
            min_duration = int(bank.duration.min())
            duracao = st.slider(label='Duração', 
                                        min_value = min_duration,
                                        max_value = max_duration, 
                                        value = (min_duration, max_duration),
                                        step = 1)


            # PROFISSÕES
            jobs_list = bank.job.unique().tolist()
            jobs_list.append('all')
            jobs_selected =  st.multiselect("Profissão", jobs_list, ['all'])

            # ESTADO CIVIL
            marital_list = bank.marital.unique().tolist()
            marital_list.append('all')
            marital_selected =  st.multiselect("Estado civil", marital_list, ['all'])

            # DEFAULT?
            default_list = bank.default.unique().tolist()
            default_list.append('all')
            default_selected =  st.multiselect("Default", default_list, ['all'])

            
            # TEM FINANCIAMENTO IMOBILIÁRIO?
            housing_list = bank.housing.unique().tolist()
            housing_list.append('all')
            housing_selected =  st.multiselect("Tem financiamento imob?", housing_list, ['all'])

            
            # TEM EMPRÉSTIMO?
            loan_list = bank.loan.unique().tolist()
            loan_list.append('all')
            loan_selected =  st.multiselect("Tem empréstimo?", loan_list, ['all'])

            
            # MEIO DE CONTATO?
            contact_list = bank.contact.unique().tolist()
            contact_list.append('all')
            contact_selected =  st.multiselect("Meio de contato", contact_list, ['all'])

            
            # MÊS DO CONTATO
            month_list = bank.month.unique().tolist()
            month_list.append('all')
            month_selected =  st.multiselect("Mês do contato", month_list, ['all'])

            
            # DIA DA SEMANA
            day_of_week_list = bank.day_of_week.unique().tolist()
            day_of_week_list.append('all')
            day_of_week_selected =  st.multiselect("Dia da semana", day_of_week_list, ['all'])

            # POUTCOME?
            poutcome_list = bank.poutcome.unique().tolist()
            poutcome_list.append('all')
            poutcome_selected = st.multiselect("Poutcome",poutcome_list,['all'])

            # YES?
            y_list = bank.y.unique().tolist()
            y_list.append('all')
            y_selected = st.multiselect("Yes",y_list,['all'])
                    
            # encadeamento de métodos para filtrar a seleção
            bank = (bank.query("age >= @idades[0] and age <= @idades[1]")
                        .query("duration >= @duracao[0] and duration <= @duracao[1]")
                        .pipe(multiselect_filter, 'job', jobs_selected)
                        .pipe(multiselect_filter, 'marital', marital_selected)
                        .pipe(multiselect_filter, 'default', default_selected)
                        .pipe(multiselect_filter, 'housing', housing_selected)
                        .pipe(multiselect_filter, 'loan', loan_selected)
                        .pipe(multiselect_filter, 'contact', contact_selected)
                        .pipe(multiselect_filter, 'month', month_selected)
                        .pipe(multiselect_filter, 'day_of_week', day_of_week_selected)
                        .pipe(multiselect_filter, 'poutcome', poutcome_selected)
                        .pipe(multiselect_filter, 'y', y_selected)
            )


            submit_button = st.form_submit_button(label='Aplicar')
    
    # SELECIONA O TIPO DE GRÁFICO
    graph_type = st.radio('Tipo de gráfico:', ('Filtrado', 'Não-filtrado'))
    if graph_type == 'Filtrado':
        
        # Dados filtrados
        st.write('## Filtrado')
        st.write(bank.head())

    else:
        # Dados não filtrados
        st.write('## Não-filtrado')
        st.write(bank_raw.head())

if __name__ == '__main__':
	main()
