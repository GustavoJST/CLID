
# Sumário <!-- omit in toc -->
- [Início rápido](#início-rápido)
  - [Setup do projeto no Google Cloud](#setup-do-projeto-no-google-cloud)
  - [Instalação no Windows](#instalação-no-windows)
  - [Instalação no Linux](#instalação-no-linux)
  - [Primeira execução](#primeira-execução)
  - [Movendo a pasta do CLID](#movendo-a-pasta-do-clid)
- [Guia do usuário](#guia-do-usuário)
  - [Downloading](#downloading)
  - [Uploading](#uploading)
  - [Calculando tamanho de uma pasta](#calculando-tamanho-de-uma-pasta)
  - [Configurações e preferências](#configurações-e-preferências)

<hr>
<br>

# Início rápido
## Setup do projeto no Google Cloud
Para usar o CLID, é necessário que você faça um projeto no Google Cloud. Siga o tutorial passo a passo para criar um.
1. Abra a página web do [Console do Google Cloud](https://console.cloud.google.com/getting-started) e faça login.
2. No canto superior esquerdo, clique em **Selecione um projeto** e crie um novo projeto.
3. De um nome ao projeto (qualquer nome) e clique em **Criar**.
4. Vá para a [Tela de permissão OAuth](https://console.cloud.google.com/apis/credentials/consent), selecione seu projeto e coloque o Tipo de Usuário (User Type) para **Externo**.
5. Preencha apenas os campos necessários (nome do app, email para suporte do usuário e email do desenvolvedor). Os emails podem ser o mesmo que você usou para fazer login no Google Cloud. Depois de preencher estas informações, pule até chegar em **Usuários de teste**.
6. Em Usuários de teste, adicione os emails que você quer usar com o CLID (Você pode especificar mais de um email). Depois disso, clique em **Salvar e continuar**.
7. Abra a página da [API do Google Drive](https://console.cloud.google.com/marketplace/product/google/drive.googleapis.com?q=search&referrer=search), selecione o projeto que você criou e ative a API.
8. Agora, entre na página das [Credenciais](https://console.cloud.google.com/apis/credentials) e crie uma nova credencial **ID do Cliente OAuth**.
9. No **Tipo de aplicativo**, escolha **App para computador**, de um nome e clique em **Criar**.
10. Na janela pop-up que irá se abrir, faça do download do arquivo **JSON**.
11. In the pop-up window that will open, download the **JSON** file.
12. O arquivo JSON terá o nome **client_secrets_(stringLongaAqui).json**. Renomeie-o para `credentials.json`.
13. Mova o arquivo `credentials.json` para a pasta do CLID (mesmo lugar onde `CLID.py` está localizado) depois de fazer os procedimentos de instalação mencionados abaixo, para o seu respectivo sistema operacional.
<br> <br>

## Instalação no Windows
1. Certifique-se de ter a **versão 3.10** (ou superior) do Python.
2. Clone/faça download do repositório.
3. Instale o virtualenv usando `pip install virtualenv`.
4. Navegue até a pasta do projeto usando `cd path/to/[CLID_folder]`.
5. Crie um novo ambiente virtual na pasta do projeto, chamado `CLID_env`, usando `virtualenv CLID_env`.
6. Ative o ambiente virtual navegando até a pasta `Scripts` usando `cd CLID_env/Scripts`. Após isso, digite `activate`. 
7. Depois de ativar o ambiente virtual, instale as dependencias necessárias usando `pip install -r requirements.txt`. 
8. Abra `CLID.py` no editor de código, copie o shebang para Windows e cole-o na primeira linha do código.
9.  Agora você pode iniciar o CLID no terminal usando apenas `CLID.py` ou clicando diretamente no arquivo/atalho do `CLID.py`.
<br><br>

## Instalação no Linux
1. Certifique-se de ter a **versão 3.10** (ou superior) do Python.
2. Clone/faça download do repositório.
3. Instale o virtualenv usando `pip install virtualenv`.
4. Navegue até a pasta do projeto usando `cd path/to/[CLID_folder]`.
5. Crie um novo ambiente virtual na pasta do projeto, chamado `CLID_env`, usando `virtualenv CLID_env`.
6. Ative o ambiente virtual usando `source CLID_env/bin/activate`.
7. Depois de ativar o ambiente virtual, instale as dependencias necessárias usando `pip install -r requirements.txt`. 
8. Abra `CLID.py` no editor de código, copie o shebang para Linux e cole-o na primeira linha do código.
9.  Torne `CLID.py` um executável usando `chmod u+x CLID.py`.
10. Agora você pode iniciar o CLID no terminal usando `./CLID.py`. <br><br> 
 
## Primeira execução
Na primeira vez que você executar o CLID, um processo de autenticação (Flow), será iniciado, e o navegador será aberto. Por fim, escolha a conta na qual você deseja acessar o Google Drive com o CLID (e lembre-se, apenas contas que são **Usuários de Teste** irão funcionar. Leia novamente o passo 6 do [Setup do projeto no Google Cloud](#setup-do-projeto-no-google-cloud) para mais informações). 

Após isso, um arquivo `token.json` será gerado a partir de `credentials.json`. Se você quiser mudar de conta, apenas delete `token.json`, execute o CLID e escolha outra conta (que seja um usuário de teste) no processo de autenticação. <br> <br> 

## Movendo a pasta do CLID
Cuidado ao mover a pasta do CLID pelo seus sistema após a criação do `CLID_env`. Pastas criadas pelo virtualenv vão 'quebrar' quando forem movidas de lugar, fazendo CLID parar de funcionar.

Se você precisar mover a pasta do CLID para outro lugar em seu computador, delete a pasta `CLID_env`, mova a pasta do CLID e refaça o passo a passo da criação do ambiente virtual, [mencionado acima](#instalação-no-windows), para seu sistema operacional.
<br><br> 

# Guia do usuário
## Downloading
Fazer o download de um arquivo/pasta é muito simples:

1. A partir do menu, digite `D` para entrar no modo de download.
2. Pesquise por um arquivo/pasta procurando pelo seu nome, ou digite `list` para visualizar uma lista com todos seus arquivos e pastas presentes no seu Drive.
3. Escolha o número do arquivo que você quer baixar.
4. Escolha um diretório de download... 
<br>
    
E é isso! Se um arquivo estiver comprimido, você terá a opção de extrair o arquivo depois de baixa-lo. Os formatos suportados para a extração são `.zip`, `.tar.gz` e `.tar`. 
<br>

Embora o processo de download seja fácil, tem algumas coisas importantes que você precisa ter em mente: <br>


### Download de arquivo/pasta do Google Workspace <!-- omit in toc -->
No CLID, é possível baixar um arquivo ou pasta. Observe que, quando fazendo download de uma pasta, esta não será comprimida. Em vez disso, CLID irá fazer uma 'cópia' da estrutura da sua pasta do Google Drive, criando pastas no seu sistema local quando necessário, e baixando os arquivos dentro das pastas criadas.
<br>

Agora, a respeito dos arquivos do Google Workspace. Ao fazer download de um arquivo do Google Workspace (Docs, Slides, etc), você poderá escolher qual o formato será usado para exportar o arquivo antes do download. No entanto, ao fazer download de uma pasta que possui arquivo(s) do Google Workspace dentro de si, CLID irá automaticamente escolher um formato de exportação, e se o arquivo for de um tipo não suportado, ele será pulado.

Em conclusão, tentar fazer download de arquivos não suportados irá **cancelar** o download (no caso de arquivos únicos), ou **pular** o arquivo (quando fazendo download de pastas). Veja a tabela abaixo para mais informações sobre quais os formatos de exportação estão disponíveis para cada modo de download (arquivo único ou pasta).
<br><br>

| Arquivo Google Workspace         | Download de arquivo único           | Download de pasta     |
| -----------------------------    | :-----------------------------:     | :-------------------: |
| Google Documents                 | MS Word, HTML, Plain Text ou PDF    | MS Word               |
| Google Slides (Presentation)     | MS PowerPoint ou PDF                | MS PowerPoint         |
| Google Sheets                    | MS Excel, CSV ou PDF                | MS Excel              |
| Google Jamboard                  | PDF                                 | PDF                   |
| Google Drawing                   | PNG, JPEG, SVG ou PDF               | PNG                   |
| Google App Scripts               | JSON                                | JSON                  |
| Google Sites                     | :x: Não suportado :x:               | :x: Não suportado :x: |
| Google Forms                     | :x: Não suportado :x:               | :x: Não suportado :x: |
| Google My Maps                   | :x: Não suportado :x:               | :x: Não suportado :x: |

<br> 

## Uploading
Fazer upload de arquivos com o CLID também é muito simples:
1. A partir do menu, digite `C` para entrar no modo de upload.
2. Digite o **caminho absoluto** (absolute path) do arquivo que você quer fazer upload.

Depois dos dois passos mencionados acima, o processo de upload irá começar. Se o arquivo for um diretório (pasta), CLID irá automaticamente comprimir o diretório antes de fazer upload para o Google Drive (Já no Google Drive, é possivel fazer a descompressão do arquivo `.zip` usando apps de terceiros, se você querer.) <br>

CLID também irá checar se o arquivo já está presente no seu Drive, e se estiver, irá lhe dar uma opção para substituir o arquivo ou manter os dois arquivos, renomeando o arquivo que você esta fazendo upload para algo como `arquivo(1).zip`.<br><br>

## Calculando tamanho de uma pasta
CLID também pode calculcar o tamanho de uma pasta do Drive. Ele faz isso iterando sobre todos os arquivos em sua pasta, pegando o tamanho de cada um e somando a um total. Ao final da operação, você terá um resumo com informações sobre o nome da pasta, tamanho, número total de arquivos, pastas, arquivos do Google Workspace e arquivos não suportados. <br>

Esse processo pode demorar para pastas com muitas subpastas dentro, Quanto mais **subpastas** uma pasta tiver, maior será o tempo que levará para calcular o seu tamanho.

**Importante**: Dependendo dos conteúdos da pasta, o tamanho total da pasta no seu sistema pode ser diferente do valor calculado pelo CLID. Isso acontece quando lidando com arquivos do Google Workspace, principalmente devido as diferenças de tamanho do arquivo, dependendo para qual formato o arquivo foi exportado (alguns formatos de exportação são mais leves/pesados que outros.) 
<br><br>

## Configurações e preferências
CLID possui um arquivo `settings.json` que permite ao usuário mudar como o CLID se comporta. **Para qualquer mudança feita em `settings.json` ter efeito, é necessário reiniciar o CLID**. A seguir, uma explicação do que cada configuração faz: <br><br>

### download_directory (string | null) <!-- omit in toc -->
Permite ao usuário especificar um diretório de download para todos os arquivos/pastas baixados com o CLID. Se `"download_directory": null`, CLID irá perguntar por um diretório de download toda vez que você for baixar um arquivo.

Exemplo: `"download_directory": "C:\\Users\\Gustavo\\Downloads"` <br>

Clid irá pular o prompt de diretório de download, e todos os arquivos/pastas baixados com CLID irão para a pasta `Downloads`. Note que o caminho especificado deve ser um **caminho absoluto**. 

Por padrão, o valor desta configuração é `null`.<br><br>

### upload_path (string | null) <!-- omit in toc -->
Quase a mesma coisa que `download_directory`, mas diz respeito ao upload de arquivos. Especifique o **caminho absoluto** do arquivo que você quer fazer upload, e CLID irá pular o prompt pedindo pelo caminho do arquivo na hora do upload. Muito útil se você faz upload do mesmo arquivo várias vezes no Google Drive. Se `"upload_path": null`, CLID irá sempre perguntar por um caminho de arquivo ao fazer upload.

Exemplo: `"upload_path": "C:\\Users\\Gustavo\\file.txt"` 

Por padrão, o valor desta configuração é `null`.<br><br>

**IMPORTANTE: Para `download_directory` e `upload_path`, lembre-se de usar barras invertidas duplas ( \\\\ ) ou uma única barra normal ( / ) no caminho do arquivo/diretório.** Esse é um problema comum no Windows pois, ao copiar o caminho de uma pasta ou arquivo, geralmente ele é separado usando uma única barra invertida ( \\ ), que não é suportado pelo JSON. <br> <br>

### shared_with_me (bool) <!-- omit in toc -->
Modifica como o CLID olha e lista seus arquivos do Google Drive.

* `false` : CLID irá pesquisar/listar apenas arquivos e pastas **criados ou de autoria do usuário**, ao fazer um download ou calcular o tamanho de uma pasta. 
* `true` : CLID irá pesquisar/listar arquivos e pastas **criados ou de autoria do usuário**, assim como arquivos **compartilhados com o usuário**, ao fazer um download ou calcular o tamanho de uma pasta. 
  
Por padrão, o valor desta configuração é `false`.<br><br>

### preferred_compression_format (string) <!-- omit in toc -->
Muda o formato de compressão preferido ao comprimir pastas para upload. Os formatos suportados são:

* `".zip"` 
* `".tar.gz"`

Exemplo: `"preferred_compression": ".tar.gz"`

Se você pretende usar o CLID para fazer upload/download de arquivos que serão usados entre sistemas Windows e Linux, é aconselhável usar o formato `.tar.gz`, pois ele ajuda a evitar problemas de codificação de caracteres (especialmente os da língua portuguesa, como 'ã' ou 'õ'), que podem ocorrer ao usar `.zip`.

Se você pretende usar CLID apenas com sistemas Windows, `.zip` deve ser suficiente. Em caso de problemas com nome de arquivos, tente mudar para `.tar.gz`.

Por padrão, o valor desta configuração é `".tar.gz"`.<br><br>