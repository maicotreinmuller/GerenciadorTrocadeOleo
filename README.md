# Controle de Trocas de Óleo

Este projeto é uma aplicação web para gerenciar trocas de óleo, clientes e vencimentos de manutenções. Desenvolvido com Flask e SQLite, oferece uma interface intuitiva para cadastro e acompanhamento das trocas de óleo realizadas, com controle de vencimentos e exibição de um dashboard financeiro.

## Funcionalidades

- **Dashboard**: Resumo financeiro das trocas realizadas, incluindo o total arrecadado e status das próximas manutenções.
- **Cadastro de Clientes**: Registro de dados de clientes, como nome, telefone, placa, marca, modelo e ano do veículo.
- **Troca de Óleo**: Lançamento e edição de registros de troca de óleo, com campos para data, quilometragem, valor e vencimento.
- **Controle de Vencimentos**: Indicação do status de cada troca (No prazo, Vence hoje, Vencido).
- **Pesquisa e Filtro**: Pesquisa em tempo real para facilitar o acesso rápido a registros específicos.
- **Alertas**: Utilização de SweetAlert para confirmar exclusões e alertas de sucesso.

## Estrutura de Arquivos

- **app.py**: Contém a lógica do servidor com as rotas e as funções de CRUD para clientes e trocas de óleo.
- **templates/**
  - `base.html`: Template base com a estrutura de layout, menu lateral e suporte para mensagens de sucesso.
  - `dashboard.html`: Exibe o resumo financeiro com gráficos do status de trocas.
  - `clientes.html`: Interface para gerenciamento de clientes, com modal para cadastro e edição.
  - `troca_oleo.html`: Página para controle das trocas de óleo, com funcionalidade de cadastro, edição e pesquisa.
- **static/**:
  - **CSS e JS**: Arquivos de estilo e scripts personalizados para tornar a interface responsiva e moderna.

## Como Usar

1. Clone o repositório:
    ```bash
    git clone https://github.com/maicotreinmuller/GerenciadorTrocadeOleo.git
    ```

2. Inicie o servidor:
    ```bash
    python app.py
    ```
3. Acesse a aplicação em `http://127.0.0.1:5000`.

## Tecnologias

- **Backend**: Flask, SQLite
- **Frontend**: HTML, CSS, JavaScript (com SweetAlert e Chart.js para gráficos)
- **Configuração Local**: Formatação BRL e manipulação de datas para controle de vencimentos.
