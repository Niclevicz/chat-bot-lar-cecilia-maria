# chat-bot-lar-cecilia-maria

## 🐾 Chatbot de Agendamento para Adoção de Animais
Este projeto é um chatbot interativo desenvolvido com Python e Flask para facilitar o agendamento de visitas em um abrigo de animais fictício chamado Lar Cecília Maria. Ele oferece uma interface web simples através de um index.html, onde o usuário interage com o assistente virtual.

### 🚀 Tecnologias Utilizadas
* Python 3.10+
* Flask
* HTML/CSS (interface via index.html)
* Gemini API (Google Generative AI)

### 📁 Estrutura do Projeto


~~~bash
Projeto/
├── static/
│   └── styles.css         # (Se houver)
├── templates/
│   └── index.html         # Interface principal do chatbot
├── app.py                 # Código principal Flask
├── .env                   # Chave da API (não incluído no repositório)
├── requirements.txt       # Dependências do projeto
└── README.md              # Este arquivo
~~~

### ✅ Pré-requisitos
1. Python instalado (recomenda-se usar um ambiente virtual).
2. Criar um arquivo .env com sua chave da API do Gemini:

~~~env
GOOGLE_API_KEY=sua_chave_aqui
~~~

### ⚙️ Como Executar o Projeto
1. Clone o repositório
~~~bash
git clone https://github.com/seuusuario/seu-repositorio.git
cd seu-repositorio
~~~
2. Crie e ative um ambiente virtual (opcional, mas recomendado)
~~~bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
~~~
3. Instale as dependências
~~~bash
pip install -r requirements.txt
~~~
4. Execute a aplicação Flask
~~~bash
python app.py
~~~
Se tudo estiver correto, a aplicação estará disponível em:
~~~cpp
http://127.0.0.1:5000
~~~

### 💻 Acessar a Interface
Após iniciar o Flask, abra seu navegador e acesse:

[📍 http://127.0.0.1:5000](http://127.0.0.1:5000)

Você verá a tela do index.html, onde o chatbot estará pronto para conversar com o usuário e realizar o agendamento da visita.

### 📅 Funcionalidade do Chatbot
* Pergunta nome, espécie, faixa etária e porte do animal.
* Sugere opções compatíveis.
* Realiza o agendamento da visita ao abrigo com data, hora e endereço.

### 🐶 Exemplo de Uso
>Usuário: Quero adotar um gato.
>Chatbot: Claro! Você prefere filhote, adulto ou idoso?
>Usuário: Adulto.
>Chatbot: Aqui estão dois gatinhos adultos incríveis! Vamos agendar uma visita?

### 📌 Observações
* O arquivo .env não deve ser compartilhado publicamente.
* Este projeto é apenas um protótipo para fins educativos e pode ser adaptado para produção.
