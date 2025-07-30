# BandicotaFramManagement App Project
## MSc. Business Software Development #17 CU

Hello everyone,

Thank you for your interest in my MSc. project! My name is Pariwat Paiwong, you can call me Earth. I'm a software engineer from Thailand, and I'd like to share this special master's degree project with you.

## How I discovered this opportunity

I went to study bandicota farms in Phitsanulok, Thailand. In Thailand, some country people eat rats, but only bandicota - this is simple culture. As technology grows up, we don't hunt bandicota anymore, but we develop it into farm systems.

## The pain point I want to share

Farmers have no knowledge about technology and use shared knowledge in groups. I got this pain point from the subject "Requirement Analysis" when I started my Master's in BSD at CU.

In my opinion, farmers should use technology to help their business, not hope on someone or trust some people.

## How I approached the software design

I designed software using knowledge from when I studied the subject "Business Software Design."

The software must connect to internet because in this place internet is not stable, and it should share data between farms.

The software should calculate inbreeding rate to stop abnormal bandicota.

## My development experience I'd like to share

I used Flet to develop because I have knowledge in Flutter before.

For the base source code to calculate inbreeding, I used Python to develop sample of tabular method calculation.

In my software, if data is larger, this becomes slow - following data and device is one effect.

## What I hope to share with you

I hope this project can be a show or sample case for those who need to learn and know what performance of Flet is like. I want to share this experience so others can learn from what I've discovered during this journey.

## Run the app

1.start app 1 time for create database
2.run init-DB-farm.sql
3.run init-DB-farm_ad.sql

### uv

Run as a desktop app:

```
uv run flet run
```

Run as a web app:

```
uv run flet run --web
```

### Poetry

Install dependencies from `pyproject.toml`:

```
poetry install
```

Run as a desktop app:

```
poetry run flet run
```

Run as a web app:

```
poetry run flet run --web
```

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/getting-started/).

## Build the app

### Android

```
flet build apk -v
```

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```
flet build ipa -v
```

For more details on building and signing `.ipa`, refer to the [iOS Packaging Guide](https://flet.dev/docs/publish/ios/).

### macOS

```
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).
