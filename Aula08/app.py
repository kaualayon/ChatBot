import os #biblioteca para interagir com o sistema operacional
import gradio as gr # importa a biblitoeca ggradio para criar interface web
from groq import Groq # importa a biblioteca Groq para interagir com a API Groq

# Define a chave da API Groq
GROQ_API_KEY = os.getenv('GROQ_API_KEY','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')

#Inicializa o cliente da API Groq
client = Groq(api_key=GROQ_API_KEY)

#Funçao para processar a entrada de dados pelo usuario e gerar resposta
def assistente_quimicafisica(user_prompt):
    if user_prompt.strip()=="15":
        return "Encerrando assistente especialista em Quimica e Fisica ! Até mais !!"
    
    #faz a solicitaçao para o modelo LLM
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages =[
            {
              "role":"system","content":"Voce é um assistente especializado em Quimica e Fisica"},
              {"role":"user","content":user_prompt}
        ],
        temperature=0,
        max_tokens=1024,
        top_p=1,
        stream=False
    )

    #Retorna a resposta do assistente

    return completion.choices[0].message.content



#Configura a interface do Gradio
iface = gr.Interface(
   fn=assistente_quimicafisica,
   inputs=gr.Textbox(lines=2,placeholder= "Digite sua pergunta sobre as areas de química e física: "),
   outputs="text",
   title="Assistente Especialista em Quimica e Fisica",
   description="Digite sua pergunta sobre as areas de Quimica e Fisica e receba respostas da IA especialista",
   live = True
)

# Executa a interface web

if __name__ == "__main__":
    iface.launch()