import boto3
import sys
import argparse
from botocore.exceptions import ClientError


def gerar_credenciais_temporarias(role_arn, session_name, duration):
    # Inicializa o cliente STS
    sts_client = boto3.client('sts')

    try:
        # Solicita as credenciais temporárias
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name,
            DurationSeconds=duration
        )

        # Exibe as credenciais temporárias
        credentials = response['Credentials']
        print(f"AWS Access Key ID: {credentials['AccessKeyId']}")
        print(f"AWS Secret Access Key: {credentials['SecretAccessKey']}")
        print(f"AWS Session Token: {credentials['SessionToken']}")

    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError' and 'DurationSeconds exceeds the MaxSessionDuration' in \
                e.response['Error']['Message']:
            print("[ERRO] A duração solicitada excede o limite de tempo máximo permitido para esta role.")
            print("Por favor, solicite ao administrador da role para aumentar o limite de tempo.")
        else:
            print(f"[ERRO] Falha ao obter credenciais: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gerar credenciais temporárias do AWS STS")
    parser.add_argument('--role-arn', required=True, help='ARN da role a ser assumida')
    parser.add_argument('--session-name', required=True, help='Nome único para a sessão')
    parser.add_argument('--duration', type=int, default=3600, help='Duração em segundos (padrão: 3600 = 1 hora)')

    args = parser.parse_args()

    gerar_credenciais_temporarias(args.role_arn, args.session_name, args.duration)


if __name__ == "__main__":
    main()
