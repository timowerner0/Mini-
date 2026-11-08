import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Mini Gamma", page_icon="⚡", layout="centered")

st.title("⚡ Mini Gamma")
st.write("Digite o prompt, gere os slides e personalize o texto.")

api_key = st.sidebar.text_input("Chave da API (Groq/OpenAI)", type="password")

if not api_key:
    st.warning("⚠️ Insira sua chave de API na barra lateral para começar.")
else:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

    prompt = st.text_area("Sobre o que será a apresentação?", placeholder="Ex: História da IA em 5 slides", height=100)
    
    if st.button("Gerar Apresentação", type="primary"):
        if prompt:
            with st.spinner("Gerando slides..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        
                        messages=[
                            {
                                "role": "system",
                                "content": "Você é um criador de apresentações profissional. Retorne os slides divididos claramente com títulos e tópicos curtos (máximo 4 tópicos por slide). Formate usando Markdown."
                            },
                            {"role": "user", "content": prompt}
                        ]
                    )
                    st.session_state['resultado'] = response.choices[0].message.content
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            st.error("Digite um prompt antes de gerar.")

    if 'resultado' in st.session_state:
        st.divider()
        st.subheader("✏️ Edite e Personalize")
        texto_editado = st.text_area("Altere o conteúdo como quiser:", value=st.session_state['resultado'], height=350)
