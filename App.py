import streamlit as st
from openai import OpenAI
from fpdf import FPDF

st.set_page_config(page_title="Mini Gamma", page_icon="⚡", layout="centered")

st.title("⚡ Mini Gamma")
st.write("Digite o prompt, escolha o estilo visual e baixe seus slides em PDF.")

# Dicionário com as paletas de cores dos temas
TEMAS = {
    " Minimalista": {
        "bg": (248, 249, 250),        # Fundo claro
        "card": (255, 255, 255),      # Cartão branco
        "title": (33, 37, 41),         # Título escuro
        "text": (73, 80, 87),          # Texto cinza escuro
        "accent": (13, 110, 253)       # Azul minimalista
    },
    "🚀 Futurista": {
        "bg": (10, 15, 29),           # Fundo azul profundo/espaço
        "card": (20, 29, 47),         # Cartão tech
        "title": (0, 240, 255),        # Cyan neon
        "text": (210, 225, 240),       # Texto claro futurista
        "accent": (112, 0, 255)       # Roxo neon
    },
    "🩸 Sangue": {
        "bg": (12, 12, 12),           # Fundo preto
        "card": (26, 20, 20),         # Cartão escuro avermelhado
        "title": (220, 20, 60),        # Vermelho sangue
        "text": (235, 235, 235),       # Texto claro
        "accent": (139, 0, 0)          # Vermelho escuro profundo
    }
}

# Função para gerar o PDF formatado com base no tema escolhido
def gerar_pdf(texto_slides, tema_nome):
    cores = TEMAS[tema_nome]
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    
    blocos = texto_slides.split('---')
    
    for bloco in blocos:
        if not bloco.strip():
            continue
        pdf.add_page()
        
        # Fundo da página
        pdf.set_fill_color(*cores["bg"])
        pdf.rect(0, 0, 297, 210, 'F')
        
        # Cartão central de conteúdo
        pdf.set_fill_color(*cores["card"])
        pdf.rect(15, 15, 267, 180, 'F')
        
        # Linha estética superior de detalhe (accent color)
        pdf.set_fill_color(*cores["accent"])
        pdf.rect(15, 15, 267, 3, 'F')
        
        linhas = bloco.strip().split('\n')
        pdf.set_left_margin(25)
        pdf.set_y(28)
        
        for linha in linhas:
            linha_clean = linha.strip()
            if not linha_clean:
                continue
            
            # Se for título
            if linha_clean.startswith('#') or 'Slide' in linha_clean:
                titulo = linha_clean.replace('#', '').strip()
                pdf.set_font("Helvetica", style='B', size=20)
                pdf.set_text_color(*cores["title"])
                pdf.cell(0, 15, txt=titulo.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                pdf.ln(4)
            # Se for tópico
            else:
                topico = linha_clean.replace('-', '•').replace('*', '•')
                pdf.set_font("Helvetica", size=13)
                pdf.set_text_color(*cores["text"])
                pdf.multi_cell(245, 9, txt=topico.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(2)
                
    return bytes(pdf.output())

# Configurações na barra lateral
st.sidebar.header("⚙️ Configurações")
api_key = st.sidebar.text_input("Chave da API (Groq)", type="password")
tema_escolhido = st.sidebar.selectbox("Escolha o Estilo dos Slides", list(TEMAS.keys()))

if not api_key:
    st.warning("⚠️ Insira sua chave de API da Groq na barra lateral para começar.")
else:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

    prompt = st.text_area("Sobre o que será a apresentação?", placeholder="Ex: História do Futebol em 5 slides", height=100)
    
    if st.button("Gerar Apresentação", type="primary"):
        if prompt:
            with st.spinner("Criando a apresentação..."):
                try:
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "system",
                                "content": "Você é um criador de apresentações profissional. Retorne os slides divididos estritamente pelo caractere '---'. Para cada slide, use um título com # e tópicos curtos (máximo 4 por slide)."
                            },
                            {"role": "user", "content": prompt}
                        ]
                    )
                    st.session_state['resultado'] = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Erro ao gerar: {e}")
        else:
            st.error("Digite um prompt antes de gerar.")

    if 'resultado' in st.session_state:
        st.divider()
        st.subheader(f"📋 Prévia do Conteúdo ({tema_escolhido})")
        st.markdown(st.session_state['resultado'])
        
        try:
            pdf_bytes = gerar_pdf(st.session_state['resultado'], tema_escolhido)
            st.divider()
            st.download_button(
                label=f"📥 Baixar PDF ({tema_escolhido.strip()})",
                data=pdf_bytes,
                file_name=f"apresentacao_{tema_escolhido.strip().lower()}.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Erro ao converter para PDF: {e}")
