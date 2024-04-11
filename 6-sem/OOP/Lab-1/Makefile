postgres:
	docker run --name postgres_oop -p 5431:5432 -e POSTGRES_USER=$(user) -e POSTGRES_PASSWORD=$(password) -d postgres

createdb:
	docker exec -it postgres_oop createdb --username=$(user) --owner=$(owner) oop_lab_1_db

dropdb:
	docker exec -it postgres_oop dropdb --username=$(user) --owner=$(owner) oop_lab_1_db
