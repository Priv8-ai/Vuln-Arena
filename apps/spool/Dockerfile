FROM golang:1.22-alpine AS build
WORKDIR /src
COPY main.go go.mod ./
RUN go build -o /spool main.go
FROM alpine:3.20
RUN apk add --no-cache curl
WORKDIR /app
COPY --from=build /spool /app/spool
COPY static /app/static
RUN mkdir -p /data && echo 'ARENA{spool_data_flag}' > /data/flag.txt
EXPOSE 80
CMD ["/app/spool"]
