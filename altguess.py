# Alt Guess Plugin for B3
# By clearskies (Anthony Nguyen)
# GPL licensed

import b3
import b3.plugin

__version__ = "1"
__author__ = "clearskies (Anthony Nguyen)"

class AltguessPlugin(b3.plugin.Plugin):
	requiresConfigFile = False

	def onStartup(self):
		self._admin = self.console.getPlugin("admin")
		self._admin.registerCommand(self, "altguess", 60, self.cmd_altguess, "ag")

		self.blacklist = [".", "UnnamedPlayer", "EmptyNameDefault", "New_UrT_Player", "noob", "lol"]

	def cmd_altguess(self, data, client, cmd = None):
		"""\
		<player> all - Guesses alternate ID's for a given player. Returns 20 results if all is not specified
		"""
		if data:
			input = self._admin.parseUserCmd(data)
		if not data:
			self.client.message("Enter a player to search for alternate ID's")
			return

		t = self._admin.findClientPrompt(input[0], client)

		if not t:
			return

		getAll = False
		if input[1] == "all": getAll = True

		aliases = t.getAliases()
		validAliases = []

		for a in aliases:
			if a.alias not in self.blacklist:
				validAliases.append(a.alias)

		if t.name not in self.blacklist:
			validAliases.append(t.name)

		if not validAliases:
			client.message("That person's name(s) is(are) too generic, sorry.")
			return

		validAliases = [va.replace("'", "\.") for va in validAliases]

		ipAliases = []
		ipAliases.append(t.ip)

		for ip in t.getIpAddresses():
			ipAliases.append(ip.ip)

		candidates = []

		fullIpA = "', '".join([str(x) for x in ipAliases])
		q = "SELECT * FROM ipaliases WHERE ip in ('{0}')".format(fullIpA)
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				candidates.append(r["client_id"])
				c.moveNext()
		c.close()

		q = "SELECT * FROM clients WHERE ip in ('{0}')".format(fullIpA)
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				candidates.append(r["id"])
				c.moveNext()
		c.close()

		fullA = "', '".join(validAliases)
		q = "SELECT * FROM aliases WHERE alias in ('{0}')".format(fullA)
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				candidates.append(r["client_id"])
				c.moveNext()
		c.close()

		q = "SELECT * FROM clients WHERE name in ('{0}')".format(fullA)
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				candidates.append(r["id"])
				c.moveNext()
		c.close()

		candidates = [str(c) for c in sorted(list(set(candidates))) if c != t.id]

		if not candidates:
			client.message("No possible alternates found for ^2{0}^7(^1{1}^7).".format(t.name, t.id))
			return

		if not getAll:
			candidates = candidates[:20]

		output = []

		q = "SELECT * FROM clients WHERE id in ('{0}')".format("', '".join(candidates))
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				output.append("^2{0}^7(^1@{1}^7)".format(r["name"], r["id"]))
				c.moveNext()
		c.close()

		client.message("Possible aliases for ^2{0}^7(^1@{1}^7): {2}".format(t.name, str(t.id), ", ".join(output)))