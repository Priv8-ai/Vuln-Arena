FROM rust:1.88-alpine AS build
RUN apk add --no-cache musl-dev pkgconfig
WORKDIR /src
COPY apps/harbor/Cargo.toml .
COPY apps/harbor/src ./src
RUN cargo build --release

FROM alpine:3.20
RUN addgroup -S arena && adduser -S arena -G arena
WORKDIR /app
COPY --from=build /src/target/release/harbor /app/harbor
COPY apps/harbor/public /app/public
COPY shared/ui/chrome.css /app/public/assets/chrome.css
COPY shared/ui/chrome.js /app/public/assets/chrome.js
RUN mkdir -p /app/data /app/private \
 && printf 'Welcome to Tidevault.\n' > /app/data/welcome.txt \
 && printf 'storage_scope=harbor-private\n' > /app/private/runtime.conf \
 && chown -R arena:arena /app
USER arena
EXPOSE 8080
CMD ["/app/harbor"]
