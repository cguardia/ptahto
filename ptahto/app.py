import ptah
import ptahcrowd

from pyramid.config import Configurator
from pyramid.asset import abspath_from_asset_spec
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from ptahto import models
from ptahto.permissions import Manager

auth_policy = AuthTktAuthenticationPolicy('secret_ptahto')
session_factory = UnencryptedCookieSessionFactoryConfig('secret_ptahto')

POPULATE_CONTENT = 'pthato-content'

@ptah.populate(POPULATE_CONTENT,
               title='Create ptahto_content',
               requires=(ptah.POPULATE_DB_SCHEMA,))
def bootstrap_data(registry):
    """ create initial content """
    if not ptah.get_session().query(models.Blog).all():
        blog = models.Blog(name='ptahto',
                           title='A blog',
                           tagline='Ptah stuff',
                           discussion=True,
                           disqus='')
        ptah.get_session().add(blog)

    if not ptah.get_session().query(models.Category)\
           .filter(models.Category.name == 'general').all():
        category = models.Category(name='general')
        ptah.get_session().add(category)



def main(global_config, **settings):

    config = Configurator(settings=settings,
                          root_factory = models.blog_factory,
                          session_factory = session_factory,
                          authentication_policy = auth_policy)

    config.add_static_view('ptahto', 'ptahto:static')

    config.add_route('blog', '/')
    config.add_route('config', '/config.html')
    config.add_route('dashboard', '/dashboard.html')
    config.add_route('about', '/about.html')
    config.add_route('rss', '/rss')
    config.add_route('atom', '/atom')
    config.add_route('archive', '/posts')
    config.add_route('add-post', '/posts/add.html')
    config.add_route('view-post', '/posts/{id}',
                     factory=models.post_factory, use_global_views=True)
    config.add_route('edit-post', '/posts/{id}/edit.html',
                     factory=models.post_factory, use_global_views=True)
    config.add_route('categories', '/categories')
    config.add_route('add-category', '/categories/add.html')
    config.add_route('view-category', '/categories/{id}',
                     factory=models.category_factory, use_global_views=True)
    config.add_route('edit-category', '/categories/{id}/edit.html',
                     factory=models.category_factory, use_global_views=True)
    config.add_route('rss-category', '/categories/{id}/rss',
                     factory=models.category_factory, use_global_views=True)
    config.add_route('atom-category', '/categories/{id}/atom',
                     factory=models.category_factory, use_global_views=True)

    config.include('ptah')
    config.scan()

    config.ptah_init_settings()
    config.ptah_init_sql()
    
    config.ptah_init_manage(
        managers = ['*'],
        disable_modules = ['rest', 'introspect', 'apps', 'permissions', 'settings'])

    config.commit()

    import transaction
    transaction.commit()

    return config.make_wsgi_app()
