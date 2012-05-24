import logging
from datetime import datetime
import time
from email import utils

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form

from ptahto import models
from ptahto import permissions

# logger, check Debug Toolbar logging section or stdout
log = logging.getLogger(__name__)


class TemplateAPI(object):

    def __init__(self, request):
        self.blog = models.blog_factory({})
        self.posts = ptah.get_session().query(models.Post).all()
        self.now = self.to_rfc822(datetime.utcnow())

    def to_rfc822(self, date):
        datetuple = date.timetuple()
        timestamp = time.mktime(datetuple)
        return utils.formatdate(timestamp)

    def recent_posts(self):
        return self.posts[:10]


@view_config(renderer='ptahto:templates/blog.pt',
             context=models.Blog,
             wrapper=ptah.wrap_layout(),
             permission=permissions.View,
             route_name='blog')
def home_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/rss.pt',
             context=models.Blog,
             permission=permissions.View,
             route_name='rss')
def rss_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/atom.pt',
             context=models.Blog,
             permission=permissions.View,
             route_name='atom')
def atom_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/blog.pt',
             context=models.Blog,
             wrapper=ptah.wrap_layout(),
             permission=permissions.View,
             route_name='about')
def about_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/blog.pt',
             context=models.Blog,
             wrapper=ptah.wrap_layout(),
             permission=permissions.ModifyContent,
             route_name='dashboard')
def dashboard_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/blog.pt',
             context=models.Blog,
             wrapper=ptah.wrap_layout(),
             permission=permissions.View,
             route_name='archive')
def archive_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/edit.pt',
             context=models.Blog,
             wrapper=ptah.wrap_layout(),
             permission=permissions.ModifyContent,
             route_name='config')
def edit_blog(context, request):
    configform = form.Form(context,request)
    configform.fields = models.Blog.__type__.fieldset

    def backAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return
        form.context.name = data['name']
        form.context.title = data['title']
        form.context.tagline = data['tagline']
        form.context.discussion = data['discussion']
        form.context.disqus = data['disqus']
        form.message('Blog has been updated.')

    configform.label = u'Blog Configuration'
    configform.buttons.add_action('Update', action=updateAction)
    configform.buttons.add_action('Back', action=backAction)
    configform.content = {'name':context.name,
                        'title':context.title,
                        'tagline':context.tagline,
                        'discussion':context.discussion,
                        'disqus':context.disqus}

    result = configform.update()
    if isinstance(result, HTTPFound):
        return result

    rendered_form = configform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    api = TemplateAPI(request)

    return {'api': api,
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}


@view_config(renderer='ptahto:templates/post.pt',
             context=models.Post,
             wrapper=ptah.wrap_layout(),
             permission=permissions.View,
             route_name='view-post')
def post_view(context, request):
    api = TemplateAPI(request)
    return {'api': api}


@view_config(renderer='ptahto:templates/edit.pt',
             wrapper=ptah.wrap_layout(),
             permission=permissions.AddContent,
             route_name='add-post')
def add_post(context, request):
    postform = form.Form(context,request)
    postform.fields = models.Post.__type__.fieldset

    def cancelAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return

        now = datetime.utcnow()
        user = ptah.auth_service.get_current_principal().name
        post = models.Post(creator = user,
                           title = data['title'],
                           tags = data['tags'],
                           category = data['category'],
                           text = data['text'],
                           discussion = data['discussion'],
                           modified = now,
                           created = now)
        ptah.get_session().add(post)

        form.message('Post has been created.')
        return HTTPFound(location='/')

    postform.label = u'Add post'
    postform.buttons.add_action('Add', action=updateAction)
    postform.buttons.add_action('Cancel', action=cancelAction)

    result = postform.update() # prepare form for rendering
    if isinstance(result, HTTPFound):
        return result

    rendered_form = postform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    api = TemplateAPI(request)

    return {'api': api,
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}


@view_config(renderer='ptahto:templates/edit.pt',
             context=models.Post,
             wrapper=ptah.wrap_layout(),
             permission=permissions.ModifyContent,
             route_name='edit-post')
def edit_post(context, request):
    postform = form.Form(context,request)
    postform.fields = models.Post.__type__.fieldset

    def backAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return
        user = ptah.auth_service.get_current_principal().name
        form.context.creator = user
        form.context.title = data['title']
        form.context.tags = data['tags']
        form.context.category = data['category']
        form.context.text = data['text']
        form.context.discussion = data['discussion']
        form.context.modified = datetime.utcnow()
        form.message('Post has been updated.')

    postform.label = u'Edit Post'
    postform.buttons.add_action('Update', action=updateAction)
    postform.buttons.add_action('Back', action=backAction)
    postform.content = {'title':context.title,
                        'tags':context.tags,
                        'category':context.category,
                        'text':context.text,
                        'discussion':context.discussion}

    result = postform.update()
    if isinstance(result, HTTPFound):
        return result

    rendered_form = postform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    api = TemplateAPI(request)

    return {'api': api,
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}


@view_config(renderer='ptahto:templates/edit.pt',
             context=models.Category,
             wrapper=ptah.wrap_layout(),
             permission=permissions.ModifyContent,
             route_name='edit-category')
def edit_category(context, request):
    categoryform = form.Form(context,request)
    categoryform.fields = models.Category.__type__.fieldset

    def backAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return
        form.context.name = data['name']
        form.message('Category has been updated.')

    categoryform.label = u'Edit category'
    categoryform.buttons.add_action('Update', action=updateAction)
    categoryform.buttons.add_action('Back', action=backAction)
    categoryform.content = {'name':context.name}

    result = categoryform.update()
    if isinstance(result, HTTPFound):
        return result

    rendered_form = categoryform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    api = TemplateAPI(request)

    return {'api': api,
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}


@view_config(renderer='ptahto:templates/edit.pt',
             wrapper=ptah.wrap_layout(),
             permission=permissions.AddContent,
             route_name='add-category')
def add_category(context, request):
    categoryform = form.Form(context,request)
    categoryform.fields = models.Category.__type__.fieldset

    def cancelAction(form):
        return HTTPFound(location='/')

    def updateAction(form):
        data, errors = form.extract()
        if errors:
            form.message(errors, 'form-error')
            return

        category = models.Category(name = data['name'])
        ptah.get_session().add(category)

        form.message('Category has been created.')
        return HTTPFound(location='/')

    categoryform.label = u'Add category'
    categoryform.buttons.add_action('Add', action=updateAction)
    categoryform.buttons.add_action('Cancel', action=cancelAction)

    result = categoryform.update() # prepare form for rendering
    if isinstance(result, HTTPFound):
        return result

    rendered_form = categoryform.render()

    ptah.include(request, 'bootstrap')
    rendered_includes = ptah.render_includes(request)

    api = TemplateAPI(request)

    return {'api': api,
            'rendered_form': rendered_form,
            'rendered_includes': rendered_includes,
            'rendered_messages': ptah.render_messages(request)}


