CREATE TABLE IF NOT EXISTS `utenti` (
    `chat_id`  INT            PRIMARY KEY,
    `username` VARCHAR(64)    NULL,
    `nome`     VARCHAR(128)   NULL,
    `banned`   TINYINT(1)     DEFAULT 0,
    `count`    TINYINT(1)     DEFAULT 0
) DEFAULT CHARSET=utf8;
