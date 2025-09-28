### **Guia de Laboratório: Amazon S3 Básico, Avançado e Acesso a Logs**

#### **Visão Geral**

Neste laboratório prático, você aprenderá a utilizar os principais recursos do Amazon S3 voltados à organização, segurança e gerenciamento eficiente de dados. Serão abordadas a criação de buckets seguros, controle de versões, automação de regras de ciclo de vida, geração de URLs pré-assinadas e a configuração de logs de acesso.

#### **Objetivos de Aprendizagem**

* Criar buckets no S3 com configurações recomendadas de segurança.
* Ativar e utilizar o versionamento para manter múltiplas versões de arquivos.
* Configurar regras de ciclo de vida para transição e expiração de objetos.
* Gerar URLs pré-assinadas para compartilhamento seguro e temporário.
* Ativar e consultar logs de acesso utilizando um bucket dedicado.

#### **Cenário**

Você é responsável pela gestão de armazenamento na nuvem e sua missão é garantir que os dados estejam organizados, seguros e com custos otimizados. Para isso, você aplicará práticas de versionamento, automação e monitoramento de acessos no Amazon S3.

#### **Pré-requisitos**

* Conta ativa na AWS.
* Permissões no IAM para criar e gerenciar buckets e objetos no S3.
* Um editor de texto simples (como Bloco de Notas ou VS Code).

---

### **Parte 1: Criação dos Buckets S3**

Vamos começar criando dois buckets: um para nossos dados e outro para armazenar os logs de acesso.

1.  **Acesse o console do S3:** Na barra de pesquisa do Console AWS, digite "S3" e selecione o serviço.
2.  **Verifique a Região:** No canto superior direito, certifique-se de que a região selecionada seja **N. Virginia (us-east-1)**.

#### **1.1. Criar o Bucket Principal (para os Dados)**

1.  Clique no botão **Criar bucket**.
2.  **Configurações:**
    * **Nome do bucket:** Insira um nome único globalmente. Ex: `meu-bucket-de-dados-seunome-aaaammdd`.
        > **Importante:** Nomes de bucket são únicos em toda a AWS. Use apenas letras minúsculas, números e hifens.
    * **Região da AWS:** Mantenha `us-east-1`.
    * **Propriedade do objeto:** Mantenha `ACLs desabilitadas (recomendado)`.
    * **Bloquear todo o acesso público:** Mantenha esta opção **marcada**. Esta é a prática de segurança mais importante.
    * **Versionamento do bucket:** Deixe `Desativar` (ativaremos mais tarde).
3.  Clique em **Criar bucket** no final da página.

#### **1.2. Criar o Bucket de Logs**

1.  Clique novamente em **Criar bucket**.
2.  **Configurações:**
    * **Nome do bucket:** Insira outro nome único. Ex: `meus-logs-de-acesso-seunome-aaaammdd`.
    * Mantenha todas as outras configurações iguais ao primeiro bucket, incluindo **Bloquear todo o acesso público**.
3.  Clique em **Criar bucket**.

---

### **Parte 2: Upload de Arquivos e Versionamento**

Agora, vamos habilitar o versionamento para proteger nossos arquivos contra exclusões acidentais e manter um histórico de alterações.

1.  **Crie um arquivo de teste:**
    * No seu computador, crie um arquivo de texto chamado `teste-s3.txt`.
    * Dentro do arquivo, escreva: `Versão 1 do arquivo.` e salve.
2.  **Acesse o bucket principal** (`meu-bucket-de-dados-...`) e clique em **Carregar**.
3.  Adicione o arquivo `teste-s3.txt` e clique em **Carregar**.
4.  **Habilitar o Versionamento:**
    * Dentro do bucket de dados, clique na aba **Propriedades**.
    * Encontre a seção "Versionamento de bucket" e clique em **Editar**.
    * Selecione **Ativar** e clique em **Salvar alterações**.
5.  **Faça upload de uma nova versão:**
    * Edite o arquivo `teste-s3.txt` no seu computador. Adicione uma nova linha: `Versão 2 do arquivo.` e salve.
    * Faça o upload do mesmo arquivo novamente para o bucket. O S3 não irá sobrescrever, mas sim criar uma nova versão.
6.  **Visualize as Versões:**
    * Na aba **Objetos** do seu bucket, ative a opção **Mostrar versões**.
    * Você verá as duas versões do arquivo, cada uma com um "ID da versão" diferente. A versão mais recente é a padrão quando você acessa o objeto.

