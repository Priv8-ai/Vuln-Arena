FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY apps/quorum/Quorum.csproj .
RUN dotnet restore
COPY apps/quorum/Program.cs .
RUN dotnet publish -c Release -o /out --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine
WORKDIR /app
COPY --from=build /out/ .
COPY apps/quorum/wwwroot ./wwwroot
COPY shared/ui/chrome.css ./wwwroot/assets/chrome.css
COPY shared/ui/chrome.js ./wwwroot/assets/chrome.js
RUN mkdir -p /app/exports /app/private \
 && printf 'Quarterly approval sample\n' > /app/exports/sample.txt \
 && printf 'tenant-signing-context=quorum-run-fixture\n' > /app/private/runtime.conf \
 && addgroup -S arena && adduser -S arena -G arena \
 && chown -R arena:arena /app
USER arena
EXPOSE 8080
ENTRYPOINT ["dotnet", "Quorum.dll"]
