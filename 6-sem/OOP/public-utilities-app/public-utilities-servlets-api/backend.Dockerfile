FROM maven:3-adoptopenjdk-16 AS build

WORKDIR /app

COPY pom.xml .

RUN mvn dependency:go-offline -B

COPY src /app/src

RUN mvn package

FROM adoptopenjdk:16-jre-hotspot

COPY --from=build /app/target/public-utilities-servlets-api-1.0-SNAPSHOT.war /usr/local/lib/public-utilities-servlets-api.war

CMD ["java", "-jar", "/usr/local/lib/public-utilities-servlets-api.war"]
