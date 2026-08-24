# Qwerty Command and Officer Handoff Guide

This handbook explains every Qwerty command currently loaded in the main and
recruitment Discord servers. It is written for members, recruitment staff, and
future officers who may inherit the project without knowing its history.

## 1. How Qwerty is divided

Qwerty uses one Discord application and one running process in two servers.
Commands are registered separately, so a command intended for one server does
not appear in the other.

| Server | Purpose | Command style |
|---|---|---|
| Main | Chapter operations, resources, birthdays, roles, and games | `/slash` and legacy `!prefix` commands |
| Recruitment | Calendar, PNM attendance, anonymous questions, and member transition | `/slash` commands plus attendance codewords sent by DM |

Slash commands show a form after typing `/`. Parameters labeled optional may be
left blank. Prefix commands must be typed exactly as shown, including the `!`.

## 2. Recruitment server tutorial

### Joining and the PNM form

When a recruitment member receives the invite-based `PNM` role, Qwerty sends a
DM containing a **Complete PNM Form** button. This works whether the role is
already present during the join event or is assigned moments afterward. The
form asks for first name, last name, phone number, Pitt email, and the member's
current Discord username. Qwerty checks the phone and email formats and
confirms the username matches the submitting Discord account.

Once all fields are valid, Qwerty immediately posts a report in the private
channel configured by `PNM_JOIN_LOG_CHANNEL_ID`. There is no staff approval
step and Qwerty does not add or remove roles. It stores only completion status,
timestamps, and the report message ID locally; the name, phone number, and
email remain solely in the private join-log message.

### Commands available to every recruitment member

#### `/calendar`

Shows up to ten future recruitment events in chronological order. Times render
in each viewer's local Discord timezone.

Example:

```text
/calendar
```

#### `/ask-anonymously question:<text>`

Sends a question to the configured private staff channel. The public channel
does not receive the question, and the confirmation is visible only to the
submitter. Qwerty does not save or forward the submitter's identity.

Example:

```text
/ask-anonymously question:What should I wear to the professional event?
```

The submitter receives a reference code. Staff see the question and reference
code, but not the sender.

#### Attendance check-in by DM

Recruitment attendance is not a slash command for PNMs. At an event:

1. A recruitment leader announces the active codeword in person.
2. The PNM opens a direct message with Qwerty.
3. The PNM sends only the codeword.
4. Qwerty confirms the check-in.

Each Discord account can check in only once per event. Codewords are not
case-sensitive. A PNM must still belong to the recruitment server.

### Recruitment staff commands

These commands require either Discord's **Manage Server** permission or the
role named by `RECRUITMENT_ADMIN_ROLE` (normally `Recruitment Team`). Responses
containing codes or administrative information are private to the staff user.

#### `/pnm-form-send member:<member>`

Sends or resends the private PNM form. Use this for a member who
joined before the feature was enabled or after they reopen direct messages.

```text
/pnm-form-send member:@Alex
```

The selected member must have the role configured by `PNM_ONBOARDING_ROLE`.

#### `/pnm-form-send-all`

Resends the private PNM form to every non-bot member with the role configured by
`PNM_ONBOARDING_ROLE`. Members who have already completed the form are skipped.
After processing, Qwerty privately reports the number sent, skipped, and failed.

```text
/pnm-form-send-all
```

#### `/publish-recruitment-info`

Creates any missing introductions, rush schedule, and FAQ posts, or updates
Qwerty's existing posts in place. Qwerty runs the same sync automatically at
startup, so this command is mainly useful after changing the writeups while the
bot is already online.

```text
/publish-recruitment-info
```

The private response reports whether each post was created, updated, not
configured, or failed. The bot stores only its own message IDs and never clears
other messages from those channels.

#### `/calendar-add`

Adds an event to the recruitment calendar.

Parameters:

| Parameter | Required | Format |
|---|---:|---|
| `name` | Yes | Event name, up to 100 characters |
| `date` | Yes | `YYYY-MM-DD` |
| `time` | Yes | 24-hour `HH:MM` in `QWERTY_TIMEZONE` |
| `location` | No | Up to 200 characters |
| `details` | No | Up to 700 characters |

Example for 7:30 PM:

```text
/calendar-add name:Professional Night date:2026-09-10 time:19:30 location:WPU 630 details:Business casual attire
```

