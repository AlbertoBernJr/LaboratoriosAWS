# Guia de Laboratório: Credenciais Temporárias com AWS Security Token Service (STS)

## Visão Geral

Este laboratório prático demonstra o uso de credenciais temporárias na AWS via AWS Security Token Service (STS). Você aprenderá a criar e "assumir" uma `role` (função) IAM com permissões restritas, tanto pelo console quanto via linha de comando, validando os acessos permitidos e negados para entender o poder e a segurança desse mecanismo.

## Objetivos de Aprendizagem

  * Preparar o ambiente CloudShell com as dependências necessárias.
  * Criar uma `role` IAM com uma política de confiança específica e permissões limitadas.
  * Assumir a `role` no console da AWS para testar as permissões visualmente.
  * Utilizar o AWS CloudShell para gerar credenciais temporárias via STS.
  * Configurar e usar essas credenciais temporárias na AWS CLI.
  * Compreender na prática como a expiração de credenciais e as políticas de confiança funcionam.

## Cenário

Você é um desenvolvedor que precisa acessar o Amazon S3 por um curto período. Em vez de usar suas credenciais de longo prazo, você assumirá uma `role` com permissões temporárias e restritas apenas ao S3, seguindo o princípio do menor privilégio.

## Pré-requisitos

  * Acesso ao Console de Gerenciamento da AWS.
  * Familiaridade básica com a linha de comando.
  * O arquivo de script `credenciais_temporarias.py` fornecido pelo curso.

-----

## Parte 1: Configuração do Ambiente no CloudShell

Vamos garantir que o CloudShell tenha todas as ferramentas necessárias para o laboratório.

1.  **Abrir o CloudShell:** No Console AWS, clique no ícone do CloudShell (parece um terminal `>_`) no canto superior direito para iniciar uma sessão.

2.  **Atualizar o Sistema e Instalar Python:** Execute os seguintes comandos para garantir que o ambiente esteja atualizado e o Python 3 esteja instalado.

    ```bash
    sudo yum update -y
    sudo yum install -y python3
    python3 --version
    ```

3.  **Instalar Boto3 (SDK da AWS para Python):** Execute os comandos abaixo para instalar a biblioteca Boto3, que o script usará para interagir com a AWS.

    ```bash
    pip3 install boto3 --upgrade
    python3 -c "import boto3; print(boto3.__version__)"
    ```

-----

## Parte 2: Criação da Role Temporária no IAM

Agora, vamos criar a `role` que definirá as permissões temporárias.

1.  Acesse o serviço **IAM** no Console AWS.

2.  No menu esquerdo, clique em **Funções (Roles)** e depois em **Criar função (Create role)**.

3.  **Selecionar entidade confiável:** Escolha **Política de confiança personalizada**.

4.  No editor JSON, substitua o conteúdo pelo seguinte, colando o ARN do seu próprio usuário IAM onde indicado. Para encontrar seu ARN, vá em **IAM \> Usuários \> seu-nome-de-usuario**.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "COLE_AQUI_O_ARN_DO_SEU_USUARIO_IAM"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    ```

    > **O que isso faz?** Esta "Política de Confiança" estabelece que **apenas** o seu usuário IAM tem permissão para assumir esta `role`. É a porta de entrada.

5.  Clique em **Avançar**.

6.  **Adicionar permissões:** Na barra de busca, procure e selecione a política `AmazonS3FullAccess`.

7.  Clique em **Avançar**.

8.  **Nomear, revisar e criar:**

      * **Nome da função:** `SeuNome-Role-S3-Temporaria`
      * Revise as configurações e clique em **Criar função**.

-----

## Parte 3: Testando a Role no Console AWS

Vamos verificar visualmente se a `role` funciona como esperado.

1.  No canto superior direito do console, clique no seu nome de usuário e copie o **ID da conta**.
2.  Clique novamente no seu nome de usuário e selecione **Alternar função (Switch role)**.
3.  Preencha os campos:
      * **ID da conta:** Cole o ID que você copiou.
      * **Função:** `SeuNome-Role-S3-Temporaria`
      * **Nome de exibição:** `Acesso-Temporario-S3`
      * **Cor:** Escolha uma cor para diferenciar a sessão.
4.  Clique em **Alternar função**.
5.  **Validação:** O console mudará de cor. Navegue até o **S3** (acesso permitido) e depois tente ir para o **Lambda** (acesso negado).
6.  Para voltar, clique no nome da `role` no canto superior direito e selecione **Retornar**.

-----

## Parte 4: Gerando Credenciais Temporárias com STS no CloudShell

Agora, vamos fazer o mesmo processo, mas via linha de comando.

1.  **Faça o upload do script:** No CloudShell, clique em **Ações \> Carregar arquivo** e envie o script `credenciais_temporarias.py`.

2.  **Obtenha o ARN da Role:** Volte para **IAM \> Funções**, clique na sua `role` e copie o ARN.

3.  **Execute o script para gerar as credenciais:** No CloudShell, execute o comando abaixo, substituindo `SEU_ROLE_ARN` pelo ARN que você copiou.

    ```bash
    python3 credenciais_temporarias.py --role-arn SEU_ROLE_ARN --session-name AcessoTemporario --duration 3600
    ```

4.  **Resultado:** O terminal exibirá as credenciais temporárias. Copie os três valores: `AccessKeyId`, `SecretAccessKey`, e `SessionToken`.

-----

## Parte 5: Usando as Credenciais Temporárias na AWS CLI

Vamos configurar o CloudShell para usar essas credenciais temporárias.

1.  Execute o comando `aws configure` e insira os dois primeiros valores que você copiou:

      * `AWS Access Key ID`: Cole o `AccessKeyId`.
      * `AWS Secret Access Key`: Cole o `SecretAccessKey`.
      * `Default region name`: `us-east-1`
      * `Default output format`: `json`

2.  **Adicionar o Session Token (Passo Crucial):** Execute o comando abaixo para adicioná-lo à configuração, substituindo `SEU_SESSION_TOKEN` pelo valor que você copiou.

    ```bash
    aws configure set aws_session_token SEU_SESSION_TOKEN
    ```

### 5.1. Validando o Acesso via CLI

1.  **Verifique sua identidade atual:**

    ```bash
    aws sts get-caller-identity
    ```

    > O resultado deve mostrar que você agora está "assumido" pela `role`.

2.  **Teste o acesso ao S3 (Permitido):**

    ```bash
    aws s3 ls
    ```

3.  **Teste o acesso ao Lambda (Negado):**

    ```bash
    aws lambda list-functions
    ```

    > Você receberá uma mensagem de "Acesso negado", provando que as permissões da `role` estão funcionando.

-----

## Parte 6: Limpeza dos Recursos

É fundamental remover todos os recursos criados.

1.  **Remover as credenciais temporárias da CLI:**
      * No CloudShell, execute `rm -rf ~/.aws` para apagar a pasta de configuração.
2.  **Excluir a Home Directory do CloudShell (Opcional, mas recomendado):**
      * No CloudShell, clique em **Ações \> Excluir home directory do AWS CloudShell** e confirme.
3.  **Excluir a Role IAM:**
      * Vá para o serviço **IAM \> Funções**.
      * Procure pela sua `role` (`SeuNome-Role-S3-Temporaria`), selecione-a e clique em **Excluir**.
