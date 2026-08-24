# Two-Server Qwerty Setup

After installation, use [docs/COMMAND_TUTORIAL.md](docs/COMMAND_TUTORIAL.md) for
every member and staff command, routine operating procedures, and successor
handoff instructions.

## 1. Use one Discord application

Keep the existing Qwerty application and token. Install that same application into both the main and recruitment servers using the install link in the Discord Developer Portal.

On the application's **Bot** page, enable:

- **Server Members Intent** — required to identify eligible PNMs and notice main-server joins
- **Message Content Intent** — required to read attendance codewords sent by DM

The install link needs the `bot` and `applications.commands` scopes. Give Qwerty these permissions in both servers:

- View Channels
- Send Messages
- Embed Links
- Attach Files
- Read Message History

In the main server, also grant **Manage Roles** and place Qwerty's role above the
new-member role if Qwerty should assign that role after recruitment transitions.

## 2. Prepare the servers

Turn on Discord Developer Mode so you can right-click each server or channel and copy its ID.

In the recruitment server:

1. Create a `Recruitment Team` staff role, or choose another exact name.
2. Confirm the invite-based role is named `PNM`, or configure its exact name.
3. Create a private PNM join-log channel and copy its channel ID.
4. Create a private staff channel for anonymous questions and copy its channel ID.

In the main server:

1. Create or choose the role transitioned members should receive. The default is `New Member`.
2. Create a main-server invite that will remain valid for the transition period.

## 3. Configure Qwerty

Install Python 3.10 or later and the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Keep credentials such as the bot token and Google service-account path in `.env`.
Server IDs, channel IDs, invite settings, and role names live in the ignored
`server_config.json` file. Copy `server_config.example.json` when setting up a
new machine. Environment variables with matching names can override any local
server setting.

The local server configuration should contain:

```json
{
  "MAIN_GUILD_ID": "main-server-id",
  "RECRUITMENT_GUILD_ID": "recruitment-server-id",
  "RECRUITMENT_INTRODUCTIONS_CHANNEL_ID": "introductions-channel-id",
  "RECRUITMENT_RUSH_SCHEDULE_CHANNEL_ID": "rush-schedule-channel-id",
  "RECRUITMENT_FAQ_CHANNEL_ID": "faq-channel-id",
  "ANONYMOUS_QUESTIONS_CHANNEL_ID": "private-recruitment-channel-id",
  "PNM_JOIN_LOG_CHANNEL_ID": "pnm-join-log-channel-id",
  "PNM_ONBOARDING_ROLE": "PNM",
  "MAIN_SERVER_INVITE_URL": "https://discord.gg/your-invite",
  "RECRUITMENT_ADMIN_ROLE": "Recruitment Team",
  "TRANSITION_SOURCE_ROLE": "Accepted PNM",
  "MAIN_NEW_MEMBER_ROLE": "New Member"
}
```

Do not commit `.env`, `server_config.json`, service credentials, or the generated
`data/` directory.

## 4. Start Qwerty

Only one running process should use the token:

```powershell
python bot.py
```

At startup, Qwerty removes stale global slash commands and publishes separate command sets directly to the two configured servers.

## 5. Operate recruitment

1. Test the PNM form with an account that receives the invite-based `PNM` role and confirm its report appears in the join log.
2. Confirm the introductions, rush schedule, and FAQ posts appear after startup; use `/publish-recruitment-info` to refresh them manually.
3. Add events with `/calendar-add`.
4. Open each event's attendance with `/attendance-code-add` and close it afterward with `/attendance-code-remove`.
5. Verify all transitioning PNMs have the configured source role.
6. Test `/transition-invite` with one account.
7. Run `/transition-invite-all confirm:True` only when the group is ready.
8. Follow progress with `/transition-status`.

Runtime records are stored under `data/`. Back up this directory if attendance and transition history must survive a machine move.
