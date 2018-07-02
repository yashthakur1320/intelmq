# -*- coding: utf-8 -*-

from intelmq.lib import utils
from intelmq.lib.bot import Bot


class CediaParserBot(Bot):

    def process(self):
        report = self.receive_message()
        raw_report = utils.base64_decode(report["raw"])

        feed_list = raw_report.split('\n')
        for feed in feed_list[:-1]:
            event = self.new_event(report)

            event.add('source.fqdn', feed)
            event.add('classification.type', 'malware')
            event.add('raw', feed)
            self.send_message(event)

        self.acknowledge_message()


BOT = CediaParserBot
