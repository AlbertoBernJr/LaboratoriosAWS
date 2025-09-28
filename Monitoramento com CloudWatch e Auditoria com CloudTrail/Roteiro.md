# Guia de Laboratório: Monitoramento com CloudWatch e Auditoria com CloudTrail

## Visão Geral

Este laboratório prático orienta você na criação de um ambiente de monitoramento e auditoria na AWS. Você irá configurar alarmes para monitorar a utilização de CPU em uma instância EC2, habilitar o rastreamento de atividades da conta com o AWS CloudTrail e aprender a visualizar os logs gerados.

### O que você irá construir

  * **Fluxo de Monitoramento:** Uma instância EC2 enviará métricas para o CloudWatch. Um Alarme detectará alta utilização de CPU e usará o SNS para enviar uma notificação para o seu e-mail.
  * **Fluxo de Auditoria:** Todas as chamadas de API na sua conta serão registradas pelo CloudTrail e armazenadas de forma segura em um bucket S3.

## Objetivos de Aprendizagem

  * Configurar um alarme no CloudWatch para monitorar a CPU de uma instância EC2.
  * Enviar notificações por e-mail usando o Amazon SNS.
  * Habilitar o AWS CloudTrail para auditar eventos na conta.
  * Armazenar e visualizar logs de auditoria em um bucket S3.

## Pré-requisitos

  * Conta AWS ativa com as permissões IAM necessárias (CloudWatch, CloudTrail, SNS, S3, EC2).
  * Um par de chaves EC2 para acesso via SSH.

-----

## Parte 1: Preparação do Ambiente (Instância EC2)

Vamos começar criando a máquina virtual que será monitorada.

1.  Acesse o serviço **EC2** no Console AWS.
2.  Clique em **Executar instância**.
3.  **Configurações da Instância:**
      * **Nome:** `SeuNome-Instancia-Teste-CloudWatch`
      * **AMI:** `Amazon Linux 2 AMI (HVM)` - (deve ser o padrão).
      * **Tipo de instância:** `t2.micro` (qualificada para o nível gratuito).
      * **Par de chaves (login):** Selecione um par de chaves que você já possua e tenha acesso ao arquivo `.pem`.
      * **Configurações de rede:**
          * Clique em **Editar**.
          * **Atribuir IP público automaticamente:** Verifique se está **Habilitado**.
          * **Firewall (security groups):**
              * Selecione **Criar um novo grupo de segurança**.
              * **Nome do grupo de segurança:** `SeuNome-SG-Teste-CloudWatch`
              * **Regras de entrada:** Adicione uma regra do tipo `SSH` com a **Origem** definida como `0.0.0.0/0`.
                > **Aviso de Segurança:** Usar `0.0.0.0/0` abre o acesso SSH para qualquer IP na internet. Para ambientes de produção, sempre restrinja a origem para o seu IP (`Meu IP`).
4.  Revise as configurações e clique em **Executar instância**.
5.  Aguarde a instância ser criada e, na lista de instâncias, copie o **ID da Instância**.

-----

## Parte 2: Configuração do Alarme de Monitoramento (CloudWatch e SNS)

Agora, vamos criar o sistema que nos alertará sobre o uso excessivo de CPU.

### 2.1. Criar o Tópico de Notificação (SNS)

1.  Acesse o serviço **Amazon SNS**.
2.  No menu esquerdo, clique em **Tópicos** e depois em **Criar tópico**.
3.  **Tipo:** Selecione `Padrão`.
4.  **Nome:** `SNS-Alarme-CPU-SeuNome`
5.  Clique em **Criar tópico**.
6.  Dentro do tópico recém-criado, clique em **Criar inscrição**.
      * **Protocolo:** Selecione `E-mail`.
      * **Endpoint:** Insira seu endereço de e-mail pessoal.
7.  Clique em **Criar inscrição**.

### 2.2. CONFIRMAR A INSCRIÇÃO DO E-MAIL (Passo Crucial\!)

1.  Acesse sua caixa de entrada de e-mail.
2.  Você receberá um e-mail da AWS com o assunto "AWS Notification - Subscription Confirmation".
3.  Abra o e-mail e clique no link **"Confirm subscription"**.
    > Se você não fizer isso, não receberá as notificações do alarme.

### 2.3. Criar o Alarme no CloudWatch

1.  Acesse o serviço **CloudWatch**.
2.  No menu esquerdo, em **Alarmes**, clique em **Todos os alarmes**.
3.  Clique em **Criar alarme** e depois em **Selecionar métrica**.
4.  Navegue até **EC2 \> Métricas por instância**.
5.  Na barra de busca, cole o **ID da sua instância EC2** para encontrá-la rapidamente.
6.  Marque a métrica `CPUUtilization` e clique em **Selecionar métrica**.
7.  **Configurar as condições:**
      * **Estatística:** `Média`
      * **Período:** `5 minutos`
      * **Condições:**
          * **Tipo de limite:** `Estático`
          * **Sempre que CPUUtilization for...:** `Maior que`
          * **...o limite:** `70` (para 70%)
