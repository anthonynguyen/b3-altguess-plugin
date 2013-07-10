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
		<player> <threshold> all - Guesses alternate ID's for a given player. Threshold = uncertain guess precision (lower = more precise). Returns maximum 10 of each type of result is all is not specified
		"""
		if data:
			input = self._admin.parseUserCmd(data)
		if not data:
			self.client.message("Enter a player to search for alternate ID's")
			return

		t = self._admin.findClientPrompt(input[0], client)

		if not t:
			return

		threshold = 2
		getAll = False

		if input[1]:
			iParts = input[1].split()
			try:
				threshold = int(iParts[0])
			except ValueError:
				client.message("Invalid threshold specified. Defaulting to 2.")
			except IndexError:
				pass

			try:
				if iParts[1] == "all":
					getAll = True
			except IndexError:
				pass

		aliases = sorted(t.getAliases(), key = lambda x: x.numUsed, reverse=True)[:threshold]

		validAliases = []

		for a in aliases:
			if a.alias not in self.blacklist:
				validAliases.append(a.alias)

		if t.name not in self.blacklist:
			validAliases.append(t.name)

		if validAliases:
			validAliases = [va.replace("'", "\.") for va in validAliases]

		ipAliases = []
		ipAliases.append(t.ip)

		for ip in t.getIpAddresses():
			ipAliases.append(ip.ip)

		ccandidates = []
		ucandidates = []

		fullIpA = "', '".join([str(x) for x in ipAliases])
		q = "SELECT * FROM ipaliases WHERE ip in ('{0}')".format(fullIpA)
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				ccandidates.append(r["client_id"])
				c.moveNext()
		c.close()

		q = "SELECT * FROM clients WHERE ip in ('{0}')".format(fullIpA)
		c = self.console.storage.query(q)
		if c.rowcount > 0:
			while not c.EOF:
				r  = c.getRow()
				ccandidates.append(r["id"])
				c.moveNext()
		c.close()

		if validAliases:
			fullA = "', '".join(validAliases)
			q = "SELECT * FROM aliases WHERE alias in ('{0}')".format(fullA)
			c = self.console.storage.query(q)
			if c.rowcount > 0:
				while not c.EOF:
					r  = c.getRow()
					ucandidates.append(r["client_id"])
					c.moveNext()
			c.close()

			q = "SELECT * FROM clients WHERE name in ('{0}')".format(fullA)
			c = self.console.storage.query(q)
			if c.rowcount > 0:
				while not c.EOF:
					r  = c.getRow()
					ucandidates.append(r["id"])
					c.moveNext()
			c.close()
			ucandidates = [str(c) for c in sorted(list(set(ucandidates))) if c != t.id]

		ccandidates = [str(c) for c in sorted(list(set(ccandidates))) if c != t.id]

		uucandidates = []
		for uc in ucandidates:
			if uc not in ccandidates:
				uucandidates.append(uc)

		cmore = False
		umore = False
		if not getAll:
			cmore = len(ccandidates) - 10
			if cmore < 1:
				cmore = False
			umore = len(uucandidates) - 10
			if umore < 1:
				umore = False
			ccandidates = ccandidates[:10]
			uucandidates = uucandidates[:10]

		coutput = []
		uoutput = []

		nC = False
		nU = False

		if ccandidates:
			q = "SELECT * FROM clients WHERE id in ('{0}')".format("', '".join(ccandidates))
			c = self.console.storage.query(q)
			if c.rowcount > 0:
				while not c.EOF:
					r  = c.getRow()
					coutput.append("^2{0}^7(^1@{1}^7)".format(r["name"], r["id"]))
					c.moveNext()
			c.close()
		else:
			nD = True

		if uucandidates:
			q = "SELECT * FROM clients WHERE id in ('{0}')".format("', '".join(uucandidates))
			c = self.console.storage.query(q)
			if c.rowcount > 0:
				while not c.EOF:
					r  = c.getRow()
					uoutput.append("^2{0}^7(^1@{1}^7)".format(r["name"], r["id"]))
					c.moveNext()
			c.close()
		else:
			nU = True
		
		if not nC:
			client.message("Certain alternates for ^2{0}^7(^1@{1}^7): {2}{3}".format(t.name, str(t.id), ", ".join(coutput), " + ^2{0}^7 more".format(cmore) if cmore else ""))
		else:
			client.message("No certain alternates found for ^2{0}^7(^1@{1}^7).".format(t.name, t.id))
		
		if not nU:
			client.message("Uncertain alternates for ^2{0}^7(^1@{1}^7): {2}{3}".format(t.name, str(t.id), ", ".join(uoutput), " + ^2{0}^7 more".format(umore) if umore else ""))
		else:
			if not validAliases:
				client.message("No uncertain alternates found for ^2{0}^7(^1@{1}^7) because their name(s) is(are) too generic.".format(t.name, t.id))
			else:
				client.message("No uncertain alternates found for ^2{0}^7(^1@{1}^7).".format(t.name, t.id))