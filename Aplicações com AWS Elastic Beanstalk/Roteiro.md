### **Guia de Laboratório: Implantação de Aplicações com AWS Elastic Beanstalk**

#### **Visão Geral**

Este laboratório prático guia você através do processo de implantação de uma aplicação web de exemplo usando o AWS Elastic Beanstalk. Você irá criar as permissões IAM necessárias, lançar um ambiente, explorar as funcionalidades de gerenciamento e, ao final, entender como o Elastic Beanstalk simplifica a implantação e o gerenciamento de aplicações na nuvem AWS.

#### **Objetivos de Aprendizagem**

* Criar uma `role` IAM (Perfil de Instância EC2) com as permissões necessárias para o Elastic Beanstalk.
* Configurar e lançar um ambiente Elastic Beanstalk para uma aplicação web (Node.js).
* Navegar pelo console para monitorar a saúde, logs e métricas da aplicação.
* Entender como o Elastic Beanstalk abstrai e gerencia a infraestrutura subjacente (EC2, Auto Scaling, etc.).

#### **Cenário**

Você é um desenvolvedor encarregado de implantar rapidamente uma aplicação web na AWS. A ferramenta escolhida é o AWS Elastic Beanstalk, para automatizar o provisionamento da infraestrutura, garantindo que as permissões estejam corretas e que a aplicação seja facilmente gerenciada e monitorada.

#### **Pré-requisitos**

* Uma conta AWS ativa.
* Permissões para criar `roles` IAM e ambientes Elastic Beanstalk.

---

### **Parte 1: Criação da Role IAM para a Instância EC2**

O Elastic Beanstalk precisa de permissões para que as instâncias EC2 que ele cria possam se comunicar com o serviço (para enviar logs, reportar saúde, etc.). Vamos criar essa permissão agora.

1.  Acesse o serviço **IAM** no Console AWS.
2.  No menu esquerdo, clique em **Funções** (Roles).
3.  Clique em **Criar função** (Create role).
4.  **Tipo de entidade confiável:** Selecione **Serviço da AWS**.
5.  **Caso de uso:** Selecione **EC2** e clique em **Avançar**.
6.  Na página **Adicionar permissões**, use a barra de busca para encontrar e anexar as seguintes políticas gerenciadas pela AWS:
    * `AWSElasticBeanstalkWebTier`
    * `AWSElasticBeanstalkMulticontainerDocker`
    * `AWSElasticBeanstalkWorkerTier`
    * **Dica:** Para facilitar, você pode filtrar por "AWSElasticBeanstalk" e selecionar as políticas relevantes.
7.  Clique em **Avançar**.
8.  **Nome da função:** Dê um nome descritivo, por exemplo: `role-beanstalk-ec2-SeuNomeSobrenome`.
9.  Revise as políticas anexadas e a política de confiança (deve confiar em `ec2.amazonaws.com`).
10. Clique em **Criar função**.

---

### **Parte 2: Criação do Ambiente Elastic Beanstalk**

Agora, vamos usar a `role` criada para lançar nosso ambiente e implantar uma aplicação de exemplo.

1.  Navegue até o serviço **Elastic Beanstalk** no Console AWS.
2.  Clique em **Criar aplicação**.
3.  **Nome da aplicação:** Insira um nome, por exemplo: `Meu-App-SeuNomeSobrenome`.
4.  **Nome do ambiente:** `Meu-App-SeuNomeSobrenome-dev`.
5.  **Plataforma:** Selecione **Node.js**.
6.  **Código da aplicação:** Selecione **Aplicação de exemplo**.
7.  **Predefinições:** Para este laboratório, selecione **Instância única (qualificada para o nível gratuito)** para manter os custos baixos e clique em **Próximo**.

#### **2.1. Configurando o Acesso ao Serviço (Etapa Crucial)**

Nesta tela, vamos definir as permissões que o **serviço Beanstalk** e as **instâncias EC2** usarão.

1.  **Função de serviço (Service role):**
    * Marque **Usar uma função de serviço existente**.
    * Selecione `aws-elasticbeanstalk-service-role`.
    * **O que é isso?** Esta é a permissão que o **serviço** Elastic Beanstalk usa para orquestrar outros serviços AWS (como criar instâncias EC2) em seu nome.
2.  **Perfil da instância EC2 (EC2 instance profile):**
    * No menu suspenso, selecione a `role` que você criou na Parte 1: `role-beanstalk-ec2-SeuNomeSobrenome`.
    * **O que é isso?** Esta é a permissão que as **instâncias EC2** criadas pelo Beanstalk terão para se comunicar de volta com o serviço.
3.  Clique em **Pular para revisão**.
4.  Na página de revisão, verifique as configurações e role até o final. Clique em **Enviar**.
5.  O Elastic Beanstalk começará a provisionar todos os recursos. **Isso pode levar de 5 a 10 minutos.** Você pode acompanhar os eventos na tela. Quando o status do ambiente estiver verde e com a saúde **Ok**, a implantação estará concluída.

---

### **Parte 3: Verificação e Exploração do Ambiente**

Com o ambiente pronto, vamos explorar o que foi criado.

#### **3.1. Acessando sua Aplicação**

1.  No topo do painel do seu ambiente, você verá uma URL. Clique nela.
2.  **Sucesso!** Você deverá ver a página de parabéns da aplicação de exemplo do Node.js.

#### **3.2. Explorando o Painel**

Dedique alguns minutos para navegar pelas abas no menu esquerdo do painel do seu ambiente:

* **Saúde (Health):** Mostra o status geral e métricas detalhadas sobre as solicitações.
* **Logs:** Permite solicitar e baixar os logs diretamente das instâncias EC2.
* **Monitoramento (Monitoring):** Exibe gráficos do CloudWatch para métricas como uso de CPU, tráfego de rede, etc.
* **Configuração (Configuration):** O coração do seu ambiente. Aqui você pode alterar praticamente tudo: o tipo das instâncias, as configurações de rede, o balanceador de carga, a capacidade do Auto Scaling e muito mais.

#### **3.3. O Que Aconteceu nos Bastidores?**

O Elastic Beanstalk não é mágica; é um orquestrador. Ele usou o **AWS CloudFormation** para criar uma "pilha" (stack) de recursos. Você pode ir ao console do:
* **EC2:** Para ver a instância que foi criada.
* **CloudFormation:** Para ver a pilha com todos os recursos que o Beanstalk provisionou para você.

---

### **Parte 4: Limpeza dos Recursos (Importante!)**

Siga estes passos para excluir todos os recursos criados e evitar custos.

1.  **Terminar o Ambiente Elastic Beanstalk:**
    * No painel do **Elastic Beanstalk**, selecione seu ambiente (`Meu-App-SeuNomeSobrenome-dev`).
    * No canto superior direito, clique em **Ações** -> **Terminar ambiente**.
    * Confirme digitando o nome do ambiente. Isso excluirá todos os recursos associados (EC2, Security Group, etc.).
2.  **Excluir a Aplicação (Opcional):**
    * Após o término do ambiente, você pode excluir o "contêiner" da aplicação. Na página de aplicações, selecione `Meu-App-SeuNomeSobrenome` e clique em **Ações** -> **Excluir aplicação**.
3.  **Excluir a Role do IAM:**
    * Vá para o serviço **IAM** -> **Funções**.
    * Procure pela `role` que você criou (`role-beanstalk-ec2-SeuNomeSobrenome`).
    * Selecione-a e clique em **Excluir**.

Parabéns, você concluiu o laboratório e aprendeu os fundamentos do AWS Elastic Beanstalk!
