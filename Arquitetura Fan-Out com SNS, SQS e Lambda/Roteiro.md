-----

### **Guia de Laboratório: Arquitetura Fan-Out com SNS, SQS e Lambda**

#### **Visão Geral**

Este laboratório ensina como implementar uma arquitetura fan-out na AWS. Você usará o Amazon SNS para distribuir uma única mensagem para múltiplos destinos (Amazon SQS e AWS Lambda), utilizando filtros para que cada serviço processe apenas as mensagens relevantes.

#### **O que você irá construir**

Você simulará um sistema de e-commerce. Um novo pedido (uma mensagem no SNS) será distribuído ("fan-out") para quatro serviços diferentes que executarão tarefas em paralelo:

  * **Lambda de Inventário:** Acionada diretamente pelo SNS.
  * **Lambda de Pagamento:** Acionada diretamente pelo SNS.
  * **Lambda de Notificação:** Acionada diretamente pelo SNS.
  * **Fila SQS + Lambda de Fraude:** Uma fila SQS receberá a mensagem do SNS, que será então processada por uma Lambda, simulando uma tarefa mais demorada.

#### **Pré-requisitos**

  * Conta AWS ativa com permissões para SNS, SQS, Lambda e IAM.
  * Familiaridade básica com os serviços AWS.

-----

### **Parte 1: Criação das Filas SQS (Análise de Fraude)**

Começaremos pela ponta da nossa arquitetura: as filas para a análise de fraude.

1.  Acesse o serviço **Amazon SQS**.
2.  **Criar a Dead-Letter Queue (DLQ):**
      * Clique em **Criar fila**.
      * **Tipo:** `Padrão`.
      * **Nome:** `seunome-fila-fraude-analise-dlq`
      * Clique em **Criar fila**.
3.  **Criar a Fila Principal de Análise de Fraude:**
      * Clique novamente em **Criar fila**.
      * **Nome:** `seunome-fila-fraude-analise`
      * Role até **Fila de mensagens mortas (Dead-letter queue)**.
          * Marque **Habilitado**.
          * **ARN:** Selecione o ARN da DLQ que você acabou de criar (`seunome-fila-fraude-analise-dlq`).
          * **Número máximo de recebimentos:** `3`.
      * Clique em **Criar fila**.

-----

### **Parte 2: Criação do Tópico de Notificação (SNS)**

Este tópico será o "distribuidor" central de mensagens.

1.  Acesse o serviço **Amazon SNS**.
2.  No menu esquerdo, clique em **Tópicos** e depois em **Criar tópico**.
3.  **Tipo:** Selecione `Padrão`.
4.  **Nome:** `seunome-topico-pedidos-ecommerce`
5.  Mantenha as outras configurações padrão e clique em **Criar tópico**.

-----

### **Parte 3: Configuração das Permissões (IAM Roles)**

Cada Lambda precisa de permissões para executar e enviar logs.

1.  Acesse o serviço **IAM**.
2.  **Criar Role para Lambdas Genéricas:**
      * Clique em **Funções \> Criar função**.
      * **Tipo de entidade confiável:** `Serviço da AWS`.
      * **Caso de uso:** `Lambda`. Clique em **Avançar**.
      * **Adicionar permissões:** Procure e adicione a política `AWSLambdaBasicExecutionRole`.
      * **Nome da função:** `seunome-LambdaRole-SNS-Generic`
      * Clique em **Criar função**.
3.  **Criar Role para a Lambda de Fraude (com acesso SQS):**
      * Repita os passos acima, mas adicione **duas** políticas de permissão:
        1.  `AWSLambdaBasicExecutionRole`
        2.  `AmazonSQSFullAccess` (Em produção, as permissões seriam mais restritas).
      * **Nome da função:** `seunome-LambdaRole-SQS-Fraude`
      * Clique em **Criar função**.

-----

### **Parte 4: Criação das Funções Lambda**

Vamos criar as quatro funções que farão o processamento. Acesse o serviço **AWS Lambda** e clique em **Criar função**.

#### **4.1. Lambda "Atualizar Inventário"**

