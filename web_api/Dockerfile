FROM mcr.microsoft.com/dotnet/aspnet:7.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /src
COPY ["nuget.config", "."]
COPY ["web_api.csproj", "."]
RUN dotnet restore "./web_api.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "web_api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "web_api.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "web_api.dll"]