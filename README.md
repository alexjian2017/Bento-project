# Bento-project


MYSQL database:

CREATE TABLE user_data (
  id INT NOT NULL AUTO_INCREMENT,
  u_date datetime NOT NULL,
  name VARCHAR(200) NOT NULL,
  price int NOT NULL,
  content VARCHAR(1000) ,
  buyer VARCHAR(200) NOT NULL,
  paid BOOL,
  PRIMARY KEY (id)
);

CREATE TABLE user_email (
  name VARCHAR(200) NOT NULL,
  email VARCHAR(1000) NOT NULL,
  PRIMARY KEY (name)
);
