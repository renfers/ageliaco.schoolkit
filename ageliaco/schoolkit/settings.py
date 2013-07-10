 # -*- coding: UTF-8 -*-
from zope.interface import Interface
from zope import schema
from five import grok
from Products.CMFCore.interfaces import ISiteRoot

from plone.z3cform import layout
from plone.directives import form
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
#from plone.registry import schema

class ISettings(form.Schema):
    """ Define settings data structure """
    server_uri = schema.TextLine(title=u"Server URI",
                description=u"Serveur LDAP (avec ldaps si 'over SSL' et numéro de port)")

    ldap_manager = schema.TextLine(title=u"Manager DN",
                description=u"LDAP CN for manager",
                default=u"cn=TCNEELCMSAFG,ou=CMS,ou=TCN,dc=EEL")
    manager_password = schema.Password(title=u"mot de passe Manager DN")
    ldap_ou_groups = schema.TextLine(title=u"OU pour groupes",
                description=u"OU pour la base des groupes du site",
                default=u"ou=UO0872,ou=PO,ou=EEL,o=GRP,dc=EELL")
    ldap_ou_courses =  schema.TextLine(title=u"OU pour les cours",
                description=u"OU relatif (à partir du OU de groupes) pour les cours",
                default=u"ou=PO,ou=EEL,o=GRP,dc=EEL")
    ldap_ou_classes =  schema.TextLine(title=u"OU pour les classes",
                description=u"OU relatif (à partir du OU de groupes) pour les classes",
                default=u"ou=PO,ou=EEL,o=GRP,dc=EEL")
    ldap_ou_disciplines =  schema.TextLine(title=u"OU pour les disciplines",
                description=u"OU relatif (à partir du OU de groupes) pour les disciplines",
                default=u"ou=PO,ou=EEL,o=GRP,dc=EEL")
    #     deltaTime = schema.Int(title=u"refresh delta time",
    #                 description=u"expressed in days, 0 for no cache, -1 for no ldap search",
    #                 default=1)
    #     disciplines =  schema.Tuple(title=u"Disciplines",
    #                 description=u"Disciplines (si deltaTime est à -1 à mettre à la main sinon, complétée par le ldap)",
    #                 value_type=schema.TextLine(title=u"Value")),
    #     classes =  schema.List(title=u"Classes",
    #                 description=u"Classes (si deltaTime est à -1 à mettre à la main sinon, complétée par le ldap)",
    #                 value_type=schema.TextLine(title=u"Value")),
    #     cours =  schema.List(title=u"Cours",
    #                 description=u"Cours (si deltaTime est à -1 à mettre à la main sinon, complétée par le ldap)",
    #                 value_type=schema.TextLine(title=u"Value"))
    #adminLanguage = schema.TextLine(title=u"Admin language",
    #        description=u"Type two letter language code (admins always use this language)")
    

class SchoolkitSettingsEditForm(RegistryEditForm):
    """
    Define form logic
    """
    schema = ISettings
    label = u"Schoolkit settings"

class SchoolkitSettingsView(grok.View):
    """
    View which wrap the settings form using ControlPanelFormWrapper to a HTML boilerplate frame.
    """
    grok.name("schoolkit-settings")
    grok.context(ISiteRoot)
    def render(self):
        view_factor = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
        view = view_factor(self.context, self.request)
        return view()
        
class SchoolkitSettingsControlPanel(ControlPanelFormWrapper):
    form = SchoolkitSettingsEditForm
        