#!/usr/bin/env python

import time
import random
import re
import hashlib
import datetime
import wsgiref.handlers
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
		p = re.compile('/[^A-Za-z0-9-]/')					# Regular expression used to clean up the parameters
		for parameter in self.useParameters:				# Loop through the parameters
			k+=p.sub('',self.request.get(parameter))		# Strip out messy characters in the parameters
			requestParameters += parameter + '=' + self.request.get(parameter) + '&'	# Build up the query string
		requestParameters = requestParameters[:len(requestParameters)-1]				# Strip off the extra &
		h = hashlib.md5(k).hexdigest()						# Create an MD5 hash
		epoch = datetime.datetime.now()						# Get the time
		q = APICallResult.all()								# Build a GQL query
		q.filter('h =',h)									# ...
		q.filter('apiCall =',self.request.path)				# ...
		q.order('-epoch')									# ...
		results = q.fetch(1000)									# Execute the GQL query
		for result in results:								# Loop through the results
			if result.epoch + self.cacheTime > epoch:		# If the cache time has not expired...
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

# These are the classes that define each API call's required parameters and cache times.

class CharAccountBalance(Proxy):
	useParameters = ['userID', 'apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)
		
class CorpAccountBalance(Proxy):
	useParameters = ['userID', 'apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class EveAllianceList(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CharAssetList(Proxy):
	useParameters = ['userID','apiKey','characterID','version']
	cacheTime = datetime.timedelta(hours=23)
	def get(self):
		Proxy.get(self)

class CorpAssetList(Proxy):
	useParameters = ['userID','apiKey','characterID','version']
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class AccountCharacters(Proxy):
	useParameters = ['userID','apiKey']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CharCharacterSheet(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)
				
class EveConquerableStationList(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)
			
class CorpCorporationSheet(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class EveErrorList(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)
				
class CharIndustryJobs(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CorpIndustryJobs(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class CharWalletJournal(Proxy):
	useParameters = ['userID','apiKey','characterID','accountKey','beforeRefID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CorpWalletJournal(Proxy):
	useParameters = ['userID','apiKey','characterID','accountKey','beforeRefID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CharKillLog(Proxy):
	useParameters = ['userID','apiKey','characterID','beforeKillID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CorpKillLog(Proxy):
	useParameters = ['userID','apiKey','characterID','beforeKillID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CharWalletTransactions(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CorpWalletTransactions(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CharMarketOrders(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CorpMarketOrders(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class MapJumps(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class MapKills(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class MapSovereignty(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CorpMemberTracking(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class EveCharacterID(Proxy):
	useParameters = ['names']
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class EveCharacterName(Proxy):
	useParameters = ['ids']
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class EveRefTypes(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class CharSkillInTraining(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=15)
	def get(self):
		Proxy.get(self)

class EveSkillTree(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(hours=24)
	def get(self):
		Proxy.get(self)

class CorpStarbaseList(Proxy):
	useParameters = ['userID','apiKey','characterID','version']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CorpStarbaseDetail(Proxy):
	useParameters = ['userID','apiKey','characterID','itemID','version']
	cacheTime = datetime.timedelta(hours=6)
	def get(self):
		Proxy.get(self)

class CharFacWarStats(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class CorpFacWarStats(Proxy):
	useParameters = ['userID','apiKey','characterID']
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class EveFacWarTopStats(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

class MapFacWarSystems(Proxy):
	useParameters = []
	cacheTime = datetime.timedelta(minutes=60)
	def get(self):
		Proxy.get(self)

# Google App Engine Infrastructure

def main():
  application = webapp.WSGIApplication([('/char/AccountBalance.xml.aspx',CharAccountBalance),
										('/corp/AccountBalance.xml.aspx',CorpAccountBalance),										
										('/eve/AllianceList.xml.aspx',EveAllianceList),						
										('/char/AssetList.xml.aspx',CharAssetList),									
										('/corp/AssetList.xml.aspx',CorpAssetList),
										('/account/Characters.xml.aspx',AccountCharacters),										
										('/char/CharacterSheet.xml.aspx',CharCharacterSheet),
										('/eve/ConquerableStationList.xml.aspx',EveConquerableStationList),
										('/corp/CorporationSheet.xml.aspx',CorpCorporationSheet),										
										('/eve/ErrorList.xml.aspx',EveErrorList),																				
										('/char/IndustryJobs.xml.aspx',CharIndustryJobs),																	
										('/corp/IndustryJobs.xml.aspx',CorpIndustryJobs),																											
										('/char/WalletJournal.xml.aspx',CharWalletJournal),																																					
										('/corp/WalletJournal.xml.aspx',CorpWalletJournal),																																					
										('/char/KillLog.xml.aspx',CharKillLog),
										('/corp/KillLog.xml.aspx',CorpKillLog),
										('/char/WalletTransactions.xml.aspx',CharWalletTransactions),
										('/corp/WalletTransactions.xml.aspx',CorpWalletTransactions),
										('/char/MarketOrders.xml.aspx',CharMarketOrders),
										('/corp/MarketOrders.xml.aspx',CorpMarketOrders),
										('/map/Jumps.xml.aspx',MapJumps),								
										('/map/Kills.xml.aspx',MapKills),
										('/map/Sovereignty.xml.aspx',MapSovereignty),
										('/corp/MemberTracking.xml.aspx',CorpMemberTracking),
										('/eve/CharacterID.xml.aspx',EveCharacterID),																																								
										('/eve/CharacterName.xml.aspx',EveCharacterName),
										('/eve/RefTypes.xml.aspx',EveRefTypes),
										('/char/SkillInTraining.xml.aspx',CharSkillInTraining),										
										('/eve/SkillTree.xml.aspx',EveSkillTree),
										('/corp/StarbaseList.xml.aspx',CorpStarbaseList),	
										('/corp/StarbaseDetail.xml.aspx',CorpStarbaseDetail),
										('/char/FacWarStats.xml.aspx',CharFacWarStats),																				
										('/corp/FacWarStats.xml.aspx',CorpFacWarStats),																														
										('/eve/FacWarTopStats.xml.aspx',EveFacWarTopStats),
										('/map/FacWarSystems.xml.aspx',MapFacWarSystems)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
  main()