8.  Clique em **Avançar**.
9.  **Configurar ações:**
      * **Sempre que este alarme estiver no estado:** Selecione `Em alarme`.
      * **Selecione um tópico do SNS:** Escolha `Selecionar um tópico do SNS existente`.
      * **Enviar notificações para:** Selecione o tópico que você criou (`SNS-Alarme-CPU-...`).
10. Clique em **Avançar**.
11. **Nome do alarme:** `SeuNome-Alarme-CPU-Alta-Instancia-Teste`
12. Revise tudo e clique em **Criar alarme**.

-----

## Parte 3: Configuração da Trilha de Auditoria (CloudTrail)

Vamos registrar todas as atividades (chamadas de API) que ocorrem em sua conta.

1.  Acesse o serviço **CloudTrail**.
2.  No menu esquerdo, clique em **Trilhas** e depois em **Criar trilha**.
3.  **Configurações da Trilha:**
      * **Nome da trilha:** `trilha-auditoria-geral-seunome`
      * **Local de armazenamento:** Selecione `Criar novo bucket S3`. Deixe o nome sugerido.
      * **Criptografia de arquivo de log SSE-KMS:** Mantenha **marcado**.
      * **Chave do AWS KMS gerenciada pelo cliente:** Selecione `Novo`.
      * **Alias do AWS KMS:** `alias/CloudTrailKey-seunome`
4.  Clique em **Avançar**.
5.  **Escolher eventos de log:**
      * **Eventos de gerenciamento:** Mantenha marcado.
      * **Eventos de dados** e **Eventos do Insights:** Mantenha desmarcados para este laboratório.
6.  Clique em **Avançar**, revise as configurações e clique em **Criar trilha**.

-----

## Parte 4: Geração de Carga e Verificação dos Alertas

Vamos estressar a CPU da nossa instância para disparar o alarme.

1.  **Conecte-se à sua instância EC2:**
      * No console do **EC2**, selecione sua instância.
      * Clique em **Conectar**.
      * Vá para a aba **Conexão de instância do EC2** e clique em **Conectar**.
2.  **Instale a ferramenta `stress`:** Execute os comandos abaixo no terminal, um de cada vez.
    ```bash
    sudo yum update -y
    sudo amazon-linux-extras install epel -y
    sudo yum install stress -y
    ```
3.  **Inicie o teste de estresse:** O comando abaixo irá sobrecarregar a CPU por 10 minutos (600 segundos).
    ```bash
    stress --cpu 8 --timeout 600
    ```
4.  **Monitore o resultado:**
      * Após cerca de 5 minutos, volte para o console do **CloudWatch**. O estado do seu alarme deve mudar para **Em alarme** (vermelho).
      * Verifique seu e-mail. Você deverá receber a notificação do SNS informando sobre o alarme.
      * Para parar o teste a qualquer momento, volte ao terminal e pressione `Ctrl+C`.

-----

## Parte 5: Limpeza dos Recursos (Etapa Crucial)

Para evitar custos inesperados, sempre exclua os recursos ao final do laboratório na seguinte ordem:

1.  **Encerrar a Instância EC2:**
      * No console do **EC2**, selecione a `Instancia-Teste-CloudWatch`, clique em **Estado da instância** e **Encerrar instância**.
2.  **Excluir o Alarme CloudWatch:**
      * No console do **CloudWatch**, vá para **Alarmes**, selecione o alarme que você criou e clique em **Ações -\> Excluir**.
3.  **Excluir Recursos do SNS:**
      * No console do **SNS**, vá para **Inscrições**, selecione a sua e clique em **Excluir**.
      * Depois, vá para **Tópicos**, selecione o seu e clique em **Excluir**.
4.  **Excluir a Trilha do CloudTrail:**
      * No console do **CloudTrail**, vá para **Trilhas**, selecione a sua e clique em **Excluir**.
5.  **Esvaziar e Excluir o Bucket S3:**
      * No console do **S3**, encontre o bucket criado pelo CloudTrail.
      * Clique no nome do bucket, selecione a opção **Esvaziar** e siga as instruções.
      * Após esvaziar, volte à lista de buckets, selecione-o e clique em **Excluir**.
6.  **Excluir a Chave KMS:**
      * No console do **KMS**, selecione a chave `alias/CloudTrailKey-seunome`, clique em **Ações da chave -\> Programar exclusão da chave** e configure para 7 dias.
7.  **Excluir o Grupo de Segurança:**
      * No console do **EC2**, em **Segurança de Rede**, vá para **Grupos de segurança**, selecione `SG-Teste-CloudWatch` e clique em **Ações -\> Excluir grupos de segurança**.