1.  **Nome da função:** `seunome-lambda-inventario`
2.  **Tempo de execução:** `Python 3.12`.
3.  **Função de execução:** Selecione **Usar uma função existente** e escolha `seunome-LambdaRole-SNS-Generic`.
4.  Clique em **Criar função**.
5.  No editor de código, substitua o conteúdo por:
    ```python
    import json

    def lambda_handler(event, context):
        print("Recebido evento para ATUALIZAR INVENTÁRIO:")
        print(json.dumps(event))
        # Logica para atualizar inventário (simulada)
        message_attributes = event['Records'][0]['Sns']['MessageAttributes']
        order_id = message_attributes.get('OrderID', {}).get('Value', 'N/A')
        print(f"Inventário atualizado para o pedido: {order_id}")
        return {
            'statusCode': 200,
            'body': json.dumps(f'Inventário atualizado para pedido {order_id}')
        }
    ```
6.  Clique em **Deploy**.

#### **4.2. Lambda "Processar Pagamento"**

1.  Crie uma nova função com o nome `seunome-lambda-pagamento`.
2.  Use a mesma role: `seunome-LambdaRole-SNS-Generic`.
3.  No editor de código, cole:
    ```python
    import json

    def lambda_handler(event, context):
        print("Recebido evento para PROCESSAR PAGAMENTO:")
        print(json.dumps(event))
        # Logica para processar pagamento aqui (simulada)
        message_attributes = event['Records'][0]['Sns']['MessageAttributes']
        order_id = message_attributes.get('OrderID', {}).get('Value', 'N/A')
        payment_type = message_attributes.get('PaymentType', {}).get('Value', 'N/A')
        print(f"Pagamento do tipo '{payment_type}' processado para o pedido: {order_id}")
        return {
            'statusCode': 200,
            'body': json.dumps(f'Pagamento processado para pedido {order_id}')
        }
    ```
4.  Clique em **Deploy**.

#### **4.3. Lambda "Notificar Cliente"**

1.  Crie uma nova função com o nome `seunome-lambda-notificacao-cliente`.
2.  Use a mesma role: `seunome-LambdaRole-SNS-Generic`.
3.  No editor de código, cole:
    ```python
    import json

    def lambda_handler(event, context):
        print("Recebido evento para NOTIFICAR CLIENTE:")
        print(json.dumps(event))
        # Logica para notificar cliente (simulada)
        message_attributes = event['Records'][0]['Sns']['MessageAttributes']
        order_id = message_attributes.get('OrderID', {}).get('Value', 'N/A')
        customer_email = message_attributes.get('CustomerEmail', {}).get('Value', 'N/A')
        print(f"Notificação enviada para {customer_email} sobre o pedido: {order_id}")
        return {
            'statusCode': 200,
            'body': json.dumps(f'Notificação enviada para pedido {order_id}')
        }
    ```
4.  Clique em **Deploy**.

#### **4.4. Lambda "Analisar Fraude"**

1.  Crie uma nova função com o nome `seunome-lambda-analise-fraude`.
2.  **Função de execução:** Use a role com permissão SQS: `seunome-LambdaRole-SQS-Fraude`.
3.  No editor de código, cole:
    ```python
    import json

    def lambda_handler(event, context):
        print("Recebido evento da SQS para ANÁLISE DE FRAUDE:")
        for record in event['Records']:
            # A mensagem da SQS contém a mensagem original do SNS
            sns_message_body = json.loads(record['body'])
            original_sns_message = json.loads(sns_message_body['Message'])
            message_attributes = sns_message_body.get('MessageAttributes', {})

            print(f"Mensagem original do SNS: {json.dumps(original_sns_message)}")
            print(f"Atributos da mensagem: {json.dumps(message_attributes)}")

            order_id = message_attributes.get('OrderID', {}).get('Value', 'N/A')
            transaction_value = float(message_attributes.get('TransactionValue', {}).get('Value', 0))

            print(f"Analisando fraude para o pedido: {order_id} com valor: {transaction_value}")

            # Simular falha para testar DLQ (descomente para testar)
            # if transaction_value > 1000:
            #     raise Exception("Valor da transação muito alto, enviando para DLQ!")

        return {
            'statusCode': 200,
            'body': json.dumps('Análise de fraude concluída')
        }
    ```
