from datetime import datetime, timedelta

import pytz
import dateutil.parser

class TimeStampedMixin:

    def assertDictEqualWithTimestamp(self, dict1, dict2, timestamp_key='@timestamp'):
        """If any of the dictionaries has a timestamp key, pop it, and assert
        that it is within a window of 5 secs"""
        timestamps = [x.pop(timestamp_key) for x in [dict1, dict2]
                      if timestamp_key in x]
        for timestamp in timestamps:
            timeval = dateutil.parser.parse(timestamp)
            self.assertTrue(datetime.utcnow().replace(tzinfo=pytz.utc) - timeval < timedelta(seconds=5),
                            "Timestamp {} is older than 5 seconds".format(timestamp))
        self.assertDictEqual(dict1, dict2)
