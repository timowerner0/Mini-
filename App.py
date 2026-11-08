import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Mini Gamma", page_icon="⚡", layout="centered")

st.title("⚡ Mini Gamma v2.0")
st.write("Crie apresentações completas com temas, fontes personalizadas e imagens inteligentes.")

# Dicionário de Temas
TEMAS = {
    " Minimalista": {
        "bg": (248, 249, 250), "card": (255, 255, 255),
        "title": (33, 37, 41), "text": (73, 80, 87), "accent": (13, 110, 253)
    },
    "🚀 Futurista": {
        "bg": (10, 15, 29), "card": (20, 29, 47),
        "title": (0, 240, 255), "text": (210, 225, 240), "accent": (112, 0, 255)
    },
    "🩸 Sangue": {
        "bg": (12, 12, 12), "card": (26, 20, 20),
        "title": (220, 20, 60), "text": (235, 235, 235), "accent": (139, 0, 0)
    }
}

# Fontes disponíveis
FONTES = {
    "Inter": "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bwght%5D.ttf",
    "Montserrat": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "Roboto": "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto%5Bwght%5D.ttf"
}

# Função auxiliar para buscar imagem relacionada via Unsplash Source (baseada no prompt/título)
def baixar_imagem(termo):
    try:
        url = f"https://source.unsplash.com/random/400x300/?{termo}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except:
        pass
    return None

# Função de Geração do PDF
def gerar_pdf(texto_slides, tema_nome, fonte_nome, termo_busca):
    cores = TEMAS[tema_nome]
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    
    # Carregar Fonte do Google Fonts dinamicamente
    font_path = f"/tmp/{fonte_nome}.ttf"
    try:
        r = requests.get(FONTES[fonte_nome])
        with open(font_path, "wb") as f:
            f.write(r.content)
        pdf.add_font(fonte_nome, "", font_path)
        pdf.add_font(fonte_nome, "B", font_path)
    except:
        fonte_nome = "Helvetica" # Fallback se falhar
        
    blocos = texto_slides.split('---')
    layout_posicoes = ["direita", "esquerda", "topo", "nenhuma"]
    
    for i, bloco in enumerate(blocos):
        if not bloco.strip():
            continue
        pdf.add_page()
        
        # Fundo do Slide
        pdf.set_fill_color(*cores["bg"])
        pdf.rect(0, 0, 297, 210, 'F')
        
        # Cartão central
        pdf.set_fill_color(*cores["card"])
        pdf.rect(15, 15, 267, 180, 'F')
        
        # Detalhe superior
        pdf.set_fill_color(*cores["accent"])
        pdf.rect(15, 15, 267, 3, 'F')
        
        # Definir layout da imagem para este slide (alternando)
        posicao_img = layout_posicoes[i % len(layout_posicoes)]
        
        img_temp_path = None
        if posicao_img != "nenhuma":
            img = baixar_imagem(termo_busca)
            if img:
                img_temp_path = f"/tmp/slide_img_{i}.jpg"
                img.save(img_temp_path)

        # Configurar larguras baseadas na presença da imagem
        largura_texto = 245
        x_texto = 25
        y_texto = 28
        
        if img_temp_path and posicao_img == "esquerda":
            pdf.image(img_temp_path, x=25, y=30, w=80, h=60)
            x_texto = 110
            largura_texto = 160
        elif img_temp_path and posicao_img == "direita":
            pdf.image(img_temp_path, x=190, y=30, w=80, h=60)
            largura_texto = 160
        elif img_temp_path and posicao_img == "topo":
            pdf.image(img_temp_path, x=115, y=25, w=70, h=40)
            y_texto = 70
            largura_texto = 245
            
        linhas = bloco.strip().split('\n')
        pdf.set_left_margin(x_texto)
        pdf.set_y(y_texto)
        
        for linha in linhas:
            linha_clean = linha.strip()
            if not linha_clean:
                continue
            
            # Limpar caracteres corrompidos/marcadores problemáticos
            linha_clean = linha_clean.replace('?', '-').replace('•', '-')
            
            if linha_clean.startswith('#') or 'Slide' in linha_clean:
                titulo = linha_clean.replace('#', '').strip()
                pdf.set_font(fonte_nome, style='B', size=18)
                pdf.set_text_color(*cores["title"])
                pdf.cell(0, 12, txt=titulo.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                pdf.ln(3)
            else:
                topico = f"- {linha_clean.lstrip('-* ')}"
                pdf.set_font(fonte_nome, size=12) # Legenda maior e legível
                pdf.set_text_color(*cores["text"])
                pdf.multi_cell(largura_texto, 8, txt=topico.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(2)
                
    return bytes(pdf.output())

# Configurações na barra lateral
st.sidebar.header("⚙️ Configurações Pro")
api_key = st.sidebar.text_input("Chave da API (Groq)", type="password")
tema_escolhido = st.sidebar.selectbox("Estilo Visual", list(TEMAS.keys()))
fonte_escolhida = st.sidebar.selectbox("Tipografia (Fonte)", list(FONTES.keys()))

if not api_key:
    st.warning("⚠️ Insira sua chave de API da Groq na barra lateral para começar.")
else:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

    prompt = st.text_area("Sobre o que será a apresentação?", placeholder="Ex: Cristiano Ronaldo, Inteligência Artificial, Farmacologia...", height=100)
    termo_chave = st.text_input("Palavra-chave para imagens (ex: football, technology, medicine)", value="presentation")
    
    if st.button("Gerar Apresentação Completa", type="primary"):
        if prompt:
            with st.spinner("Criando slides, ajustando fontes e buscando imagens..."):
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
        st.subheader(f"📋 Prévia do Projeto")
        st.markdown(st.session_state['resultado'])
        
        try:
            pdf_bytes = gerar_pdf(st.session_state['resultado'], tema_escolhido, fonte_escolhida, termo_chave)
            st.divider()
            st.download_button(
                label=f"📥 Baixar PDF Pro ({fonte_escolhida} / {tema_escolhido.strip()})",
                data=pdf_bytes,
                file_name=f"mini_gamma_{fonte_escolhida.lower()}.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Erro ao renderizar PDF com imagens: {e}")
