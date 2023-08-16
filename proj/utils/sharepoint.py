from shareplum import Site
from shareplum import Office365
from shareplum.site import Version

def upload_images(username, password, url, sitefolder, teamname, )
    authcookie = Office365(url, username=username, password=password).GetCookies()
    site = Site(os.path.join(url, 'sites', teamname), version=Version.v2016, authcookie=authcookie)

    folder = site.Folder(sitefolder)