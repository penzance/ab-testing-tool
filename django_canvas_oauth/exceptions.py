class CanvasOauthError(Exception): pass

class NewTokenNeeded(CanvasOauthError): pass

#Unused
class BadOAuthReturnError(CanvasOauthError): pass

class BadLTIConfigError(CanvasOauthError): pass
