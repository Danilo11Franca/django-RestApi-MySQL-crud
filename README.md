# CRUD REST API feito em Django

## Como rodar

Para rodar o projeto execute o comando: `python manage.py migrate` e `python manage.py runserver`

A rota para a API é: ```/api/products```

## Banco de dados MySQL

### O banco de dados foi baseado no Esquema abaixo:

```sql
CREATE SCHEMA IF NOT EXISTS `nodis_devops_test`
DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `nodis_devops_test`.`product` (
`product_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
`title` VARCHAR(32) NOT NULL,
`sku` VARCHAR(32) NOT NULL,
`description` VARCHAR(1024) NULL,
`price` DECIMAL(12,2)NOT NULL DEFAULT 0.00,
`created` DATETIME NOT NULL,
`last_updated` DATETIME NULL,
PRIMARY KEY (`product_id`),
UNIQUE INDEX (`sku` ASC),
INDEX (
`created`
),
INDEX (`last_updated`)
);

CREATE TABLE IF NOT EXISTS `nodis_devops_test`.`product_barcode` (
`product_id` INT UNSIGNED NOT NULL,
`barcode` VARCHAR(32) NOT NULL,
PRIMARY KEY (`product_id`, `barcode`),
UNIQUE INDEX (`barcode`)
);

CREATE TABLE IF NOT EXISTS `nodis_devops_test`.`product_attribute` (
`product_id` INT UNSIGNED NOT NULL,
`name` VARCHAR(16) NOT NULL,
`value` VARCHAR(32) NOT NULL,
PRIMARY KEY (`product_id`, `name`)
);
```

---

### Para popular o banco de dados execute o comando: `python manage.py seed`

Esse comando insere 10 produtos por padrão, para inserir mais ou menos execute o comando `python manage.py seed --products <quantidade>`

### Para rodar os testes execute o comando `python manage.py test`

## Tarefas não realizadas ou incompletas

- Não foi feito o deploy no Kubernetes
- Teste unitário incompleto
- Script de popular o banco de dados inserindo valores default para alguns campos