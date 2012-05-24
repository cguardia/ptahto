import ptah

from ptahto.models import Blog, Category, Post
from ptahto.views import TemplateAPI


ptah.layout.register(
    'ptah-page', parent='workspace', use_global_views=True,
    renderer='ptahto:templates/layout-ptahpage.pt')


@ptah.layout(
    'page', use_global_views=True,
    renderer='ptahto:templates/layout-page.pt')
class PageLayout(ptah.View):
    """ Page layout """

    def update(self):
        self.api = TemplateAPI(self.request)


@ptah.layout(
    'workspace', parent='page', use_global_views=True,
    renderer='ptahto:templates/layout-workspace.pt')
class WorkspaceLayout(ptah.View):

    def update(self):
        self.user = ptah.auth_service.get_current_principal()
        self.ptahManager = ptah.manage.check_access(
            ptah.auth_service.get_userid(), self.request)
        self.isAnon = self.user is None
        self.api = TemplateAPI(self.request)


@ptah.layout(
    '', parent="workspace", use_global_views=True,
    renderer="ptahto:templates/layout-content.pt")
class ContentLayout(ptah.View):
    """ Content layout """

    def update(self):
        self.api = TemplateAPI(self.request)

