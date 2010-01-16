#!/usr/bin/env python

# Based on Erik Evenson's excellent eveapiproxy application, updated for Dominion.
# Based on http://wiki.eve-id.net/APIv2_Page_Index (as of 151936JAN10).
# Contributors: Erik Evenson, dafire, zakuluka

import time
import random
import re
import hashlib
import datetime
import wsgiref.handlers
import urllib
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import urlfetch

class APICallResult(db.Model):
	"Define a API call result database record"
	apiCall = db.StringProperty(required=True)				# The API call -- for example, /eve/SkillTree.xml.aspx
	h = db.StringProperty(required=True)					# A unique hash of the parameters used in the API call
	epoch = db.DateTimeProperty(required=True)				# The date and time the API call was made
	value = db.TextProperty()								# The API call response

class Proxy(webapp.RequestHandler):
	APIROOT = 'http://api.eve-online.com'					# CCP's API call address
	
	def get(self):
		parameters = self.request.arguments()				# The parameters from the submitted by the user
		self.response.headers['Content-Type'] = 'application/xml;charset=UTF-8'	# Set the output MIME type to XML
		k=''												# Start building the hash
		requestParameters = '?'								# Start building the query string.  We will strip off any irrelevant parameters.
		p = re.compile('/[^%A-Za-z0-9-]/')					# Regular expression used to clean up the parameters
		for parameter in self.useParameters:				# Loop through the parameters
			k+=p.sub('',self.request.get(parameter))		# Strip out messy characters in the parameters
			requestParameters += urllib.urlencode({parameter:self.request.get(parameter)}) + '&'
			#requestParameters += parameter + '=' + self.request.get(parameter) + '&'	# Build up the query string
		requestParameters = requestParameters[:len(requestParameters)-1]				# Strip off the extra &
		h = hashlib.md5(k).hexdigest()						# Create an MD5 hash
		epoch = datetime.datetime.now()						# Get the time
		q = APICallResult.all()								# Build a GQL query
		q.filter('h =',h)									# ...
		q.filter('apiCall =',self.request.path)				# ...
		q.order('-epoch')									# ...
		results = q.fetch(1000)								# Execute the GQL query
		for result in results:								# Loop through the results
			if result.epoch + self.cacheTime > epoch:   # If the cache time has not expired...
				self.response.out.write(result.value)		# ...send the cached response to the user and don't bother CCP
				return										# ...and finish
			else:											# Otherwise...
				result.delete()								# Delete the cached copy and replace with a new response from CCP
		url = self.APIROOT+self.request.path + requestParameters						# Form the API call URL
		value = urlfetch.fetch(url)							# Execute the API call
		apiCallResult = APICallResult(apiCall=self.request.path,h=h,epoch=epoch)		# Create a new cache item
		p = re.compile("'")									# Regular expression to clean up some characters XML doesn't like
		apiCallResult.value = db.Text(p.sub("'",value.content))							# Set the response text
		apiCallResult.put()									# Do a GQL put
		self.response.out.write(value.content)				# Write out the results
		return												# Finished
		
# Added per dafire's comment
	def post(self):
		self.get()

# These are the classes that define each API call's required parameters and cache times.
# Arranged in the order indicated on the website above (for easy checks in the future).
# All time intervals have been verified as of same date listed above

