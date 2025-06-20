# MEnDec
![MEnDec Logo](mendec.png)
![Python package](https://github.com/biojet1/mendec/workflows/Python%20package/badge.svg)
![Upload Python Package](https://github.com/biojet1/mendec/workflows/Upload%20Python%20Package/badge.svg)

[github.com/biojet1/mendec](https://github.com/biojet1/mendec)
[pypi.org/project/mendec](https://pypi.org/project/mendec/)

Python package for Message ENcryption and DEcryption

# Install
```
pip install mendec
```

# Usage

## Generate the secret key piar
```
> python -m mendec keygen --bits 384 --output SECRET_KEY
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
> printf 'Attack at Noon'" " | python3 -m mendec encrypt -o CYPHER KEY1 -
```

## Using the second key decrypt the message
```
> python3 -m mendec decrypt KEY2 - < CYPHER
Attack at Noon
```

## Using the second key encrypt the message, then the first key to decrypt the message
```
> printf Acknowledge | python3 -m mendec encrypt KEY2 | python3 -m mendec decrypt KEY1
Acknowledge
```

# Usage
