# GeoConteúdo

O **GeoConteúdo** é um software desktop local para análise de conteúdo em pesquisas geográficas qualitativas. Desenvolvido para substituir fluxos de trabalho feitos no LibreOffice Base, ele oferece uma interface visual rica, moderna e intuitiva em **PySide6 (Qt)** para leitura, seleção e codificação de entrevistas vinculadas a espacialidades e categorias discursivas.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem**: Python 3
- **Interface Gráfica**: PySide6 (Qt 6)
- **Banco de Dados**: SQLite gerenciado localmente com SQLAlchemy (ORM)
- **Análise de Dados**: Pandas
- **Gráficos**: Matplotlib
- **Redes / Grafos**: NetworkX (para preparação de métricas e exportação de rede)

---

## 📂 Estrutura do Projeto de Pesquisa

Cada projeto do GeoConteúdo trabalha com arquivos armazenados localmente no seu computador dentro de uma pasta específica da pesquisa. A estrutura de diretórios do projeto criada é:

```
GeoConteudo [Nome do Projeto]/
├── projeto.geoconteudo       # Banco SQLite local contendo dados e metadados
├── entrevistas/             # Cópias locais das entrevistas importadas (.txt ou .docx)
├── exportacoes/             # Planilhas CSV exportadas do projeto e arquivos para o Gephi
├── graficos/                # Imagens geradas de frequências e matriz de cruzamento
└── backups/                 # Pasta reservada para cópias de segurança (backups)
```

---

## 🚀 Instalação e Execução

### Pré-requisitos

Certifique-se de ter o **Python 3** instalado em sua máquina.

### Passos para Instalação

1. Abra o terminal na pasta do projeto e crie um ambiente virtual para isolar as dependências:
   ```bash
   python3 -m venv .venv
   ```

2. Ative o ambiente virtual:
   - **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```cmd
     .venv\Scripts\activate
     ```

3. Instale as dependências requeridas através do arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### Executando o GeoConteúdo

Com o ambiente virtual ativo, execute o script de entrada:
```bash
python3 run.py
```

---

## 💡 Como Usar o Software

### 1. Criar ou Abrir um Projeto
- **Criar**: Acesse o menu `Arquivo -> Novo Projeto...`, preencha o Nome do Projeto, Descrição, Notas Metodológicas e selecione a pasta de destino. O GeoConteúdo criará a estrutura completa de pastas no local selecionado.
- **Abrir**: Vá em `Arquivo -> Abrir Projeto...` e selecione o arquivo `projeto.geoconteudo` de um projeto existente.

### 2. Importar Entrevistas
- Clique no botão **`+ Importar Entrevista`** na lateral esquerda.
- Selecione um ou mais arquivos em formato **`.txt`** ou **`.docx`**.
- O sistema copiará automaticamente os arquivos de origem para a subpasta `entrevistas/` do projeto, extrairá seu conteúdo integral e registrará a entrevista no banco de dados.

### 3. Cadastrar Sujeitos Entrevistados (Opcional)
- Acesse o menu `Gerenciar -> Sujeitos Entrevistados...` para abrir a ficha de sujeitos.
- Você pode cadastrar pseudônimos/códigos de sujeitos da pesquisa e associar suas características sociodemográficas e espaciais (idade, gênero, raça, renda, filhos, município, bairro, vila, rua) e também dados relativos ao autor/vítima da relação.
- *Nota*: Você também pode criar um sujeito rapidamente de dentro da janela de codificação clicando no botão **`+ Novo`**.

### 4. Selecionar e Codificar Trechos (Evocações)
- Clique em uma entrevista na lateral esquerda para carregar seu texto integral no painel central.
- Com o mouse, **selecione o trecho** que deseja codificar no texto central.
- Clique no botão **`Analisar trecho`** (ou use o menu correspondente).
- A janela de codificação se abrirá exibindo o trecho selecionado. Preencha:
  - **Categoria Discursiva**: Use o autocompletar de categorias existentes ou digite uma nova (ela será cadastrada automaticamente no projeto ao salvar).
  - **Espacialidade Discursiva**: Use o autocompletar de espacialidades existentes ou digite uma nova (também cadastrada de forma automática).
  - **Sujeito Entrevistado**: Vincule o sujeito a quem pertence a fala.
  - **Elementos / Sujeito da Relação / Observações Analíticas**: Informações qualitativas geográficas.
- Clique em **`Salvar Evocação`**. O trecho aparecerá listado na lateral direita.

### 5. Navegar e Interagir com as Evocações
- Ao clicar em uma evocação na lateral direita, o GeoConteúdo localiza o trecho no texto da entrevista central, dá foco e **destaca visualmente com cor de fundo amarela** o fragmento correspondente.
- Clique com o **botão direito** sobre a evocação na lista da direita para **Editar** ou **Excluir** o registro.

### 6. Gerar Relatórios, Gráficos e Rede para Gephi
- Vá na aba **`Relatórios e Visualizações`** (ou menu `Análise e Exportação -> Gerar Gráficos e Matriz...`).
- Clique no botão **`Atualizar Dados e Gráficos`**. O sistema irá processar em tempo real:
  1. O gráfico de frequência de Categorias Discursivas.
  2. O gráfico de frequência de Espacialidades Discursivas.
  3. A Matriz de Cruzamento quantitativa (exibida na grade e salva como Heatmap gráfico).
  4. Métricas estatísticas de rede calculadas via NetworkX (densidade da rede, número de conexões, etc.).
- Os gráficos de imagens geradas são guardados automaticamente na pasta `graficos/` do seu projeto.
- **Exportação CSV**: Use o menu `Análise e Exportação -> Exportar Evocações (CSV)...` para salvar a planilha de dados na subpasta `exportacoes/`.
- **Rede para Gephi**: Vá em `Análise e Exportação -> Exportar Rede para Gephi (CSV)...`. O sistema exportará dois arquivos na pasta `exportacoes/` do projeto:
  - `gephi_nodes.csv` (Nós: ID do nó, rótulo e tipo - Categoria ou Espacialidade).
  - `gephi_edges.csv` (Arestas: Origem, Destino e Peso baseado no cruzamento acumulado de evocações).
  - Esses arquivos estão prontos para importação direta no software Gephi.
