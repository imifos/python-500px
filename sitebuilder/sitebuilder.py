from fivehundredpx.client import FiveHundredPXAPI
from fivehundredpx.auth import *
import urllib
import os
from fivehundredpx.bind  import bind_api

"""
A Python script that generates a gallery/thumbnail page from your 500px.com account.
It's based on the 500px/python-500px project, extends a bit the base library and adds a site generator.
License: MIT, Code by @imifos

500px.com API key:
https://500px.com/settings/applications
"""




_CONSUMER_KEY="TRALALALAL"
_CONSUMER_SECRET="SECRET_TRALALLAAAAA"
_USER_ID="19194355"
_BASEDIR="/Users/natasha/dev/python-500px-sitebuilder/sitebuilder"





#####################################################################
# Extends the original 500px API interface class with some additional
# things.
#
class FiveHundredPXAPIEx(FiveHundredPXAPI):

    ### Galleries API
    # https://github.com/500px/api-documentation/tree/master/endpoints/galleries
    users_galleries = bind_api(path='/users/{id}/galleries', require_auth=True, allowed_params=['id','rpp'], as_query=True)
    users_galleries_items = bind_api(path='/users/{id}/galleries/{galid}/items', require_auth=True, allowed_params=['id','galid','rpp'], as_query=True)

    ### Extend the /photos interface without breaking it
    photosEx = bind_api(path='/photos',allowed_params=['feature','sort','rpp','user_id'], require_auth=True, as_query=True)




#####################################################################
#
class SiteGenerator(object):

    #
    #
    def __init__(self,consumer_key,consumer_secret,user_id,base_directory):

        self.consumer_key=consumer_key
        self.consumer_secret=consumer_secret
        self.user_id=user_id
        self.base_directory=base_directory

        self.outputdir=None
        self.imagedir=None
        self.outputfile=None
        self.api=None
        self.unauthorized_api=None


    # Prepares the output and starts the output index.html busing the prefix.html file.
    #
    def open_output(self):

        self.outputdir=self.base_directory+"/out/"
        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)

        self.imagedir=self.base_directory+"/out/img/"
        if not os.path.exists(self.imagedir):
            os.makedirs(self.imagedir)

        outfile=self.outputdir+"index.html"
        print "Preparing output file ", outfile
        self.outputfile = open(outfile, "w")

        with open(self.base_directory+"/prefix.html") as file:
            self.outputfile.write(file.read())


    # Concludes the output index.html with the suffix.html and closes the output.
    #
    def close_output(self):

        with open(self.base_directory+"/suffix.html") as file:
            self.outputfile.write(file.read())
        self.outputfile.close()


    # Write a line into the output file
    #
    def out(self,line):
        self.outputfile.writelines(line)
        self.outputfile.writelines('\n')


    # Writes the HTML blick for a single thumbnail/photo
    #
    def out_photo_description(self,photo):
        self.out('  <div class="thumbnail">')
        self.out('    <div class="frame">')
        self.out('       <a target="_blank" href="https://500px.com'+photo['url']+'">')
        self.out('          <img class="pic" src="img/'+str(photo['id'])+'.jpg">')
        self.out('       </a>')
        self.out('    </div>')
        self.out('    <p class="title">'+str(photo['name'].encode('utf8'))+'</p>')
        self.out('  </div>')


    #
    #
    def init_api(self):

        print "Authenticating against 500px.com"

        handler = OAuthHandler(self.consumer_key,self.consumer_secret)

        headers = {}
        handler.apply_auth('https://api.500px.com/v1/oauth/request_token', 'POST', headers, { 'oauth_callback' : 'http://localhost' })

        self.api=FiveHundredPXAPIEx(auth_handler=handler)
        self.unauthorized_api=FiveHundredPXAPI()


    # Fetches the latest N photos from the public profile and returns a dictionary if 'photos'.
    #
    # Usage: for photo in <return>:
    #            print photo['url'], "/", photo['image_url']
    #
    # Note: I use the paging mechanism to specify the amout I want. By this, it's limited to 100, which is
    # the max number of elements 500px returns in one single page. If you xant to make it more complicated and add
    # multi paging, be my guest :)
    #
    def fetch_top_public_stream(self,amount):
        public_stream = self.api.photosEx(feature='user',require_auth=True,user_id=self.user_id,rpp=amount,sort='created_at')
        return public_stream['photos']


    # Fetches the list of photo galleries.
    #
    # Usage: # for gallery in <return>:
    #               print gallery['id'], "/", gallery['name']
    #
    # To correctly handle unicode: name=str(gallery['name'].encode('utf8'))
    #
    def fetch_galleries(self):
        galleries = self.api.users_galleries(require_auth=True,id=self.user_id,rpp='100')
        return galleries['galleries']


    # Fetches the list of photos in a given gallery.
    #
    # Usage: for photo in <return>:
    #           print photo['url'] photo['description'] photo['name'] photo['image_url'] photo['id']
    #
    def fetch_gallery(self,id):
        detail=self.api.users_galleries_items(require_auth=True,id=self.user_id,galid=id,rpp='100')
        return detail['photos']


    # Downloads all photo thumbnails of the passed gallerie into the 'img/' folder. Name: <id>.jpg
    #
    def fetch_gallery_thumbnails(self, photos):

        for photo in photos:

            filename=self.imagedir+str(photo['id'])+'.jpg'
            if os.path.isfile(filename):
                print "     Thumbnail already downloaded "+str(photo['id'])+" / "+photo['name']
            else:
                print "     Download thumbnail "+str(photo['id'])+" / "+photo['name']
                f=open(filename,'wb')
                f.write(urllib.urlopen(photo['image_url']).read())
                f.close()


    # Builds the web site in the 'out/' directory
    #
    def build(self):

        print "500px Site Builder started..."
        print ""

        self.init_api()
        self.open_output()

        self.out("<h1>Welcome to my 500px.com index page</h1>")

        ###

        print "Fetching public stream..."

        stream = self.fetch_top_public_stream(10)

        self.out('<div id="gallerySTREAM" class="gallery">')
        self.out('  <h2>Public Stream (Latest 10)</h2>')

        self.fetch_gallery_thumbnails(stream)
        for photo in stream:
            self.out_photo_description(photo)

        self.out('\n</div> <!--gallery-->\n\n\n')

        ###

        print "Fetching galleries..."

        galleries = self.fetch_galleries()

        for gallery in galleries:

            print "  ", gallery['id'], "/", gallery['name']

            self.out('<div id="gallery'+str(gallery['id'])+'" class="gallery">')

            gname=str(gallery['name'].encode('utf8'))
            self.out('  <h2>'+gname+'</h2>')

            photos=self.fetch_gallery(gallery['id'])
            self.fetch_gallery_thumbnails(photos)
            for photo in photos:
                self.out_photo_description(photo)

            self.out('\n</div> <!--gallery-->\n\n\n')

        ###

        self.close_output()

        print ""
        print "Operation completed"




#####################################################################
#
if __name__ == '__main__':

    sb=SiteGenerator(_CONSUMER_KEY,_CONSUMER_SECRET,_USER_ID,_BASEDIR)
    sb.build()
