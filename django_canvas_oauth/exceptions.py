class CanvasOauthError(Exception): pass

class NewTokenNeeded(CanvasOauthError): pass

class BadOAuthReturnError(CanvasOauthError): pass

class BadLTIConfigError(CanvasOauthError): pass
