# Telegram Join Gate Bot

A Telegram group Join Gate Bot.

## Features

- Automatically restricts new members.
- Requires users to join a Telegram channel.
- Verify button checks channel membership.
- Automatically restores messaging permission after verification.
- Admins are automatically ignored.
- Supports /gate and /ungate commands.

## Environment Variables

BOT_TOKEN=Your Telegram Bot Token

OWNER_ID=Your Telegram User ID

CHANNEL_USERNAME=Your Channel Username

CHANNEL_ID=Your Channel ID

## Required Bot Permissions

The bot must be an administrator in the group.

Required permission:

- Restrict members

For reliable channel membership checking, make the bot an administrator in the required channel as well.

## Commands

/gate

/ungate USER_ID
