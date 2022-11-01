# CLID <!-- omit in toc -->
CLID (abreviação para CLI Drive) é um simples cliente CLI feito para interagir com o Google Drive. Use o CLID para fazer o download/upload de arquivos e pastas, ou calcular o tamanho de um pasta presente no seu Google Drive, tudo diretamente do terminal. 

CLID foi feito usando a [Google API Python client library](https://github.com/googleapis/google-api-python-client) para a comunicação API com o Google Drive, [tqdm](https://github.com/tqdm/tqdm) para exibir as barras de progresso e [gdrive_folder_size](https://github.com/XtremeRahul/gdrive_folder_size) para ajudar no cálculo do tamanho de pastas do Google Drive.
<br><br>

<hr>

Sumário
- [Sobre o projeto](#sobre-o-projeto)
- [Documentação](#documentação)
- [Limitações](#limitações)

<hr>

# Sobre o projeto
CLID é um simples programa cujo o principal objetivo é fazer o download/upload de arquivos e pastas, além de calcular o tamanho de pastas do Google Drive, usando apenas o terminal.

A ideia para projeto surgiu de um problema que eu estava tendo em sincronizar uma pasta entre meu computador desktop e meu notebook que eu uso na faculdade. Eu estava usando o Google Drive para fazer essa sincronização, porém estava ficando bem repetitivo fazer isso todo dia (muitas tarefas pequenas e repetitivas, como abrir o navegador, baixar o arquivo, descomprimir o arquivo, substituir a pasta... já deu pra entender). Então, eu tive a ideia de fazer um programa/script no Python que lidaria com a maioria dessas tarefas chatas, sem nem mesmo eu precisar abrir o navegador.
<br><br>

## História legal cara... mas o que ele consegue fazer? <!-- omit in toc -->
A seguir, uma lista do que o CLID consegue e não consegue fazer:

### CLID consegue: <!-- omit in toc -->
- Baixar arquivos e pastas criados por você ou de sua propriedade, além de arquivos e pastas que foram compartilhados com você.
- Fazer upload de arquivos e pastas.
- Calcular o tamanho de uma pasta do Google Drive.
- Exportar arquivos do Google Workspace para formatos diferentes durante o download.
- Facilitar o processo de upload/download, comprimindo/extraindo pastas quado necessário.
- Lidar com arquivos duplicados no Google Drive ou no sistema quando fazendo download/upload de arquivos.

### CLID não consegue: <!-- omit in toc -->
- Baixar múltiplos arquivos/pastas de uma só vez.
- Interagir com o Google Drive em qualquer outra maneira que não seja uma das formas citadas acimas. Isso inclui mover arquivos para outros lugares no Google Drive, compartilhar arquivos/pastas com outros, mudar as configurações de visibilidade de um arquivo, ou qualquer outra ação do Google Drive. 
- Baixar arquivos/pastas que não estejam na pasta root do Google Drive (Também conhecida como pasta/página principal), com a exceção de arquivos/pastas compartilhadas com o usuário. Você pode, no entanto, baixar uma pasta no diretório raiz, junto com todos os seus arquivos e subpastas (não importanto o quão fundo a pasta seja).
- Fazer café :( . Ainda...
<br><br>

# Documentação
Leia a [documentação](docs/guide-pt-BR.md/#sumário) para obter informações sobre como instalar e usar o CLID.
<br><br>

# Limitações
- Downloads de pastas são mais lentos que downloads de arquivos. Se você achar muito lento, é aconselhavel fazer upload/download de pastas como um arquivo comprimido.
- Downloads e uploads são feitos em chunks, a fim de não sobrecarregar a memória RAM caso o arquivo seja muito grande. O problema é que API do Google Drive para o Python um pouco lento para fazer requisições. Para contornar esse problema, o tamanho de cada chunk é de 100MB. Embora você possa mudar este valor no código, fazer isso irá resultar em velocidades de download menores.
- Devido ao tamanho de 100MB do chunk (descrito acima), as barras de progresso irão atualizar apenas 100MB por vez, o que pode demorar um pouco dependendo do quão rapido é a sua internet. Se você alterar o tamanho do chunk, a barra de progresso irá mudar de acordo, porém a sua velocidade de download **irá** diminuir.
- Apenas um arquivo/pasta pode ser baixado por vez.
- CLID pode apenas baixar arquivos que foram compartilhados com o usuário ou que estão no diretório root do Google Drive (pasta/página principal do drive). Isso significa que se você quiser baixar um arquivo ou pasta que esta dentro de outra pasta, você terá que baixar toda a pasta que está no diretório root, ou baixar o arquivo/pasta por fora do CLID. 

