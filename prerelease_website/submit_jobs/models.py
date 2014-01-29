import yaml
import urllib2
import logging
from rosdistro import get_index, get_index_url, get_distribution_cache
from rosdistro.manifest_provider import get_release_tag
import rospkg.distro
#from django.db import models

logger = logging.getLogger('submit_jobs')


class DryRosDistro(object):
    def __init__(self, distro):
        self.distro = distro
        if distro == 'groovy':
            self.distro_obj = rospkg.distro.load_distro(rospkg.distro.distro_uri(distro))
        else:
            self.distro_obj = None

    def get_info(self):
        res = {}
        if not self.distro_obj:
            return res
        for name, s in self.distro_obj.stacks.iteritems():
            if s.vcs_config.type == 'svn':
                url = s.vcs_config.anon_dev
                branch = ""
            else:
                url = s.vcs_config.repo_uri
                branch = s.vcs_config.dev_branch
            res[name] = {'distro': self.distro + "_dry",
                         'version': ["devel"],
                         'url': [url],
                         'branch': [branch]}
        return res


#We're essentially using GitHub as a backend since the distro files are hosted there
class WetRosDistro(object):
    def __init__(self, distro):
        self.distro = distro

        try:
            index = get_index(get_index_url())
            self._distribution_file = get_distribution_cache(index, distro).distribution_file
        except:
            logger.error("Could not load rosdistro distribution cache")
            self._distribution_file = None

    def get_info(self):
        res = {}
        if not self._distribution_file:
            return res
        for name in self._distribution_file.repositories.keys():
            repo = self._distribution_file.repositories[name]
            if repo.release_repository or repo.source_repository:
                res[name] = {'distro': self.distro + "_wet", 'version': [], 'url': [], 'branch': []}

        # first add devel
        for name in self._distribution_file.repositories.keys():
            r = self._distribution_file.repositories[name].source_repository
            if not r:
                continue
            if not r.version:
                res[name]['branch'].append("")
            else:
                res[name]['branch'].append(r.version)
            res[name]['version'].append('devel')
            res[name]['url'].append(r.url)

        # then add release
        for name in self._distribution_file.repositories.keys():
            r = self._distribution_file.repositories[name].release_repository
            if not r:
                continue
            if 'release' not in r.tags:
                continue
            release_tag = get_release_tag(r, '{package}')
            if r.version is not None:
                release_tag_without_version = release_tag.replace('/%s' % r.version, '').replace('/%s' % r.version.split('-')[0], '')
            else:
                release_tag_without_version = release_tag.replace('/{version}', '').replace('/{upstream_version}', '')
            res[name]['version'].append('latest')
            res[name]['url'].append(r.url)
            res[name]['branch'].append(release_tag_without_version)

            if r.version:
                res[name]['version'].append(r.version.split('-')[0])
                res[name]['url'].append(r.url)
                res[name]['branch'].append(release_tag)
                #res[name]['branch'].append("release/pkg_name/" + r.version.split('-')[0])
        return res

    def get_repos(self):
        if self._distribution_file is None:
            return []
        return [repo_name for repo_name in self._distribution_file.repositories.keys() if self._distribution_file.repositories[repo_name].release_repository is not None or self._distribution_file.repositories[repo_name].source_repository is not None]

    def is_released(self, repo_name):
        if self._distribution_file is None:
            return False
        return repo_name in self._distribution_file.repositories and self._distribution_file.repositories[repo_name].release_repository is not None

    def get_release_info(self, repo_name):
        if self._distribution_file is None:
            return None
        return self._distribution_file.repositories[repo_name].release_repository

    def is_devel(self, repo_name):
        if self._distribution_file is None:
            return False
        return repo_name in self._distribution_file.repositories and self._distribution_file.repositories[repo_name].source_repository is not None

    def get_devel_info(self, repo_name):
        if self._distribution_file is None:
            return None
        return self._distribution_file.repositories[repo_name].source_repository

    def get_repo_version(self, repo_name):
        if repo_name not in self._distribution_file.repositories:
            logger.error("Repo %s not in distro file for %s" % (repo_name, self.distro))
            return None

        #Since debian information is tacked onto the version #, we split
        return self._distribution_file.repositories[repo_name].release_repository.version.split('-')[0]
