from requests import post
from json import loads
from datetime import datetime


class PublishedFile:
    def __init__(self, publishedfiledisct):
        self.result = int(publishedfiledisct['result'])
        self.publishedfileid = int(publishedfiledisct['publishedfileid'])
        if self.result == 1:
            self.ban_reason = publishedfiledisct['ban_reason']
            self.banned = int(publishedfiledisct['banned'])
            self.consumer_app_id = int(publishedfiledisct['consumer_app_id'])
            self.creator = int(publishedfiledisct['creator'])
            self.creator_app_id = int(publishedfiledisct['creator_app_id'])
            self.description = publishedfiledisct['description']
            self.favorited = int(publishedfiledisct['favorited'])
            self.file_size = int(publishedfiledisct['file_size'])
            self.file_url = publishedfiledisct['file_url']
            self.filename = publishedfiledisct['filename']
            self.hcontent_file = publishedfiledisct['hcontent_file']
            self.hcontent_preview = publishedfiledisct['hcontent_preview']
            self.lifetime_favorited = int(publishedfiledisct['lifetime_favorited'])
            self.lifetime_subscriptions = int(publishedfiledisct['lifetime_subscriptions'])
            self.preview_url = publishedfiledisct['preview_url']
            self.subscriptions = int(publishedfiledisct['subscriptions'])
            self.tags = publishedfiledisct['tags']
            self.time_created = datetime.fromtimestamp(publishedfiledisct['time_created'])
            self.time_updated = datetime.fromtimestamp(publishedfiledisct['time_updated'])
            self.title = publishedfiledisct['title']
            self.views = int(publishedfiledisct['views'])
            self.visibility = int(publishedfiledisct['visibility'])


class PublishedFileDetails:
    @staticmethod
    def get_details(publishedfileids):
        publishedfiledetails = []
        request_data = {
            'itemcount': len(publishedfileids)
        }

        for id, i in zip(publishedfileids, range(len(publishedfileids))):
            request_data[f"publishedfileids[{i}]"] = id

        response = post("https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/",
                        data=request_data)
        if response.status_code == 200:
            response_json = response.json()
            for details in response_json['response']['publishedfiledetails']:
                publishedfiledetails.append(PublishedFile(details))

        return publishedfiledetails