4.  Clique em **Deploy**.
5.  **Adicionar o Gatilho SQS:**
      * Na página da função, clique em **Adicionar gatilho**.
      * **Fonte:** Selecione `SQS`.
      * **Fila do SQS:** `seunome-fila-fraude-analise`.
      * **Tamanho do lote:** `1`.
      * Clique em **Adicionar**.

-----

### **Parte 5: Conectando Tudo com Filtros de Assinatura SNS**

Acesse o seu tópico SNS (`seunome-topico-pedidos-ecommerce`), vá para a aba **Assinaturas** e clique em **Criar assinatura**.

#### **5.1. Inscrever a Lambda de Inventário**

  * **Protocolo:** `AWS Lambda`.
  * **Endpoint:** ARN da `seunome-lambda-inventario`.
  * Marque **Política de filtro de assinatura**.
  * Cole o JSON:
    ```json
    {
       "EventType": ["OrderPlaced", "InventoryCheckRequired"]
    }
    ```
  * Clique em **Criar assinatura**.

#### **5.2. Inscrever a Lambda de Pagamento**

  * **Protocolo:** `AWS Lambda`.
  * **Endpoint:** ARN da `seunome-lambda-pagamento`.
  * **Política de filtro:**
    ```json
    {
       "EventType": ["OrderPlaced"],
       "PaymentType": ["CreditCard", "Boleto"]
    }
    ```
  * Clique em **Criar assinatura**.

#### **5.3. Inscrever a Lambda de Notificação**

  * **Protocolo:** `AWS Lambda`.
  * **Endpoint:** ARN da `seunome-lambda-notificacao-cliente`.
  * **Política de filtro:**
    ```json
    {
       "EventType": ["OrderConfirmed", "OrderShipped"]
    }
    ```
  * Clique em **Criar assinatura**.

#### **5.4. Inscrever a Fila SQS de Fraude**

  * **Protocolo:** `Amazon SQS`.
  * **Endpoint:** ARN da `seunome-fila-fraude-analise`.
  * **Política de filtro:**
    ```json
    {
       "EventType": ["OrderPlaced"],
       "TransactionValue": [{"numeric": [">", 500]}]
    }
    ```
  * Clique em **Criar assinatura**.

-----

### **Parte 6: Testando a Arquitetura**

Vamos enviar uma mensagem que corresponda a alguns dos nossos filtros.

1.  No seu tópico SNS, clique em **Publicar mensagem**.
2.  **Corpo da mensagem:**
    ```json
    {
      "pedido_id": "PEDIDO-123",
      "cliente_id": "CLIENTE-XYZ",
      "itens": [
        {"produto_id": "PROD-A", "quantidade": 2}
      ]
    }
    ```
3.  **Atributos da mensagem (MUITO IMPORTANTE):** Adicione os seguintes atributos:

| Tipo | Nome | Valor |
| :--- | :--- | :--- |
| `String` | `EventType` | `OrderPlaced` |
| `String` | `OrderID` | `PEDIDO-123` |
| `String` | `PaymentType` | `CreditCard` |
| `String` | `CustomerEmail`| `cliente@example.com` |
| `Number` | `TransactionValue` | `750` |

4.  Clique em **Publicar mensagem**.

-----

### **Parte 7: Verificação nos Logs (CloudWatch)**

1.  Acesse o **CloudWatch** e vá para **Grupos de logs**.
2.  **Verifique os logs:**
      * `/aws/lambda/seunome-lambda-inventario`: **DEVE** ter um novo log.
      * `/aws/lambda/seunome-lambda-pagamento`: **DEVE** ter um novo log.
      * `/aws/lambda/seunome-lambda-analise-fraude`: **DEVE** ter um novo log.
      * `/aws/lambda/seunome-lambda-notificacao-cliente`: **NÃO DEVE** ter um novo log.

-----

### **Parte 8: Limpeza dos Recursos**

1.  Exclua as **assinaturas** do tópico SNS.
2.  Exclua o **tópico SNS**.
3.  Exclua as **filas SQS** (a principal e a DLQ).
4.  Exclua as quatro **funções Lambda**.
5.  Exclua as duas **funções IAM**.
