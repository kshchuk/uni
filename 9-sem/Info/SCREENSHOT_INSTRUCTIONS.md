# Інструкції для створення скріншотів до звіту

## Автоматично згенеровані дані

Текстові виводи збережені в `docs/report-screenshots/`:
- docker-compose-status.txt
- k8s-pods.txt
- k8s-services.txt
- auth-tables.txt
- catalog-tables.txt
- orders-tables.txt
- data-stats.txt
- top-customers.txt
- managers.txt

## Скріншоти, які потрібно зробити вручну

### 1. ER Діаграми
Файли вже є в `docs/images/`:
- Auth_ER.png
- Catalog_ER.png
- Orders_ER.png
- Payments_ER.png
- DWH_ER.png

### 2. DBML діаграми з dbdiagram.io

1. Відкрийте https://dbdiagram.io
2. Завантажте кожен DBML файл з `docs/db/`:
   - auth_mysql.dbml
   - catalog_mysql.dbml
   - orders_mysql.dbml
   - payments_mysql.dbml
   - dwh_postgres.dbml
3. Зробіть скріншот кожної діаграми
4. Збережіть як:
   - dbml-auth-diagram.png
   - dbml-catalog-diagram.png
   - dbml-orders-diagram.png
   - dbml-payments-diagram.png
   - dbml-dwh-diagram.png

### 3. Конвертація DBML в SQL

Зробіть скріншот терміналу під час виконання:
```bash
dbml2sql auth_mysql.dbml --mysql -o ../../database/init/01_auth_schema.sql
```

### 4. Docker Compose

**Скріншот 1: docker-compose up -d**
```bash
docker-compose up -d
```

**Скріншот 2: docker-compose ps**
```bash
docker-compose ps
```

**Скріншот 3: Docker Desktop**
- Відкрийте Docker Desktop
- Перейдіть до "Containers"
- Покажіть всі контейнери techmarket

**Скріншот 4: Docker Volumes**
- В Docker Desktop перейдіть до "Volumes"
- Покажіть всі volumes techmarket

### 5. Генератор даних

**Скріншот: Виконання generate_test_data.py**
```bash
python3 database/data/generate_test_data.py
```

### 6. Adminer - Web UI

**Відкрийте:** http://localhost:8080

**Скріншот 1: Головна сторінка Adminer**

**Скріншот 2-6: Підключення до кожної БД**
- Підключіться до auth-db (System: MySQL, Server: auth-db або localhost:3306)
- Зробіть скріншот списку таблиць
- Повторіть для catalog-db, orders-db, payments-db
- Для DWH: System: PostgreSQL, Server: dwh-db або localhost:5432

**Скріншот 7-10: Дані в таблицях**
- auth_users - покажіть список користувачів
- products - покажіть список товарів
- orders - покажіть замовлення з total_amount
- customers - покажіть список клієнтів

**Скріншот 11: Результат складного запиту**
```sql
SELECT 
    c.first_name,
    c.last_name,
    c.email,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status IN ('paid', 'shipped')
GROUP BY c.id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC
LIMIT 5;
```

**Скріншот 12: Структура таблиці з Foreign Keys**
- Відкрийте таблицю `order_items`
- Покажіть структуру з foreign keys до `orders`

### 7. Kubernetes

**Скріншот 1: kubectl apply namespace**
```bash
kubectl apply -f k8s/00-namespace-secrets.yaml
```

**Скріншот 2: ConfigMaps створення**
```bash
./k8s/create-configmaps.sh
```

**Скріншот 3: kubectl apply mysql**
```bash
kubectl apply -f k8s/mysql/
```

**Скріншот 4: kubectl get pods**
```bash
kubectl get pods -n techmarket
```

**Скріншот 5: kubectl get svc**
```bash
kubectl get svc -n techmarket
```

**Скріншот 6: kubectl get pvc**
```bash
kubectl get pvc -n techmarket
```

**Скріншот 7: kubectl describe pod**
```bash
kubectl describe pod auth-db-0 -n techmarket
```

**Скріншот 8: SHOW TABLES в K8s**
```bash
kubectl exec -it auth-db-0 -n techmarket -- \
  mysql -u auth_user -pauth_pass auth_db -e "SHOW TABLES;"
```

### 8. Kubernetes Dashboard (якщо встановлено)

```bash
kubectl proxy
```

Відкрийте: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

**Скріншот 1: Overview namespace techmarket**

**Скріншот 2: Pods list**

**Скріншот 3: Services list**

**Скріншот 4: Storage (PVC)**

### 9. Структура SQL файлів

**Скріншот: Фрагмент згенерованого SQL**
Відкрийте `database/init/01_auth_schema.sql` та покажіть:
- CREATE TABLE statements
- Foreign Keys
- Indexes

### 10. Код генератора даних

**Скріншот: Фрагмент generate_test_data.py**
Покажіть функцію `populate_orders_db` або іншу

## Рекомендації

1. Використовуйте інструмент для створення скріншотів:
   - Linux: `gnome-screenshot`, `flameshot`
   - macOS: Cmd+Shift+4
   - Windows: Win+Shift+S

2. Розмір скріншотів:
   - Оптимальна ширина: 1200-1600px
   - Формат: PNG для чіткості

3. Назви файлів:
   - Використовуйте описові назви
   - Наприклад: `01-dbml-to-sql-conversion.png`

4. Організація:
   - Збережіть всі скріншоти в `docs/report-screenshots/`
   - Додайте їх до звіту в відповідні місця

## Перелік необхідних скріншотів

- [ ] ER діаграми (5 штук) - вже є в docs/images/
- [ ] DBML діаграми з dbdiagram.io (5 штук)
- [ ] Конвертація DBML в SQL (1 скріншот терміналу)
- [ ] docker-compose up (1 скріншот)
- [ ] docker-compose ps (1 скріншот)
- [ ] Docker Desktop containers (1 скріншот)
- [ ] Docker Desktop volumes (1 скріншот)
- [ ] Генератор даних виконання (1 скріншот)
- [ ] Adminer головна (1 скріншот)
- [ ] Adminer таблиці для кожної БД (5 скріншотів)
- [ ] Adminer дані в таблицях (4-5 скріншотів)
- [ ] Adminer складний запит (1 скріншот)
- [ ] kubectl apply commands (3-4 скріншоти)
- [ ] kubectl get resources (3-4 скріншоти)
- [ ] SQL файл структура (1 скріншот)

**Всього: ~35-40 скріншотів**

## Швидкі команди для тестування

```bash
# Перевірка Docker
docker-compose ps
docker ps

# Перевірка K8s
kubectl get all -n techmarket
kubectl get pods -n techmarket -o wide

# Перевірка даних
docker-compose exec orders-db mysql -u orders_user -porders_pass orders_db -e "SELECT COUNT(*) FROM orders;"

# Відкрити Adminer
open http://localhost:8080  # macOS
xdg-open http://localhost:8080  # Linux
start http://localhost:8080  # Windows
```