Qwerty returns a short event ID. Keep that ID only if the event may need to be
removed; `/calendar-manage` can retrieve it later.

#### `/calendar-manage`

Privately lists every stored event with its event ID, name, date, and time.

```text
/calendar-manage
```

Use this before `/calendar-remove` when the event ID is unknown.

#### `/calendar-remove event_id:<id>`

Permanently removes one calendar event.

```text
/calendar-remove event_id:a1b2c3
```

This does not remove attendance records associated with a similarly named
event; calendar and attendance records are intentionally separate.

#### `/attendance-code-add event:<name> codeword:<word>`

Opens recruitment attendance for an event. The codeword must be one word with
no spaces. Event and codeword matching are case-insensitive.

```text
/attendance-code-add event:Professional Night codeword:network
```

If the same event name already exists, its codeword is replaced while its
internal event ID remains the same. A codeword cannot belong to two events.

#### `/attendance-code-list`

Privately lists all currently active recruitment events and codewords.

```text
/attendance-code-list
```

#### `/attendance-code-remove event:<name>`

Closes attendance for an event. Previously recorded check-ins remain saved.

```text
/attendance-code-remove event:Professional Night
```

Close the code after the attendance window so it cannot be reused later.

#### `/attendance-export`

Downloads all recruitment attendance as `qwerty_attendance.csv`.

```text
/attendance-export
```

The CSV contains event ID, event name, Discord user ID, Discord name, display
name, and timestamp. Store exports according to the chapter's privacy policy.

#### `/transition-invite member:<member>`

Sends the configured main-server invite to one recruitment member and records
whether Discord accepted the DM.

```text
/transition-invite member:@Alex
```

Qwerty skips a member already visible in the main server. A failed DM normally
means the member has server DMs disabled; staff should ask them to enable DMs or
provide the invite through an approved alternative.

#### `/transition-invite-all confirm:<true|false>`

Sends the main-server invite to every eligible recruitment member who:

- Is not a bot;
- Holds the role configured by `TRANSITION_SOURCE_ROLE`;
- Is not already in the main server.

Preview safely without sending:

```text
/transition-invite-all confirm:False
```

Send the batch:

```text
/transition-invite-all confirm:True
```

The recommended source role is `Accepted PNM`. Assign it only after the final
transition list has been approved. Discord still requires each person to click
the invite and voluntarily join.

#### `/transition-status`

Shows totals for joined members, delivered invitations still pending, blocked
DMs, and other delivery failures. It also previews pending member names.

```text
/transition-status
```

When an invited member joins the main server, Qwerty marks the transition as
joined and attempts to assign `MAIN_NEW_MEMBER_ROLE`.

## 3. Main server slash-command tutorial

### General information

#### `/help`

Displays Qwerty's short in-Discord command overview.

#### `/mastersheet`

Posts the configured KTP master spreadsheet link.

#### `/library`

Posts the KTP resource-library link.

#### `/photocircle`

Posts the chapter PhotoCircle invitation.

#### `/eboard`

Displays the executive board roster currently written in `cogs/helper.py`.

#### `/gboard`

Displays the general board roster currently written in `cogs/helper.py`.

Future officers must update the names and links in `cogs/helper.py` when chapter
leadership or resources change.

### Birthdays

#### `/setbirthday date:<MM-DD>`

Saves the invoking member's birthday without a birth year.

```text
/setbirthday date:04-17
```

#### `/mybirthday`

Shows the birthday currently saved for the invoking member.

#### `/removebirthday`

Deletes the invoking member's saved birthday.

#### `/birthdayboard`

Generates and posts an image calendar for the current month with saved member
birthdays. Qwerty also checks birthdays daily at noon Eastern and posts in the
channel configured by `BIRTHDAY_CHANNEL_ID`.

### Main-server attendance

Main attendance is the established Google Sheets workflow and is separate from
recruitment attendance. Its management commands require **Manage Server** or an
`Admin` role. Code lists and confirmations are ephemeral.

#### `/setcode event:<name> new_code:<code>`

Creates or replaces a main-server attendance code.

```text
/setcode event:Chapter Meeting new_code:panther
```

Members DM that code to Qwerty. Qwerty asks a follow-up question and appends the
answer to the configured Google Sheet.

#### `/listcodes`

Privately lists all active main-server attendance codes.

