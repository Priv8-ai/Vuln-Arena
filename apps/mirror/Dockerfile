FROM golang:1.22-alpine AS build
WORKDIR /src
COPY main.go .
RUN go build -o /mirror main.go
FROM alpine:3.20
COPY --from=build /mirror /mirror
COPY static /static
EXPOSE 80
CMD ["/mirror"]
