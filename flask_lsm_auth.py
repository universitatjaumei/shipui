import flask
import xmlrpclib
import urllib
import base64
import logging
from urlparse import urlparse, parse_qs, urlunparse


class LSM:

    def __init__(self):

        self.logger = logging.getLogger("werkzeug")

        self.domain = "haddock.si.uji.es"

        # Urls
        # SSO path (xmlrpc and web).
        self.sso_path = "/lsmSSO-83"

        ## SSO authentication URI.
        self.lsm_manage_uri = self.sso_path + "/lsmanage.php"

        # SSO logout URI.
        self.logout_uri = self.sso_path + "/logout_sso.php"

        # server XML-RPC end point
        self.xml_endpoint = self.sso_path + "/server.php"

        # server xmlrpc port
        self.xml_port = 80

        # server xmlrpc method
        self.xml_method = "http"

        # SSO server
        self.sso_server = "xmlrpc.uji.es"

        # SSO URL
        self.sso_url = "https://" + self.sso_server + self.lsm_manage_uri

        # SSO logout URL
        self.logout_url = "https://" + self.sso_server + self.logout_uri

        # Cookie names
        self.session_cookie_name = "LSMSession" + self._get_app_domain(True)
        self.passkey_cookie_name = "LSMSessionPK" + self._get_app_domain(True);
        self.idx_cookie_name = "LSMSessionIDX" + self._get_app_domain(True);

        # Server URL
        self.server_url = "%s://%s:%s%s" % (self.xml_method, self.sso_server, self.xml_port, self.xml_endpoint)

        self.lang_cookie_name = "uji-lang"

        # Response data
        self._response_data = {
            "cookies": {},
            "redirect": None
        }

        # Other parameters
        self.debug = 1


    def _get_app_domain(self, n_fqdn=False):
        """
        Returns the application domain. It is used for building the local session cookie name.

        If n_fqdn is true, then the "uji.es" domain part is removed from the return value.
        """

        if n_fqdn:
            return self.domain.replace(".uji.es", "").replace(".", "_")
        else:
            return self.domain

    def _dTok(self, k, c):
        if len(k) == 0:
            return ''

        msg = base64.b64decode(c)

        if len(k) != len(msg):
            return ''

        ml = len(msg)
        kl = len(k)
        newmsg = ""

        for i in range(ml):
            newmsg += chr(ord(msg[i]) ^ ord(k[i % kl]))

        return newmsg



    def _get_url(self, url=""):
        if url == "":
            url = flask.request.url

        url_object = urlparse(url)
        query_params = parse_qs(url_object.query, keep_blank_values=True)


        if "UJITok" in query_params:
            for tok in query_params.get("UJITok"):
                query_params.pop("UJITok")

            url_object = url_object._replace(query=urllib.urlencode(query_params, True))

        return urlunparse(url_object)

    def _set_redirect_url(self, redirect_url):
        self._response_data["redirect"] = redirect_url

    def _get_redirect_url(self):
        return self._response_data.get("redirect")

    def _set_cookie(self, cookie_name, cookie_value, expiration):
        self._response_data.get("cookies")[cookie_name] = { "name": cookie_name, "value": cookie_value, "expires": expiration }

    def _get_response_cookie(self, cookie_name):
        cookie = self._response_data.get("cookies").get(cookie_name)

        if cookie:
            return cookie.get("value")
        else:
            return ""

    def _get_login_redirect(self, url=""):
        """
        Returns the SSO authentication redirect.

        """
        url = self._get_url(url)
        idx = self._get_response_cookie(self.idx_cookie_name)

        if not idx:
            flask.abort(500)

        redirect_url = self.sso_url + "?Url=" + urllib.quote_plus(url) + "&lang=" + self._lsm_get_lang() + "&ident=" + self.domain + "&dimitri=" + idx
        self._set_redirect_url(redirect_url)

        return self._response_data

    def _lsm_get_logout_redirect(self, url=""):
        url = self._get_url(url)
        redirect_url = self.logout_url + "?Url=" + urllib.quote_plus(url) + "&lang=" + self._lsm_get_lang() + "&ident=" + self.domain
        self._set_redirect_url(redirect_url)

        for cookie_name in (self.session_cookie_name, self.passkey_cookie_name, self.idx_cookie_name):
            self._set_cookie(cookie_name, "", 0)

        return self._response_data

    def _lsm_get_lang(self):
        if self.lang_cookie_name in flask.request.cookies:
            return flask.request.cookies.get(self.lang_cookie_name)
        else:
            return "ca"

    def _lsm_get_lsmsession(self):
        LSMSession = flask.request.cookies.get(self.session_cookie_name)


        if LSMSession:
            return LSMSession

        pk, idx = self._get_pk_idx()

        if not 'UJITok' in flask.request.args and not flask.request.args.get("UJITok"):
            #self._lsm_get_logout_redirect()
            return ""

        if pk:
            UJITok = urllib.unquote(flask.request.args.get("UJITok"))
            LSMSession = self._dTok(pk, UJITok)

        return LSMSession

    def _set_pk_idx(self, pk, idx):
        self._set_cookie(self.idx_cookie_name, idx, None)
        self._set_cookie(self.passkey_cookie_name, pk, None)

    def _get_pk_idx(self):
        domain = self._get_app_domain()
        pk = flask.request.cookies[self.passkey_cookie_name] if self.passkey_cookie_name in flask.request.cookies else ""
        idx = flask.request.cookies[self.idx_cookie_name] if self.idx_cookie_name in flask.request.cookies else ""

        if not pk and not idx and self._get_response_cookie(self.passkey_cookie_name):
            pk = self._get_response_cookie(self.passkey_cookie_name)
            idx = self._response_data.get("cookies").get(self.idx_cookie_name)

        if idx and pk:
            return [ pk, idx ]

        server = xmlrpclib.Server(self.server_url);

        if self.debug:
            self.logger.info("Calling remote get_pk_idx...")

        # Call the server and get our result.
        xmlrpc_response = server.lsm.get_pk_idx()

        if xmlrpc_response:
            idx = xmlrpc_response[0]
            pk = xmlrpc_response[1]

            self._set_pk_idx(pk, idx)

            return [ pk, idx ]

        return [ "", "" ]

    def logout(self, url=""):
        return self._lsm_get_logout_redirect(url)

    def login(self, url=""):
        LSMSession = self._lsm_get_lsmsession()

        if not LSMSession:
            return self._get_login_redirect()

        connect = xmlrpclib.Server(self.server_url);

        # Call the server and get our result.
        xmlrpc_response = connect.lsm.check_session(LSMSession, self._get_app_domain(True))

        autenticado = xmlrpc_response[0]
        gLSMSession = xmlrpc_response[1]

        if autenticado:
            self._set_cookie(self.session_cookie_name, gLSMSession, None)
            #self._set_redirect_url(self._get_url());

            return self._response_data

        pk, idx = self._get_pk_idx()

        return self._get_login_redirect()

    def get_login(self):

        LSMSession = self._lsm_get_lsmsession()

        if not LSMSession:
            return ""

        # Call the server and get our result.
        connect = xmlrpclib.Server(self.server_url);
        xmlrpc_response = connect.lsm.get_login_session(LSMSession, self._get_app_domain(True))

        user = xmlrpc_response[0]

        if user and flask.request.args.get("UJITok"):
            self._set_cookie(self.session_cookie_name, LSMSession, None);
            self._set_redirect_url(self._get_url())

        return user

    def compose_response(self, res=None):
        if not res:
            res = flask.make_response()

        if self._response_data.get("redirect"):
            res = flask.make_response(flask.redirect(self._response_data.get("redirect")))

        for name, cookie in self._response_data.get("cookies").items():
            res.set_cookie(name, cookie.get("value"), expires=cookie.get("expires"), path="/", domain=self.domain, secure=False, httponly=True)

        return res
