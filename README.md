# MEnDec
![Python Logo](https://www.python.org/static/community_logos/python-logo.png "Sample inline image")

Python package for message encryption

# Install

`pip install https://github.com/biojet1/mendec/archive/master.zip`

# Usage

## Generate the secret key piar

`python -m mendec keygen --bits 384 --output SECRET_KEY`

## Extract first key

`python -m mendec pick SECRET_KEY 1 KEY1`

## Extract second key

`python -m mendec pick SECRET_KEY 2 KEY2`

## Using the first key encrypt a message to CYPHER file

`printf 'Attack at Noon' | python -m mendec encrypt KEY1 -o CYPHER`

## Using the second key decrypt the message

`python -m mendec decrypt KEY2 < CYPHER`

`Attack at Noon`

## Using the second key encrypt the message, then the first key to decrypt the message

`printf Acknowledge | python -m mendec encrypt KEY2 | python -m mendec decrypt KEY1`

`Acknowledge`

