# MEnDec

![MEnDec Logo](mendec.png)

Python package for Text **M**essage **EN**cryption and **DE**cryption

[![GitHub stars](https://img.shields.io/github/stars/biojet1/mendec.svg?style=social)](https://github.com/biojet1/mendec/stargazers) [![PyPI version](https://img.shields.io/pypi/v/mendec.svg)](https://pypi.org/project/mendec/) [![Workflow Name](https://github.com/biojet1/mendec/actions/workflows/tests.yml/badge.svg)](https://github.com/biojet1/mendec/actions/workflows/tests.yml) [![Workflow Name](https://github.com/biojet1/mendec/actions/workflows/publish.yml/badge.svg)](https://github.com/biojet1/mendec/actions/workflows/publish.yml)

# Install

```
pip install mendec
```

# Usage

## Generate the secret key piar

```
> python -m mendec keygen --bits 384 SECRET_KEY
```

## Extract first key

```
> python -m mendec pick SECRET_KEY 1 KEY1
```

## Extract second key

```
> python -m mendec pick SECRET_KEY 2 KEY2
```

## Using the first key encrypt a message to CYPHER file

```
> printf 'Attack at Noon' | python -m mendec encrypt KEY1 - CYPHER
```

## Using the second key decrypt the message

```
> python -m mendec decrypt KEY2 - < CYPHER
Attack at Noon
```

## Using the second key encrypt the message, then the first key to decrypt the message

```
> printf Acknowledge | python -m mendec encrypt KEY2 | python -m mendec decrypt KEY1
Acknowledge
```

## Create a script pair encryptor ←→ decryptor

Create the python script pair:

```
> python -m mendec script SECRET_KEY alice bob
> chmod +x alice bob
```

Alice sends a message using **e** command

```
> echo Where to meet | ./alice e > cypher
```

Bob decrypts the message using **d** command

```
> ./bob d < cypher
> Where to meet
```

Bob send message using **e** command

```
> echo El dorado | ./bob e > cypher
```

Alice decrypts the message using **d** command

```
> ./alice d < cypher
> El dorado
```
