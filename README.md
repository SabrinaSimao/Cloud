# Disciplina de Cloud - Insper 2018.2

## Projeto de Cloud

Diretrizes do projeto:

• O projeto é estritamente individual.

• Cada aluno deverá implementar um microserviço que:

    – Seja distribuído. Pode Utilizar uma infraestrutura de Cloud pública e/ou privada.

    – Seja elástico. Ter a capacidade de criar e destruir instâncias de forma assíncrona.

    – Implemente uma API REST.

• O aluno terá livre escolha sobre as funcionalidades propostas.

• Implementar uma aplicação cliente para consumir o serviço via API.

• Tem que ser migrável para outra nuvem (Não pode usar soluções proprietárias – lock-in).

• Utilizar uma linguagem de programação de livre escolha, embora seja sugerido usar uma que tenha
bibliotecas para manipulação de Cloud prontas.

• Possuir um script de implantação do projeto (charm, image ou script)


Simple application:

Fortune cookie generator: ask and shall receive! A fortune cookie message with a lottery number

• Output example

    Sempre ame o Raul   
    Your lottery numbers are: [9, 17, 38, 46, 53, 59]

## Installation Guide

### DISCLAIMER: 

### *always have your AWS credentials at hand, we will never ask for you to give us any private/public key or credential. Never show your acess key to anyone*

clone this git

cd Cloud/APS/

run installer script

`chmod +x install_local.sh`

`./install_local <number of web servers running> <passkey>`

passkey must be 5 or more characters

![alt text](https://github.com/SabrinaSimao/Cloud/blob/master/img/coffee.png "Go drink some coffee man" ) time! Gotta wait for the load balancer to be up and running in AWS machines.

login to load balancer: you will need the Public DNS from Ec2 dashboard (look for TAG: LoadBalancer)

Note that project_key will be created inside the APS folder

`ssh -i project_key ubuntu@PUBLIC_DNS`

Once inside the load balancer instance, type

`aws configure`

setup internally your AWS credentials (which will be secured on their cloud)

then run

`cd Cloud/APS/`

`python3 load_balancer.py <number of web servers running>`

done!

### Want to run the app?

in your local machine (actually anywhere you have the repo)

`chmod +x fortune`

`./fortune <load_balancer_ip> <command> `

commands are:

    • cookie: generate a fortune cookie
    • lottery: generate a lottery number
    • both: generate both
