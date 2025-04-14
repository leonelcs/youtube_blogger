import os
import time
from dotenv import load_dotenv, dotenv_values
import gradio as gr

from langchain_community.document_loaders import YoutubeLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# --- Configuration ---
# Load API key directly from .env file
load_dotenv()
env_values = dotenv_values()
google_api_key = env_values.get("GOOGLE_API_KEY")

if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please add it to your .env file.")

# Configure the Gemini LLM with streaming enabled
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest", 
    google_api_key=google_api_key,
    streaming=True
)

# --- Prompt Definition ---
# Define the prompt template instructing the LLM on the desired style
blog_post_prompt_template = """
Você é um assistente de IA especializado em transformar transcrições de vídeos do YouTube em posts de blog envolventes e informativos.

**Objetivo:** Reescrever a seguinte transcrição de vídeo do YouTube em um post de blog.

**Estilo Desejado:** O post deve seguir o estilo e tom do blog encontrado em: https://julianagabriel.com.br/blog/
Isso significa que o post deve ser:
*   **Informativo e Educacional:** Explicar conceitos de forma clara.
*   **Empático e Acessível:** Usar uma linguagem que conecte com o leitor, como um profissional de saúde (por exemplo, uma endocrinologista) falando com o público.
*   **Conversacional (Moderado):** Manter um tom profissional, mas não excessivamente formal ou robótico. Pode incluir perguntas retóricas ou dirigir-se ao leitor ocasionalmente.
*   **Bem Estruturado:** Usar títulos, subtítulos e listas (bullet points) para organizar a informação e facilitar a leitura.
*   **Focado na Mensagem Principal:** Extrair os pontos-chave da transcrição e apresentá-los de forma coesa.
*   **Reescrito, Não Copiado:** Reformular as frases e a estrutura para um formato de leitura (blog), não apenas colar a transcrição.
*   **Formato:** Use markdown para formatação (cabeçalhos `#`, `##`, negrito `**texto**`, listas `* item`).

**Contexto:**
*   **URL do Vídeo Original:** {youtube_url}
*   **Transcrição do Vídeo:**
---
{transcript}
---

**Instrução:**
Com base na transcrição e no estilo de blog de exemplo fornecido, gere o post do blog completo em português brasileiro. Comece diretamente com o título do post. Certifique-se de que o conteúdo seja preciso em relação à transcrição original.
"""

prompt = ChatPromptTemplate.from_template(blog_post_prompt_template)

# --- Function to Process URL with streaming ---
def create_blog_post_from_youtube_streaming(youtube_url: str):
    """
    Extracts transcript from a YouTube URL and generates a blog post with streaming output.
    
    Args:
        youtube_url: The URL of the YouTube video.
        
    Yields:
        Progress updates and content chunks as they're generated.
    """
    start_time = time.time()
    
    try:
        # Yield loading message with timer updates
        yield f"Carregando transcrição do vídeo... (0s)"
        
        # Load the transcript
        loader = YoutubeLoader.from_youtube_url(
            youtube_url,
            add_video_info=False,
            language=["pt", "en"],
            translation="pt",
        )
        
        # Load documents
        docs = loader.load()
        
        if not docs:
            yield "Erro: Não foi possível carregar a transcrição do vídeo. Verifique a URL ou as configurações de legenda do vídeo."
            return
        
        # Get transcript content
        transcript_content = docs[0].page_content
        elapsed = int(time.time() - start_time)
        yield f"Transcrição carregada com sucesso! ({elapsed}s)\n\nGerando post do blog..."
        
        # Set up streaming callbacks
        class GradioCallbackHandler(StreamingStdOutCallbackHandler):
            def __init__(self):
                super().__init__()
                self.text = ""
                
            def on_llm_new_token(self, token: str, **kwargs):
                self.text += token
                elapsed = int(time.time() - start_time)
                yield f"Gerando post do blog... ({elapsed}s)\n\n{self.text}"
        
        # Create custom callback handler for streaming
        handler = GradioCallbackHandler()
        
        # Create a new LLM instance with our callback handler
        streaming_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest", 
            google_api_key=google_api_key,
            streaming=True,
            callbacks=[handler]
        )
        
        # Create streaming chain
        streaming_chain = prompt | streaming_llm | StrOutputParser()
        
        # Process with streaming
        for chunk in streaming_chain.stream({
            "transcript": transcript_content,
            "youtube_url": youtube_url
        }):
            elapsed = int(time.time() - start_time)
            yield f"Gerando post do blog... ({elapsed}s)\n\n{chunk}"
        
        # Final output
        elapsed = int(time.time() - start_time)
        yield f"Post do blog gerado com sucesso! ({elapsed}s)\n\n{handler.text}"
        
    except Exception as e:
        elapsed = int(time.time() - start_time)
        error_msg = f"Erro ({elapsed}s): "
        
        if "Could not find transcript" in str(e):
            error_msg += f"Não foi possível encontrar a transcrição para o vídeo: {youtube_url}. Verifique se o vídeo possui legendas em português ou inglês habilitadas."
        elif "Members-only video" in str(e):
            error_msg += f"O vídeo é apenas para membros e a transcrição não pode ser acessada: {youtube_url}."
        elif "Video unavailable" in str(e):
            error_msg += f"O vídeo está indisponível: {youtube_url}."
        else:
            error_msg += f"Erro inesperado ao processar a URL {youtube_url}: {e}"
        
        yield error_msg

# --- Gradio Interface ---
def process_url_streaming(youtube_url):
    """Function to process YouTube URL from Gradio interface with streaming output"""
    if not youtube_url or "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
        yield "Por favor, insira uma URL válida do YouTube."
        return
    
    yield from create_blog_post_from_youtube_streaming(youtube_url)

# --- Example Usage ---
if __name__ == "__main__":
    # Create Gradio interface
    with gr.Blocks(theme="soft") as demo:
        gr.Markdown("# Conversor de YouTube para Blog Post")
        gr.Markdown("Cole a URL de um vídeo do YouTube para gerar um post de blog baseado na transcrição.")
        
        with gr.Row():
            youtube_url = gr.Textbox(
                label="URL do YouTube",
                placeholder="https://www.youtube.com/watch?v=...",
                show_label=True
            )
        
        with gr.Row():
            submit_btn = gr.Button("Gerar Post de Blog")
        
        output = gr.Markdown(label="Post de Blog Gerado")
        
        submit_btn.click(fn=process_url_streaming, inputs=youtube_url, outputs=output)
    
    # Launch the interface
    demo.launch()