# scrapy_mafengwo

爬景点
国家 --> 地区 --> 景点 --> 景点信息


DB

country
+-------------+--------------+------+-----+-------------------+----------------+
| Field       | Type         | Null | Key | Default           | Extra          |
+-------------+--------------+------+-----+-------------------+----------------+
| id          | int(11)      | NO   | PRI | NULL              | auto_increment |
| cn_name     | varchar(25)  | NO   |     |                   |                |
| en_name     | varchar(25)  | NO   |     |                   |                |
| state       | varchar(10)  | NO   |     |                   |                |
| url_id      | varchar(100) | NO   |     |                   |                |
| create_time | timestamp    | NO   |     | CURRENT_TIMESTAMP |                |
+-------------+--------------+------+-----+-------------------+----------------+

