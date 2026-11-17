FROM eclipse-temurin:17-jdk-jammy AS build
WORKDIR /src
COPY Main.java .
RUN javac Main.java && jar cfe desk.jar Main Main.class
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=build /src/desk.jar /app/desk.jar
RUN mkdir -p /app/data && echo 'ARENA{desk_file_read}' > /app/data/flag.txt
EXPOSE 80
CMD ["java", "-jar", "/app/desk.jar"]