#### `/removecode event:<name>`

Removes a main-server attendance code while leaving existing Sheet rows intact.

If an attendance code maps to `absent`, Qwerty asks for the absence reason and
DMs it to the officer configured by `ABSENCE_ADMIN_USER_ID`.

### Fun slash commands

#### `/eightball question:<question>`

Returns a random Magic 8-Ball answer.

```text
/eightball question:Will I finish this project tonight?
```

#### `/fact`

Returns a random fact from Qwerty's built-in list.

#### `/vibecheck`

Randomly reports whether the invoking member passed the vibe check.

#### `/coinflip`

Randomly returns heads or tails.

### Hangman slash commands

#### `/hangman`

Starts one Hangman game in the current channel. A second game cannot start in
that channel until the first ends or the bot restarts.

#### `/guess letter:<letter>`

Guesses one alphabetic character in the active Hangman game.

```text
/guess letter:e
```

### Owner utility

#### `/export_realnames`

Application-owner only. Exports non-bot members of the current main server to
`name_map.json`, mapping Discord user IDs to current display names. This file is
used by the established attendance workflow.

## 4. Main server prefix-command tutorial

Prefix commands begin with `!` and work only in the configured main server.

### Reaction roles

#### `!setuproles` — Administrator only

Creates any missing interest/major roles, posts the reaction-role message, adds
its reactions, and saves the message ID in `reaction_roles_msg.txt`. Run this in
the channel where the permanent role selector should live.

Running it again creates a new selector and makes the newest message the active
one. Delete or archive the older selector to avoid confusion.

#### `!setupmajorroles` — Administrator only

Creates any missing academic-major roles and includes them in the reaction-role
mapping used by `!setuproles`.

### Rainbow roles

#### `!createrainbowroles` — Administrator only

Creates the Red, Orange, Yellow, Green, Blue, and Purple roles. Qwerty's role
must sit above these roles in Discord's role hierarchy.

#### `!startrainbow`

Starts rotating the invoking member through the rainbow color roles every two
seconds. The member must hold the `LGBTQ+` role.

#### `!stoprainbow`

Stops the invoking member's rainbow cycle. Removing their `LGBTQ+` role also
stops the cycle and cleans up color roles.

### TypeFight

#### `!typefight [difficulty]`

Starts a typing race after a three-second countdown. The first exact message
wins. Difficulty defaults to `medium` and may be `easy`, `medium`, `hard`, or
`demon`.

```text
!typefight hard
```

#### `!typefightleaderboard [difficulty]`

Shows top competitors for one difficulty, including wins, average time, and
best streak.

```text
!typefightleaderboard easy
```

#### `!typestats [@member]`

Shows TypeFight statistics for the mentioned member or, when omitted, the
invoking member.

```text
!typestats @Alex
```

#### `!resettypefight` — Administrator only

Resets every TypeFight score and streak while preserving known usernames. This
cannot be undone unless `typefight_leaderboard.json` was backed up.

### Hangman prefix commands

#### `!solve <word>`

Attempts to solve the active Hangman word. A wrong solution consumes one wrong
guess.

```text
!solve programming
```

#### `!hangmanscoreboard [@member]`

Shows one member's wins and losses when mentioned; otherwise shows the leading
players.

### Word Scramble

#### `!scramble`

Starts one word-scramble game in the current channel.

#### `!unscramble <word>`

Attempts to solve the active scramble. Incorrect attempts count as losses.

```text
!unscramble collaboration
```

#### `!scramblescore [@member]`

Shows the mentioned member's Word Scramble wins, losses, and win rate. With no
mention, it uses the invoking member when they have a score; otherwise the
current implementation displays the leaderboard.

## 5. Recommended operating workflows

### Before a recruitment event

1. Refresh the static channel posts with `/publish-recruitment-info` if their content changed.
2. Add or verify the event with `/calendar-add` and `/calendar`.
3. Create the attendance code with `/attendance-code-add`.
4. Confirm it privately using `/attendance-code-list`.
5. Tell event staff the codeword; do not post it publicly.

### After a recruitment event

1. Close the code with `/attendance-code-remove`.
2. Download `/attendance-export` if leadership needs a snapshot.
3. Back up `data/attendance_records.json` according to chapter policy.

### Transitioning accepted PNMs

