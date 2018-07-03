# -*- coding: utf-8 -*-

from intelmq.lib import utils
from intelmq.lib.bot import Bot


class BotscoutParserBot(Bot):

    def process(self):
        report = self.receive_message()
        raw_report = utils.base64_decode(report["raw"])

        feed_list = raw_report.split('\n')
        for feed in feed_list:
            if ',' not in feed:
                continue

            data = feed.split(',')
            event = self.new_event(report)

            event.add('source.ip', data[2], raise_failure=False)
            event.add('source.account', data[1])
            event.add('classification.type', 'spam')
            event.add('raw', feed)
            self.send_message(event)

        self.acknowledge_message()


BOT = BotscoutParserBot
