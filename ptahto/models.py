from datetime import datetime

import ptah
import sqlalchemy as sqla
from pyramid.httpexceptions import HTTPNotFound


@ptah.type('blog', 'Blog')
class Blog(ptah.get_base()):
    """ A blog. """

    __tablename__ = 'ptah_models_blogs'

    __id__ = sqla.Column('id', sqla.Integer,
                         primary_key=True)

    name = sqla.Column(sqla.Unicode)
    title = sqla.Column(sqla.Unicode)
    tagline = sqla.Column(sqla.Unicode)
    discussion = sqla.Column(sqla.Boolean, default=False)
    disqus = sqla.Column(sqla.Unicode, info={'missing':''})

    __acl__ = ptah.DEFAULT_ACL


@ptah.type('category', 'Category')
class Category(ptah.get_base()):
    """ A blog category. """

    __tablename__ = 'ptah_models_categories'

    __id__ = sqla.Column('id', sqla.Integer,
                         primary_key=True)

    name = sqla.Column(sqla.Unicode)

    __acl__ = ptah.DEFAULT_ACL


@ptah.type('post', 'Post')
class Post(ptah.get_base()):
    """ A blog post. """

    __tablename__ = 'ptah_models_posts'

    __id__ = sqla.Column('id', sqla.Integer,
                         primary_key=True)

    creator = sqla.Column(sqla.Unicode)
    title = sqla.Column(sqla.Unicode)
    tags = sqla.Column(sqla.Unicode)
    category = sqla.Column(sqla.Integer, sqla.ForeignKey('ptah_models_categories.id'))
    text = sqla.Column(sqla.Unicode, info = {'field_type': 'ckeditor'})
    created = sqla.Column(sqla.DateTime, info = {'missing': None})
    modified = sqla.Column(sqla.DateTime, info = {'missing': None})
    discussion = sqla.Column(sqla.Boolean, default=False)

    __acl__ = ptah.DEFAULT_ACL


def blog_factory(request):
    return ptah.get_session().query(Blog).first()


def post_factory(request):
    id_ = request.matchdict.get('id')
    if id_:
        return ptah.get_session().query(Post) \
               .filter(Post.__id__ == id_).first()

    return HTTPNotFound(location='.')


def category_factory(request):
    id_ = request.matchdict.get('id')
    if id_:
        return ptah.get_session().query(Category) \
               .filter(Category.__id__ == id_).first()

    return HTTPNotFound(location='.')

