import unittest
from unittest.mock import Mock, patch

import discord
from discord.ext import commands

from main import CreateTicket, Dropdown, _closeticket, client, suggest


class TestDropdown(unittest.TestCase):
    async def test_callback_ticket(self):
        interaction = Mock(spec=discord.Interaction)
        dropdown = Dropdown()

        # Simulates 'ticket' selection in dropdown
        await dropdown.callback(interaction)
        interaction.response.send_message.assert_called_once_with("Click below to create a ticket", ephemeral=True, view=CreateTicket())

    async def test_callback_suggest(self):
        interaction = Mock(spec=discord.Interaction)
        dropdown = Dropdown()
        dropdown.values = ["suggest"]

        # Simulates the selection of 'suggest' in the dropdown
        await dropdown.callback(interaction)
        interaction.response.send_message.assert_called_once_with("To send a suggestion, use the command `/suggestion` ", ephemeral=True)

    async def test_callback_bug(self):
        interaction = Mock(spec=discord.Interaction)
        dropdown = Dropdown()
        dropdown.values = ["bug"]

        # Simulates 'bug' selection in dropdown
        await dropdown.callback(interaction)
        interaction.response.send_message.assert_called_once_with("To report a bug for one of our projects, follow these instructions:\n\nSend as much detail about it as possible (including description and photos).\n\nHaving this in hand, create a ticket below and send it.", ephemeral=True, view=CreateTicket())

    async def test_callback_sponsor(self):
        interaction = Mock(spec=discord.Interaction)
        dropdown = Dropdown()
        dropdown.values = ["sponsor"]

        # Simulates 'sponsor' selection in the dropdown
        await dropdown.callback(interaction)
        interaction.response.send_message.assert_called_once_with("If you want to sponsor the eco community, you can make it with 2 ways.\n\n1 - Boosting the our server\n\n2 - Be a patrono [here](https://www.patreon.com/EcoBot791/membership) and unlock a most of content about us and receive more status", ephemeral=True)

class TestCreateTicket(unittest.TestCase):
    async def test_create_ticket(self):
        interaction = Mock(spec=discord.Interaction)
        interaction.channel = Mock(spec=discord.TextChannel)

        view = CreateTicket()
        view.value = True  # Simulate the configured value when clicking the button

        with patch("discord.Client.get_channel") as mock_get_channel:
            mock_channel = mock_get_channel.return_value
            mock_channel.create_thread.return_value = discord.Thread()

            with patch("discord.Webhook.send") as mock_send:
                await view.confirm(interaction, None)

class TestClient(unittest.TestCase):
    @patch("discord.Client.wait_until_ready")
    @patch("discord.Client.sync")
    async def test_on_ready(self, mock_sync, mock_wait_until_ready):
        client_instance = client()
        client_instance.synced = False

        await client_instance.on_ready()

        mock_wait_until_ready.assert_called_once()
        mock_sync.assert_called_once_with(guild=discord.Object(id=941388532734361640))

class TestSlashCommands(unittest.TestCase):
    @patch("discord.Client.get_channel")
    async def test_suggest(self, mock_get_channel):
        interaction = Mock(spec=discord.Interaction)
        interaction.user = Mock(spec=discord.Member)
        interaction.user.avatar.url = "mocked_url"

        mock_channel = Mock(spec=discord.TextChannel)
        mock_get_channel.return_value = mock_channel

        await suggest(interaction, "Test suggestion")

        mock_channel.send.assert_called_once()
        interaction.response.send_message.assert_called_once()

    @patch("discord.Client.get_role")
    @patch("discord.TextChannel.edit")
    async def test_closeticket(self, mock_edit, mock_get_role):
        interaction = Mock(spec=discord.Interaction)
        interaction.channel = Mock(spec=discord.TextChannel)
        interaction.user = Mock(spec=discord.Member)
        interaction.user.id = 208791519136710657
        interaction.user.mention = "<@208791519136710657>"
        interaction.author.roles = [Mock(spec=discord.Role)]

        mock_role = Mock(spec=discord.Role)
        mock_get_role.return_value = mock_role

        await _closeticket(interaction)

        mock_edit.assert_called_once_with(archived=True)
        interaction.response.send_message.assert_called_once_with(f"The ticket was archived by {interaction.user.mention}, thank you for contacting us!")

if __name__ == "__main__":
    unittest.main()