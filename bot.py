import pyautogui
from time import sleep
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from langchain_google_genai import ChatGoogleGenerativeAI
import pyperclip
import os
import ast

# Carrega as variáveis de ambiente do arquivo .env


# --- Configuração do Modelo de Linguagem (LLM) ---
# Pega a chave da API do Google do arquivo .env
try:
    chave = st.secrets('GOOGLE_API_KEY')
except TypeError:
    from dotenv import load_dotenv
    load_dotenv()
    chave = os.getenv('GOOGLE_API_KEY')

# Validação para garantir que a chave da API foi carregada
if not chave:
    st.error("A chave 'google_api_key' não foi encontrada no seu arquivo .env. Por favor, adicione-a.")
    st.stop()

llm = ChatGoogleGenerativeAI(
    temperature=0.3,
    model='gemini-2.5-flash', # Usando um modelo mais recente
    api_key=chave
)

# --- PROMPT ATUALIZADO (RESPOSTA ÚNICA) ---
prompt = f'''
Atue como um ajudante especial, com 50 anos de experiência em todas as áreas de exatas e metodologia. Sua voz deve ser a de um adolescente de 15 anos, escrevendo de forma **simples, direta e rápida**, sem gírias.

### Tarefa Principal
Sua tarefa é analisar a pergunta no texto de entrada e determinar se é uma **questão de múltipla escolha** ou uma **questão aberta**.

---
### TIPO 1: Questão de Múltipla Escolha
Se a pergunta tiver alternativas como A), B), C), D), E), sua tarefa é identificar a **única** alternativa correta.

**Formato de Saída OBRIGATÓRIO para Múltipla Escolha:**
Sua resposta DEVE começar com a tag `CORRETA:` seguida por uma lista Python contendo **apenas a letra** da alternativa correta (em maiúsculo).
- Exemplo: `CORRETA: ['B']`
**NÃO DÊ EXPLICAÇÕES. APENAS A TAG E A LISTA COM A LETRA.**

---
### TIPO 2: Questão Aberta (Dissertativa)
Se a pergunta NÃO for de múltipla escolha, gere uma **única resposta completa e bem explicada**.

**Conteúdo da Resposta:**
- **Para Questões Gerais:** Dê a resposta mais direta e completa possível, incluindo qualquer informação complementar relevante diretamente no texto principal.
- **Para Questões de História da Ciência:** Se a pergunta for sobre isso, sua resposta DEVE explicar **por que o modelo de Copérnico, apesar de importante, não foi revolucionário de imediato por não ter novas observações.**

**Formato de Saída OBRIGATÓRIO para Questões Abertas:**
A resposta deve ser um único bloco de texto. **NÃO USE O SEPARADOR `||SEP||`**.
- Exemplo: `O modelo de Copérnico não foi aceito de cara porque ele não trouxe nenhuma prova nova vinda de observações do céu. Ele só organizou o que já se sabia de um jeito diferente, com o Sol no centro.`

---
### Regras Gerais
- **Limpeza:** Ignore lixo no texto de entrada (botões, menus, etc.).
- **Silêncio:** Se a entrada for inválida, não escreva nada.
'''

# --- Configurações Iniciais ---
pyautogui.PAUSE = 0.5

# --- Interface do Streamlit ---
st.set_page_config(layout="wide")
st.title('🤖 Robô de Automação EI v7.8 (Lógica If/Elif)')
st.markdown('---')

col1, col2 = st.columns(2)

with col1:
    st.info("ℹ️ Preencha suas credenciais e selecione a matéria para iniciar.")
    email = st.text_input('Digite seu e-mail:', key='email_input').lower().strip()
    senha = st.text_input('Digite sua senha:', type='password', key='password_input')
    areas = st.selectbox('Selecione a área:', ['Química', 'Biologia', 'Física'], key='area_select')

if 'indice_area' not in st.session_state:
    st.session_state.indice_area = 0

if areas == 'Química':
    st.session_state.indice_area = 0
elif areas == 'Biologia':
    st.session_state.indice_area = 1
elif areas == 'Física':
    st.session_state.indice_area = 2