class AccountCharacters(Proxy):
	useParameters = ['userID','apiKey']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CharAccountBalance(Proxy):
	useParameters = ['userID', 'apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CharAssetList(Proxy):
	useParameters = ['userID','apiKey','characterID','version']
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class CharCharacterSheet(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CharFacWarStats(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CharIndustryJobs(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CharKillLog(Proxy):
	useParameters = ['userID','apiKey','characterID','beforeKillID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CharMailingLists(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CharMailMessages(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=30)
	def get(self):
		Proxy.get(self)

class CharMarketOrders(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CharMedals(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class CharNotifications(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=30)
	def get(self):
		Proxy.get(self)

class CharSkillInTraining(Proxy): # 15 minutes or 1 hour
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CharSkillQueue(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CharStandings(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=3)
	def get(self):
		Proxy.get(self)

class CharWalletJournal(Proxy):
	useParameters = ['userID','apiKey','characterID','accountKey','beforeRefID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CharWalletTransactions(Proxy):
	useParameters = ['userID','apiKey','characterID','beforeTransID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpAccountBalance(Proxy):
	useParameters = ['userID', 'apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CorpAssetList(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID','version']
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class CorpContainerLog(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=3)
	def get(self):
		Proxy.get(self)

class CorpCorporationSheet(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CorpFacWarStats(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpIndustryJobs(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CorpKillLog(Proxy):
	useParameters = ['userID','apiKey','characterID','beforeKillID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpMarketOrders(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpMedals(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class CorpMemberMedals(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class CorpMemberSecurity(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpMemberSecurityLog(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpMemberTracking(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CorpStarbaseDetail(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID','itemID','version']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpStarbaseList(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID','version']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CorpShareholders(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpStandings(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=3)
	def get(self):
		Proxy.get(self)

class CorpTitles(Proxy): # Unable to verify time delta
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpWalletJournal(Proxy): # 15 minutes or 1 hour?
	useParameters = ['userID','apiKey','characterID','accountKey','beforeRefID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class CorpWalletTransactions(Proxy): # 15 minutes or 1 hour?
	useParameters = ['userID','apiKey','characterID','accountKey','beforeTransID']
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class EveAllianceList(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class EveCertificateTree(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class EveConquerableStationList(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class EveErrorList(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class EveFacWarStats(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class EveFacWarTopStats(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class EveCharacterID(Proxy): # 1 month?
	useParameters = ['names']
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class EveCharacterName(Proxy): # 1 month?
	useParameters = ['ids']
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class EveRefTypes(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class EveSkillTree(Proxy): # 10 years?
	useParameters = []
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class MapFacWarSystems(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class MapJumps(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class MapKills(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class MapSovereignty(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=1)
	def get(self):
		Proxy.get(self)

class ServerServerStatus(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=3)
	def get(self):
		Proxy.get(self)

# Google App Engine Infrastructure

def main():
	application = webapp.WSGIApplication([('/account/Characters.xml.aspx',AccountCharacters),
										('/char/AccountBalance.xml.aspx',CharAccountBalance),
										('/char/AssetList.xml.aspx',CharAssetList),
										('/char/CharacterSheet.xml.aspx',CharCharacterSheet),
										('/char/FacWarStats.xml.aspx',CharFacWarStats),
										('/char/IndustryJobs.xml.aspx',CharIndustryJobs),
										('/char/KillLog.xml.aspx',CharKillLog),
										('/char/mailinglists.xml.aspx',CharMailingLists),
										('/char/MailMessages.xml.aspx',CharMailMessages),
										('/char/MarketOrders.xml.aspx',CharMarketOrders),
										('/char/Medals.xml.aspx',CharMedals),
										('/char/Notifications.xml.aspx',CharNotifications),
										('/char/SkillInTraining.xml.aspx',CharSkillInTraining),
										('/char/SkillQueue.xml.aspx',CharSkillQueue),
										('/char/Standings.xml.aspx',CharStandings),
										('/char/WalletJournal.xml.aspx',CharWalletJournal),
										('/char/WalletTransactions.xml.aspx',CharWalletTransactions),
										('/corp/AccountBalance.xml.aspx',CorpAccountBalance),
										('/corp/AssetList.xml.aspx',CorpAssetList),
										('/corp/ContainerLog.xml.aspx',CorpContainerLog),
										('/corp/CorporationSheet.xml.aspx',CorpCorporationSheet),
										('/corp/FacWarStats.xml.aspx',CorpFacWarStats),
										('/corp/IndustryJobs.xml.aspx',CorpIndustryJobs),
										('/corp/KillLog.xml.aspx',CorpKillLog),
										('/corp/MarketOrders.xml.aspx',CorpMarketOrders),
										('/corp/Medals.xml.aspx',CorpMedals),
										('/corp/MemberMedals.xml.aspx',CorpMemberMedals),
										('/corp/MemberSecurity.xml.aspx',CorpMemberSecurity),
										('/corp/MemberSecurityLog.xml.aspx',CorpMemberSecurityLog),
										('/corp/MemberTracking.xml.aspx',CorpMemberTracking),
										('/corp/StarbaseDetail.xml.aspx',CorpStarbaseDetail),
										('/corp/StarbaseList.xml.aspx',CorpStarbaseList),
										('/corp/Shareholders.xml.aspx',CorpShareholders),
										('/corp/Standings.xml.aspx',CorpStandings),
										('/corp/Titles.xml.aspx',CorpTitles),
										('/corp/WalletJournal.xml.aspx',CorpWalletJournal),
										('/corp/WalletTransactions.xml.aspx',CorpWalletTransactions),
										('/eve/AllianceList.xml.aspx',EveAllianceList),
										('/eve/CertificateTree.xml.aspx',EveCertificateTree),
										('/eve/ConquerableStationList.xml.aspx',EveConquerableStationList),
										('/eve/ErrorList.xml.aspx',EveErrorList),
										('/eve/FacWarStats.xml.aspx',EveFacWarStats),
										('/eve/FacWarTopStats.xml.aspx',EveFacWarTopStats),
										('/eve/CharacterID.xml.aspx',EveCharacterID),
										('/eve/CharacterName.xml.aspx',EveCharacterName),
										('/eve/RefTypes.xml.aspx',EveRefTypes),
										('/eve/SkillTree.xml.aspx',EveSkillTree),
										('/map/FacWarSystems.xml.aspx',MapFacWarSystems),
										('/map/Jumps.xml.aspx',MapJumps),
										('/map/Kills.xml.aspx',MapKills),
										('/map/Sovereignty.xml.aspx',MapSovereignty),
										('/server/ServerStatus.xml.aspx',ServerServerStatus)],
                                       debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
