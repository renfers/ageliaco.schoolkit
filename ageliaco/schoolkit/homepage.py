# -*- coding: UTF-8 -*-
from five import grok
from zope import schema

from plone.directives import form, dexterity
from z3c.form import field, button

from plone.app.textfield import RichText
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.app.container.interfaces import IObjectAddedEvent

from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from zope.interface import implements
#from plone.app.contenttypes.interfaces import IDocument
#from plone.dexterity.content import Container
from Products.CMFCore.utils import getToolByName

from ageliaco.schoolkit import MessageFactory
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
#from plone.registry.interfaces import ageliaco.schoolkit.settings.ISettings
import ldap
import datetime

class ldap_cache(object):
    """ cache by zope instance """
    def __init__(self):
        self.timestamp = datetime.datetime.today()
        self.cours = []
        self.classes = []
        self.disciplines = []
        self.reset_all()

    def reset_all(self):
        self.timestamp = datetime.datetime.today()
        registry = getUtility(IRegistry)
        #import pdb; pdb.set_trace()
        server_uri = registry['ageliaco.schoolkit.settings.ISettings.server_uri']
        ldap_manager = registry['ageliaco.schoolkit.settings.ISettings.ldap_manager']
        manager_password = registry['ageliaco.schoolkit.settings.ISettings.manager_password']
        ldap_ou_groups = registry['ageliaco.schoolkit.settings.ISettings.ldap_ou_groups']
        ldap_ou_courses = registry['ageliaco.schoolkit.settings.ISettings.ldap_ou_courses']
        ldap_ou_classes = registry['ageliaco.schoolkit.settings.ISettings.ldap_ou_classes']
        ldap_ou_disciplines = registry['ageliaco.schoolkit.settings.ISettings.ldap_ou_disciplines']
        
        if not manager_password:
            manager_password = u'musbiro49'
        l = ldap.initialize(server_uri)
        l.bind_s(ldap_manager, manager_password)
        
        filter = '(objectClass=ETATGEgroupOfNames)'
        attrs = ['cn']
        #('cn=4TM.DFbid,ou=4,ou=COURS,ou=UO0872,ou=PO,ou=EEL,o=GRP,dc=EEL', {'cn': ['4TM.DFbid']})
        cours = l.search_s( ldap_ou_courses + ',' + ldap_ou_groups     , ldap.SCOPE_SUBTREE, filter, attrs )
        classes = l.search_s( ldap_ou_classes + ',' + ldap_ou_groups  , ldap.SCOPE_SUBTREE, filter, attrs )
        disciplines = l.search_s( ldap_ou_disciplines + ',' + ldap_ou_groups  , ldap.SCOPE_SUBTREE, filter, attrs )
        for cour in cours:
            self.cours.append(cour[1]['cn'][0])
        for classe in classes:
            self.classes.append(classe[1]['cn'][0])
        for discipline in disciplines:
            self.disciplines.append(discipline[1]['cn'][0])

    def classes(self):
        now =  datetime.datetime.today()
        if now - self.timestamp > datetime.timedelta(days=1):
            self.reset_all()
        return self.classes
        
    def disciplines(self):
        now =  datetime.datetime.today()
        if now - self.timestamp > datetime.timedelta(days=1):
            self.reset_all()
        return self.disciplines
        
    def cours(self):
        now =  datetime.datetime.today()
        if now - self.timestamp > datetime.timedelta(days=1):
            self.reset_all()
        return self.cours
        
    
class IHomepage(form.Schema):
    """
    Homepage interface
    """
    slider_height = schema.Int(
            title=MessageFactory(u"Hauteur du carousel"),
            description=MessageFactory(u"Hauteur en pixels du carousel"),
            default = 200,
            required=True,
        )
    content = RichText(
            title=MessageFactory(u"Content"),
            required=False,
        )    

    

@form.default_value(field=IExcludeFromNavigation['exclude_from_nav'], context=IHomepage)
def excludeFromNavDefaultValue(data):
    return True

@grok.subscribe(IHomepage, IObjectAddedEvent)
def setSlides(homepage, event):
    admid = 'slides'
    try:
        cycles = homepage[admid]
    except KeyError: 
        rea = homepage.invokeFactory("Folder", id=admid, title=u'Slides')
    return 

@grok.subscribe(IHomepage, IObjectAddedEvent)
def setAccordion(homepage, event):
    admid = 'accordion'
    try:
        cycles = homepage[admid]
    except KeyError: 
        rea = homepage.invokeFactory("Folder", id=admid, title=u'Anonymous Accordion')
    return 


class View(grok.View):
    grok.context(IHomepage)
    grok.require('zope2.View')
    grok.name('view')
    
    classes = []
    cours = []
    disciplines = []
    collaborateur = False
    groupes_info = {}
    
    def setclasses(self):
        if not self.groupes_info:
            self.set_groupInfo()

    def classes_cours_disciplines(self):
        if not self.cours:
            self.set_groupInfo()
        return self.classes, self.cours, self.disciplines

    def set_groupInfo(self):
        member = self.member()
        gr_info = ()
        if member.hasProperty('memberOf'):
            gr_info = member.getProperty('memberOf')
        
        classes = set()
        cours = set()
        disciplines = set()
        #import pdb; pdb.set_trace()
        if not gr_info:
            return
        for gr in gr_info:
            groupes = gr.split(',')
            if groupes[2] == 'ou=COURS':
                cours.add(groupes[0].split('=')[1])
            elif groupes[1] == 'ou=CLASSES':
                classes.add(groupes[0].split('=')[1])
            elif groupes[1] == 'ou=DISCIPLINES':
                disciplines.add(groupes[0].split('=')[1])
        self.cours = list(cours)
        self.classes = list(classes)
        self.disciplines = list(disciplines)
        self.cours.sort()
        self.classes.sort()
        self.disciplines.sort()
              
    def isCollaborateur(self):
        return self.collaborateur
        
    def member(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        return member  
        
    def groupes(self):
        #         groups_tool = getToolByName(self, 'portal_groups')
        #         gr = groups_tool.getGroupsByUserId(self.member())
        #         return gr
        mt = getToolByName(self.context, 'portal_membership')
        gr = mt.getAuthenticatedMember().getGroups()
        if 'COLLABORATEURS' in gr:
            self.collaborateur = True
        return gr
        #acl_users = getToolByName(self, 'acl_users')
        # Iterable returning id strings:
        #groups = acl_users.source_groups.getGroupIds()
        #return groups
        
#     def cours(self):
#         tool = getToolByName(self.context, 'portal_groups')
#         group = tool.getGroupById(u'cours')
#         if group is None:
#             return ()
#         return group.getGroupMembers()

groupes_info = None