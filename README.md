# websocket-world-cup

#### **Projeto integrador 8º semestre**

> **Importante!**

Antes de utilizar o projeto, sempre executar `git pull` para pegar a versão mais recente do repositório

# Para rodar o projeto:

#### **Pelo Docker**

> Caso tenha feito alguma alteração do código, rodar ==docker compose down== antes

No projeto, temos a possibilidade de rodar por docker, e para isso, basta executar o comando:

`docker-compose up -d`

Este comando irá buildar a imagem e subir o container na porta **6000**

#### **Pelo Python**

Caso não possua o docker instalado, basta executar diretamente pelo python, seguir os passos:

- Instalar a dependencia de websocket

  - `pip install websockets`

- Executar o projeto
  - `python main.py`