# --- Bloco de Estilo CSS para os "Quadrados" ---
st.markdown("""
<style>
.answer-box {
    border: 2px solid;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    background-color: #f0f2f6;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease-in-out;
}
.answer-box:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
.answer-box-1 { border-color: #008CBA; } /* Azul */
.answer-box h3 {
    margin-top: 0;
    font-size: 1.2em;
    color: #333;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)


if st.button('🚀 Iniciar Automação'):
    if not email or not senha:
        st.warning('Por favor, preencha o e-mail e a senha.')
    else:
        try:
            web = webdriver.Chrome()
            web.get('https://portal.escoladainteligencia.com.br/login')
            web.maximize_window()
            with st.spinner('Abrindo o portal no navegador...'):
                sleep(5)
            st.success('Portal aberto com sucesso! ✅')

            with st.spinner('Realizando login...'):
                WebDriverWait(web, 10).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(email)
                web.find_element(By.NAME, 'password').send_keys(senha)
                try:
                    web.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
                except:
                    pyautogui.click('entrar.png')
                sleep(5)

            with st.spinner('Navegando pela plataforma...'):
                sleep(3)
                pyautogui.click(100, 400)
                st.info("Tentando fechar o pop-up inicial...")
                
                pyautogui.scroll(-1000)
                sleep(1)
                pyautogui.click('conteudo.png')
                sleep(2)
                pyautogui.scroll(-700)
            st.success('Navegação inicial concluída! ✅')

            with st.spinner('Localizando a matéria e a próxima tarefa...'):
                lista_areas = ['quimica.png', 'biologia.png', 'fisica.png']
                localizar_objetivo = pyautogui.locateCenterOnScreen(lista_areas[st.session_state.indice_area])
                
                if localizar_objetivo:
                    soma1 = localizar_objetivo[0] + 270
                    soma2 = localizar_objetivo[1] + 10
                    pyautogui.click(soma1, soma2)
                else:
                    st.error('Matéria não localizada na tela! ❌')
                    st.stop()

                sleep(12)
                
                unidade_nao_feita = pyautogui.locateCenterOnScreen('unidade_n_feita.png')
                pyautogui.click(unidade_nao_feita)
                
                sleep(3)
                
                st.info("Iniciando busca pela próxima atividade não feita...")
                atividade_encontrada = False
                tentativas = 0
                max_tentativas = 15

                while not atividade_encontrada and tentativas < max_tentativas:
                    st.write(f"Tentativa {tentativas + 1}/{max_tentativas}...")
                    try:
                        localizacao_atvd = pyautogui.locateCenterOnScreen('atividade_n_feita.png')
                        st.success("Imagem da atividade encontrada!")
                        pyautogui.click(localizacao_atvd)
                        atividade_encontrada = True
                    except pyautogui.ImageNotFoundException:
                        pyautogui.scroll(-600)
                        sleep(0.3)
                    
                    tentativas += 1

                if not atividade_encontrada:
                    st.error('Nenhuma atividade não concluída foi encontrada após rolar toda a página. ❌')
                    st.stop()
                else:
                    sleep(3)
                    try:
                        pyautogui.click('image.png')
                    except pyautogui.ImageNotFoundException:
                        st.warning("A segunda imagem ('image.png') não foi encontrada. Continuando...")


            st.success('Tarefa localizada e aberta! ✅')

            with st.spinner('Copiando pergunta e gerando respostas com IA...'):
                sleep(3)
                pyautogui.mouseDown(button='left')
                pyautogui.moveTo(200, 200, duration=1.0)
                pyautogui.moveTo(1800, 900, duration=1.5)
                pyautogui.mouseUp(button='left')
                pyautogui.hotkey('ctrl', 'c')
                sleep(1)
                texto_copiado = pyperclip.paste()
                
                response_completa = llm.invoke(f"{prompt} {texto_copiado}").content.strip()
                
                is_multiple_choice = False
                
                with col2:
                    if response_completa.startswith('CORRETA:'):
                        is_multiple_choice = True
                        st.success("Questão de múltipla escolha detectada!")
                        letra_correta_da_ia = '' # Inicializa para o caso de erro
                        nome_imagem_alternativa = ''
                        try:
                            lista_str = response_completa.split('CORRETA:')[1].strip()
                            letras_corretas = ast.literal_eval(lista_str)

                            sleep(2)
                            if letras_corretas:
                                letra_correta_da_ia = letras_corretas[0] # Ex: 'B'
                                st.info(f"IA identificou a alternativa '{letra_correta_da_ia}'. Tentando clicar na imagem correspondente...")
                                
                                # --- LÓGICA DE CLIQUE COM IF/ELIF E CONFIDENCE ---
                                localizacao = None
                                if letra_correta_da_ia == 'A':
                                    localizacao = pyautogui.locateCenterOnScreen('A.png', confidence=0.8)
                                elif letra_correta_da_ia == 'B':
                                    localizacao = pyautogui.locateCenterOnScreen('B.png', confidence=0.8)
                                elif letra_correta_da_ia == 'C':
                                    localizacao = pyautogui.locateCenterOnScreen('C.png', confidence=0.8)
                                elif letra_correta_da_ia == 'D':
                                    localizacao = pyautogui.locateCenterOnScreen('D.png', confidence=0.8)

                                if localizacao:
                                    pyautogui.click(localizacao)
                                    st.success(f"Alternativa '{letra_correta_da_ia}' clicada com sucesso!")
                                else:
                                    # Gera a exceção para ser capturada pelo bloco 'except'
                                    nome_imagem_alternativa = f"{letra_correta_da_ia}.png"
                                    raise pyautogui.ImageNotFoundException
                            else:
                                st.warning("O modelo indicou múltipla escolha, mas não retornou uma alternativa.")
                        except pyautogui.ImageNotFoundException:
                             st.error(f"Falha ao clicar na alternativa. Não foi possível encontrar a imagem '{nome_imagem_alternativa}' na tela.")
                        except Exception as e:
                            st.error(f"Ocorreu um erro ao tentar clicar na alternativa '{letra_correta_da_ia}'. Erro: {e}")

                    elif response_completa:
                        st.success('Resposta gerada com sucesso!')
                        pyperclip.copy(response_completa)
                        st.info('A resposta foi copiada para a área de transferência.')
                        st.markdown(f"""
                        <div class="answer-box answer-box-1">
                            <h3>🤖 Resposta (Para Colar)</h3>
                            <p>{response_completa}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning('O modelo não retornou uma resposta válida.')

            if not is_multiple_choice and response_completa:
                with st.spinner('Colando a resposta na plataforma...'):
                    try:
                        wait = WebDriverWait(web, 10)
                        caixa_de_texto = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.jodit-wysiwyg')))
                        caixa_de_texto.click()
                        sleep(1)
                        pyautogui.hotkey('ctrl', 'v')
                        sleep(1)
                    except TimeoutException:
                        st.error("Não foi possível encontrar o campo de texto na página para colar a resposta.")
            
            st.balloons()
            st.success('🎉 Automação concluída com sucesso! 🎉')

        except pyautogui.ImageNotFoundException as img_err:
            st.error(f'Erro Crítico: A imagem {img_err.name} não foi encontrada na tela. A automação não pode continuar.')
        except Exception as e:
            st.error(f'Ocorreu um erro inesperado: {e}')
        finally:
            if 'web' in locals():
                st.info("O navegador será mantido aberto para inspeção.")

