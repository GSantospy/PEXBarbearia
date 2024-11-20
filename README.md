# :star: PEX I – GERENCIADOR DE BARBEARIA

Este projeto é uma aplicação web desenvolvida com FastAPI para agendamento de serviços e gestão de estoque em uma barbearia. A plataforma oferece funcionalidades como cadastro de usuários, login, agendamento de serviços, controle de estoque e gestão de contas. A interface é construída com templates Jinja2 e proporciona uma experiência interativa ao usuário.

## :wrench: Linguagens e Ferramentas

- **Python**
- **JavaScript**
- **HTML/CSS**
- **Bootstrap**
- **FastAPI**
- **OpenPyXL**
- **ReportLab**

## :art: Layout

### :desktop_computer: Desktop

<img src="https://i.postimg.cc/gj1HVTVm/image.png"/>

### :iphone: Mobile

<img src="https://i.postimg.cc/zGHX2PT4/git.png" />

## :gear: Fucionalidades do Projeto

- [x] **Cadastro**
- [x] **Login**
- [x] **Agendamento de Serviços**
- [x] **Gestão de Estoque**
- [x] **Gestão de Contas**
- [x] **Gestão de Perfil**
### Funcionalidades em desenvolvimento
- [ ] **Alterar Estoque**
- [ ] **Alterar Conta**
- [ ] **Alterar Agendamento**
- [ ] **Alterar Perfil**

## :electric_plug: Rodando o Projeto

```shell
# 1. Clone o projeto

git clone https://github.com/GSantospy/PEXBarbearia.git

# 2. Instale as dependências

pip install -r requirements.txt

# 3. Executar o Servidor

uvicorn main:app --reload

```

## :link: Endpoints

### Cadastro e Login
- **GET /** - *Página principal*
- **GET /login** - *Exibe a página de login.*
- **POST /login** - *Realiza o login de um usuário.*
- **GET /cadastro** - *Exibe a página de cadastro.*
- **POST /cadastro** - *Cadastra um novo usuário.*
### Agendamento de Serviços
- **GET /agendar** - *Exibe a página para agendamento de serviços.*
- **POST /agendar** - *Processa o agendamento de um serviço.*
- **GET /agendamentos** - *Exibe a lista de agendamentos.*
### Gestão de Estoque
- **GET /estoque** - *Exibe a página de estoque e lista os produtos.*
- **POST /estoque** - *Registra um novo produto no estoque.*
- **GET /excluir_produto/{index}** - *Exclui um produto do estoque.*
### Gestão de Contas
- **GET /contas** - *Exibe a página e a lista de contas registradas.*
- **POST /contas** - *Registra uma nova conta a pagar.*
- **GET /excluir_conta/{index}** - *Exclui uma conta.*
- **GET /alterar_status_conta/{index}/{status}** - *Altera o status de uma conta.*
### Perfil do Usuário
- **GET /perfil** - *Exibe as informações do usuário.*
- **GET /logout** - *Desconecta o usuário.*
### Relatórios
- **GET /relatorio/excel** - *Realiza o download de um relatório em .xlsx*
- **GET /relatorio/pdf** - *Realiza o download de um relatório em .pdf*


## :building_construction: Arquitetura
A aplicação é construída sobre o framework **FastAPI** e segue a arquitetura de **API RESTful**. As informações são armazenadas em memória, utilizando listas para armazenar dados de agendamentos, estoque e contas.

### Estrutura de Diretório
```bash
/static
  /css
  /js
/templates
  /index.html
  /login.html
  /cadastro.html
  /agendar.html
  /agendamentos.html
  /alterarAgendamento.html
  /estoque.html
  /alterarEstoque.html
  /contas.html
main.py
logs.log
```

## :memo: Logs
Os logs da aplicação são registrados no arquivo *logs.log*. Ele registra as requisições HTTP feitas ao servidor, com informações sobre o método, URL e o corpo das requisições, bem como o status das respostas geradas.
