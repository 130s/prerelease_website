from django.conf.urls import patterns, url

urlpatterns = patterns(
    'prerelease_website.rosinstall_gen.views',
    url(r'^$', 'landing_page'),
    url(r'^generate/dry/raw/(?P<distro>.*)/(?P<packages>.*)$', 'dry_raw'),
    url(r'^generate/dry/(?P<distro>.*)/(?P<packages>.*)$', 'dry_index'),
    url(r'^generate/combined/raw/(?P<distro>.*)/(?P<packages>.*)$', 'combined_raw'),
    url(r'^generate/combined/(?P<distro>.*)/(?P<packages>.*)$', 'combined_index'),
    url(r'^generate/raw/(?P<distro>.*)/(?P<packages>.*)$', 'raw'),
    url(r'^generate/(?P<distro>.*)/(?P<packages>.*)$', 'index')
)