---

### **Parte 3: Regra de Ciclo de Vida**

Vamos criar uma regra para mover dados mais antigos para uma classe de armazenamento mais barata e, eventualmente, excluí-los para otimizar custos.

1.  Dentro do bucket de dados, clique na aba **Gerenciamento**.
2.  Em "Regras de ciclo de vida", clique em **Criar regra de ciclo de vida**.
3.  **Configurar a Regra:**
    * **Nome da regra:** `MoverParaGlacier-ExpirarDepois`
    * **Escopo da regra:** Escolha **Aplicar a todos os objetos no bucket** e marque a caixa de confirmação.
    * **Ações de regras de ciclo de vida:**
        * Marque **Transição de versões atuais de objetos entre classes de armazenamento**.
        * Marque **Expirar versões atuais de objetos**.
    * **Configurar a transição:**
        * Em "Escolher transições...", selecione **Glacier Instant Retrieval**.
        * Em "Dias após a criação do objeto", digite `30`.
    * **Configurar a expiração:**
        * Em "Dias após a criação do objeto", digite `31`.
        > **Por que 31?** A expiração deve ocorrer após a transição. Isso dá ao objeto 1 dia na classe Glacier antes de ser excluído.
4.  Clique em **Criar regra**.

---

### **Parte 4: URLs Pré-assinadas**

Precisa compartilhar um arquivo de forma segura e temporária sem tornar seu bucket público? Use uma URL pré-assinada.

1.  Acesse a aba **Objetos** do seu bucket de dados.
2.  Clique no nome do arquivo `teste-s3.txt`.
3.  No canto superior direito, clique em **Ações** -> **Compartilhar com um URL pré-assinado**.
4.  **Tempo de expiração:** Defina um período curto, como **1 minuto**.
5.  Clique em **Criar URL pré-assinado**.
6.  Copie a URL gerada e **abra-a em uma janela anônima** do seu navegador.
7.  Você conseguirá ver o conteúdo do arquivo. Após 1 minuto, a mesma URL dará um erro de acesso negado.

---

### **Parte 5: Configuração e Verificação de Logs de Acesso**

Vamos registrar quem acessa os objetos no nosso bucket principal.

1.  Acesse o **bucket principal** (`meu-bucket-de-dados-...`) e vá para a aba **Propriedades**.
2.  Role até a seção **Registro em log de acesso ao servidor** e clique em **Editar**.
3.  Selecione **Ativar**.
4.  **Destino:** Clique em **Procurar no S3** e selecione o seu **bucket de logs** (`meus-logs-de-acesso-...`). Clique em **Escolher destino**.
5.  Clique em **Salvar alterações**.
6.  **Gere atividade:** Para criar logs, realize alguma ação no bucket de dados, como fazer o upload de um novo arquivo ou baixar o `teste-s3.txt`.

> **Nota Importante:** A entrega de logs de acesso do S3 **não é em tempo real**. Pode levar **algumas horas** para que os arquivos de log apareçam no seu bucket de destino. Seja paciente! Após o período de espera, você verá arquivos de log no formato `.log.gz` no seu bucket de logs.

---

### **Parte 6: Limpeza dos Recursos (Etapa Crucial)**

Para evitar custos inesperados, sempre exclua os recursos ao final do laboratório.

1.  **Esvaziar os Buckets:** Um bucket precisa estar completamente vazio antes de ser excluído.
    * Acesse o **bucket principal** (`meu-bucket-de-dados-...`).
    * Selecione todos os objetos, clique em **Ações -> Excluir**.
    * Na tela de confirmação, digite `excluir permanentemente` e confirme.
    * **Importante:** Se o versionamento estiver ativo, a ação acima apenas cria "marcadores de exclusão". Para limpar de vez, clique no botão **Esvaziar** no topo da página do bucket, confirme que deseja excluir todas as versões e marcadores, e siga as instruções.
    * Repita o processo para o **bucket de logs**, se algum log já tiver sido gerado.
2.  **Excluir os Buckets:**
    * Volte à página principal do S3.
    * Selecione o **bucket principal** e clique em **Excluir**. Digite o nome do bucket para confirmar.
    * Repita o processo para o **bucket de logs**.

Parabéns! Você concluiu o laboratório e aprendeu a usar funcionalidades essenciais do Amazon S3.
