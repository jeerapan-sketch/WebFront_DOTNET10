# See https://aka.ms/customizecontainer to learn how to customize your debug container
# and how Visual Studio uses this Dockerfile.

# Runtime
FROM mcr.microsoft.com/dotnet/aspnet:10.0-noble AS base
# Apply the APT security fix until it is included in the upstream runtime image.
USER root
RUN apt-get -o Acquire::Retries=0 update \
    && apt-get -o Acquire::Retries=0 install -y --no-install-recommends --only-upgrade apt libapt-pkg6.0t64 \
    && dpkg --compare-versions "$(dpkg-query -W -f='${Version}' apt)" ge 2.8.4ubuntu0.1 \
    && rm -rf /var/lib/apt/lists/*
USER $APP_UID
WORKDIR /app

EXPOSE 9999
ENV ASPNETCORE_URLS=http://+:9999

# Build
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG BUILD_CONFIGURATION=Release

WORKDIR /src

# Copy project file first (for Docker layer cache)
COPY ["WebImportExcel/WebImportExcel.csproj", "WebImportExcel/"]

# Restore packages
RUN dotnet restore "WebImportExcel/WebImportExcel.csproj"

# Copy only the API project. Documentation and deployment assets must not be
# included in the application image even when they exist in the Git checkout.
COPY ["WebImportExcel/", "WebImportExcel/"]

# Build project
WORKDIR /src/WebImportExcel

RUN dotnet build "WebImportExcel.csproj" \
    -c $BUILD_CONFIGURATION \
    -o /app/build

# Publish
FROM build AS publish
ARG BUILD_CONFIGURATION=Release

RUN dotnet publish "WebImportExcel.csproj" \
    -c $BUILD_CONFIGURATION \
    -o /app/publish \
    /p:UseAppHost=false

# Runtime image
FROM base AS final
WORKDIR /app

COPY --from=publish /app/publish .

ENTRYPOINT ["dotnet", "WebImportExcel.dll"]
