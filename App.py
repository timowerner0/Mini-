import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import io

st.set_page_config(page_title="Mini Gamma", page_icon="⚡", layout="centered")

st.title("⚡ Mini Gamma")
st.write("Digite o prompt, gere a estrutura e baixe seus slides em PDF.")

# Função para gerar o PDF formatado slide por slide
def gerar_pdf(texto_slides):
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Orientação Paisagem (Slide)
    pdf.set_auto_page_break(auto=bool(False))
    
    # Separa os slides pelo separador '---' ou por títulos de Slide
    blocos = texto_slides.split('---')
    
    for bloco in blocos:
        if not bloco.strip():
            continue
        pdf.add_page()
        
        # Fundo do Slide (Estilo Escuro Elegante)
        pdf.set_fill_color(24, 28, 36)
        pdf.rect(0, 0, 297, 210, 'F')
        
        # Cartão de Conteúdo (Moldura central)
        pdf.set_fill_color(35, 41, 54)
        pdf.rect(15, 15, 267, 180, 'F')
        
        linhas = bloco.strip().split('\n')
        pdf.set_left_margin(25)
        pdf.set_y(25)
        
        for linha in linhas:
            linha_clean = linha.strip()
            if not linha_clean:
                continue
            
            # Se for título (com # ou Slide)
            if linha_clean.startswith('#') or 'Slide' in linha_clean:
                titulo = linha_clean.replace('#', '').strip()
                pdf.set_font("Helvetica", style='B', size=20)
                pdf.set_text_color(255, 215, 0) # Cor Amarelo Dourado
                pdf.cell(0, 15, txt=titulo.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                pdf.ln(5)
            # Se for tópico
            else:
                topico = linha_clean.replace('-', '•').replace('*', '•')
                pdf.set_font("Helvetica", size=13)
                pdf.set_text_color(240, 240, 240) # Texto claro
                pdf.multi_cell(245, 9, txt=topico.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(2)
                
    return bytes(pdf.output())

# Barra lateral para chave
api_key = st.sidebar.text_input("Chave da API (Groq)", type="password")

if not api_key:
    st.warning("⚠️ Insira sua chave de API da Groq na barra lateral para começar.")
else:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

    prompt = st.text_area("Sobre o que será a apresentação?", placeholder="Ex: Trajetória e recordes do Cristiano Ronaldo em 10 slides", height=100)
    
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
        st.subheader("📋 Conteúdo dos Slides")
        
        # Exibe visualmente
        st.markdown(st.session_state['resultado'])
        
        # Gerar o arquivo PDF para download
        try:
            pdf_bytes = gerar_pdf(st.session_state['resultado'])
            st.divider()
            st.download_button(
                label="📥 Baixar Apresentação em PDF",
                data=pdf_bytes,
                file_name="apresentacao_mini_gamma.pdf",
                mime="application/pdf",
                type="primary"
            )
        except Exception as e:
            st.error(f"Erro ao converter para PDF: {e}")
