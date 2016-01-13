import os
import tarfile

from github3 import login

token = os.getenv('GITHUB_TOKEN')
gh = login(token=token)
repo = gh.repository('gamechanger', 'dusty')

version = os.getenv('VERSION')
prerelease = os.getenv('PRERELEASE') == 'true'

release_name = version
release = repo.create_release(version, name=release_name, prerelease=prerelease)

for setup_file in ['com.gamechanger.dusty.plist', 'install.sh']:
    with open(os.path.join('setup', setup_file), 'r') as f:
        release.upload_asset(content_type='text/plain',
                             name=setup_file,
                             asset=f)

for binary in ['dusty']:
    with open(os.path.join('dist', binary), 'r') as f:
        release.upload_asset(content_type='application/octet-stream',
                             name=binary,
                             asset=f)

with tarfile.open('dusty.tar.gz', 'w:gz') as tarball:
    tarball.add('dist/dusty', arcname='dusty')
    tarball.add('setup/com.gamechanger.dusty.plist', arcname='com.gamechanger.dusty.plist')
    tarball.add('setup/brew-install.sh', arcname='brew-install.sh')

with open('dusty.tar.gz', 'r') as f:
    release.upload_asset(content_type='application/octet-stream',
                         name='dusty.tar.gz',
                         asset=f)
