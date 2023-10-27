# acr-cpp-member

Arquivo config.json

```json
{
  "rules": [
    "MEMBER_NOT_INITIALIZED_IN_HEADER",
    "MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE"
  ]
}
```

Dependencias

- ctags

```shell
sudo apt-get install universal-ctags
```

# RULES

### MEMBER_NOT_INITIALIZED_IN_HEADER

Verifica os atributos presentes no header e caso possua inicialização, gera um comentario

### MEMBER_PRIVATE_HAS_PREFIX_UNDERLINE

Verifica os atributos private presentes no header e caso não exista o prefixo `_`, gera um comentario