1. Verify the main invite in `server_config.json` is valid.
2. Give approved members the configured `Accepted PNM` source role.
3. Confirm Qwerty's main-server role is above `New Member`.
4. Test `/transition-invite` with one approved account.
5. Run `/transition-invite-all confirm:True`.
6. Review `/transition-status` until all expected members have joined.
7. Follow up manually with members whose DMs were blocked.

## 6. Configuration ownership

| Setting or file | Purpose | Handoff action |
|---|---|---|
| `.env` / `DISCORD_TOKEN` | Authenticates Qwerty | Never post or commit; rotate only if exposed |
| `server_config.json` | Guild IDs, private channel, invite, and role names | Verify every semester; never commit the active invite |
| `PNM_JOIN_LOG_CHANNEL_ID` | Private destination for completed PNM forms | Restrict channel access to authorized recruitment staff |
| `PNM_ONBOARDING_ROLE` | Invite-based role that triggers the PNM form | Keep synchronized with the role assigned by the PNM invite |
| `RECRUITMENT_*_CHANNEL_ID` | Introductions, rush schedule, and FAQ destinations | Replace if any recruitment information channel changes |
| `BIRTHDAY_CHANNEL_ID` | Main birthday announcement destination | Replace if the channel changes |
| `SHEET_ID` | Main attendance Google Sheet | Point to the active semester sheet |
| `MAIN_ATTENDANCE_CREDENTIALS` | Google service-account file | Transfer securely; never commit |
| `ABSENCE_ADMIN_USER_ID` | Officer receiving absence DMs | Change during every leadership transition |
| `cogs/helper.py` | Leadership names and resource links | Review every term |
| `cogs/roles.py` | Reaction emojis and role names | Keep synchronized with Discord roles |
| `data/` | Recruitment calendar, attendance, PNM form status, information-post IDs, and transitions | Back up securely |
| `birthdays.json` and score files | Main-server persistent data | Back up before moving hosts |

Environment variables override matching values in `server_config.json`, which
is helpful on hosting platforms.

## 7. Successor handoff checklist

Before transferring ownership or hosting responsibility:

1. Add the successor to the Discord application team with the appropriate role.
2. Never send the bot token in Discord, email, or a committed file.
3. Review `.env.example`, `server_config.example.json`, and this handbook.
4. Update officer IDs, staff roles, invite links, leadership names, and channels.
5. Securely transfer the Google service-account credential if still used.
6. Back up persistent JSON data and the active attendance Sheet.
7. Install dependencies with `python -m pip install -r requirements.txt`.
8. Start Qwerty once; never run two copies with the same token simultaneously.
9. Confirm startup reports both configured servers.
10. Test one harmless command in each server and one DM attendance code.
11. Test anonymous questions using a non-staff account.
12. Test one transition invitation before any batch operation.

## 8. Troubleshooting

### A command does not appear

- Confirm the user is looking in the correct server.
- Restart Qwerty so guild commands synchronize.
- Confirm `MAIN_GUILD_ID` and `RECRUITMENT_GUILD_ID` are correct.
- Confirm Qwerty was installed with the `applications.commands` scope.

### Qwerty does not recognize a DM attendance code

- Enable **Message Content Intent** in the Discord Developer Portal.
- Confirm the sender still belongs to the applicable server.
- Confirm the event code is active and spelled correctly.
- Ensure main and recruitment events do not use the same codeword for members
  who belong to both servers.

### A transition invitation is not delivered

- The member may have server DMs disabled.
- Verify `MAIN_SERVER_INVITE_URL` is valid.
- For a batch, verify the member holds `TRANSITION_SOURCE_ROLE`.
- Check `/transition-status` for the recorded outcome.

### The new-member role is not assigned

- Confirm the role name exactly matches `MAIN_NEW_MEMBER_ROLE`.
- Give Qwerty **Manage Roles**.
- Move Qwerty's role above the destination role in Discord's role hierarchy.

### Main attendance cannot reach Google Sheets

- Verify `SHEET_ID` and `MAIN_ATTENDANCE_CREDENTIALS`.
- Share the target Sheet with the service-account email.
- Confirm the credential file exists on the host and is not committed to Git.

### Birthday announcements do not appear

- Verify `BIRTHDAY_CHANNEL_ID`.
- Confirm Qwerty can view and send messages in that channel.
- Remember the scheduled check runs at noon Eastern.
