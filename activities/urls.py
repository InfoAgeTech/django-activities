from __future__ import unicode_literals

from django.conf.urls import patterns
from django.conf.urls import url
from django.core.exceptions import ImproperlyConfigured

from .views import ActivitiesGenericObjectView
from .views import ActivitiesView
from .views import ActivityDeleteView
from .views import ActivityEditView
from .views import ActivityRepliesView
from .views import ActivityReplyDeleteView
from .views import ActivityReplyEditView
from .views import ActivityReplyView
from .views import ActivityView


# need to map these in order for the dynamic urls to work correctly
urlpattern_mapping = (
    {'regex': r'^/?$', 'view': ActivitiesView, 'name': 'activities_view'},
    {'regex': r'^/(?P<activity_id>\d+)/delete/?$', 'view': ActivityDeleteView, 'name': 'activity_delete'},
    {'regex': r'^/(?P<activity_id>\d+)/edit/?$', 'view': ActivityEditView, 'name': 'activity_edit'},
    {'regex': r'^/(?P<activity_id>\d+)/replies/(?P<reply_id>\d+)/delete/?$', 'view': ActivityReplyDeleteView, 'name': 'activity_reply_delete'},
    {'regex': r'^/(?P<activity_id>\d+)/replies/(?P<reply_id>\d+)/edit/?$', 'view': ActivityReplyEditView, 'name': 'activity_reply_edit'},
    {'regex': r'^/(?P<activity_id>\d+)/replies/(?P<reply_id>\d+)/?$', 'view': ActivityReplyView, 'name': 'activity_reply'},
    {'regex': r'^/(?P<activity_id>\d+)/replies/?$', 'view': ActivityRepliesView, 'name': 'activity_replies'},
    {'regex': r'^/(?P<activity_id>\d+)/?$', 'view': ActivityView, 'name': 'activity_view'},
)


urlpatterns = patterns('',
    url(r'^/(?P<content_type_id>\d+)/(?P<object_id>\d+)/?$', ActivitiesGenericObjectView.as_view(), name='activities_view'),
    *[url(pattern['regex'], pattern['view'].as_view(), name=pattern['name'])
      for pattern in urlpattern_mapping if pattern['name'] != 'activities_view']
)


def get_urls(extend_urlpatterns, root_urlpattern_name, class_prefix,
             bases_classes=None):
    """Function that dynamically creates activities urls so urls don't have to
    use generic content type ids in the urls.

    :param extend_urlpatterns: the urls patterns to extend
    :param root_urlpattern_name: this is the url pattern to extend the activity
        urls from.
    :param class_prefix: this is the string class prefix to use for the
        generated views.  This will also be the prefix used for the url naming
        conventions.
    :param bases: the iterable of base classes to extend.
    :param url_prefix: the prefix to use for the urls.  Default is "activities"
        so the urls would be generated as follows:

        ./activities/(?P<activity_id>\d+)/delete/?S
        ./activities/(?P<activity_id>\d+)/edit/?S

    A call to the following:

    > get_urls(my_url_patterns,
    .          class_prefix='Foo',
    .          base_classes=(LoginRequiredViewMixin,))

    This generates a view class that resembles something along the lines of:

    class FooActivityView(LoginRequiredViewMixin, ActivityView):
        class_prefix = 'Foo'

    """
    root_urlpattern = None

    for pattern in extend_urlpatterns:
        if pattern.name == root_urlpattern_name:
            root_urlpattern = pattern.regex.pattern
            break

    if root_urlpattern is None:
        raise ImproperlyConfigured('No url pattern found with the name: '
                                   '{0}'.format(root_urlpattern_name))

    # root url pattern can't end in any of these characters
    for char in ('$', '?', '/'):
        if root_urlpattern.endswith(char):
            root_urlpattern = root_urlpattern[:-1]

    for pattern in urlpattern_mapping:
        # generate the dynamic view
        pattern_view = pattern.get('view')
        pattern_name = pattern.get('name')
        pattern_regex = pattern.get('regex').replace('^/', '')

        class_name = '{0}{1}'.format(class_prefix, pattern_view.__name__)
        ExtendedActivityView = type(class_name,
                                    bases_classes + (pattern_view,),
                                    {'class_prefix': class_prefix})

        # generate the new pattern name
        pattern_name = '{0}_{1}'.format(class_prefix.lower(), pattern_name)
        url_pattern = r'{0}/activities/{1}'.format(root_urlpattern,
                                                   pattern_regex)

        # add the pattern to urls
        extend_urlpatterns += patterns('',
            url(url_pattern, ExtendedActivityView.as_view(), name=pattern_name),
        )
